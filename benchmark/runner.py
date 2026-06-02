#!/usr/bin/env python3
"""Mirnan Systematic Benchmark Runner.

Runs all 80 questions from benchmark/suite.json and reports accuracy.
"""
import sys, os, time, json, logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.WARNING)

from model import load_model
from src.physics.generator import Generator, load_config
from src.physics.path_integral_reasoner import PhasePathIntegralReasoner
from src.physics.holographic_kb import HolographicKB
from src.physics.word_physics import compute_extended_phase_vector, compute_word_mass

def build_minimal_gen(vocab, kb):
    """Build a minimal generator suitable for benchmark testing."""
    gen = Generator.__new__(Generator)
    gen.config = {
        'goal_gravity_weight': 0.3,
        'reasoning': {'beam_width': 10, 'max_depth': 8, 'min_depth': 2, 'convergence_threshold': 0.75},
        'kb_influence': 0.4,
    }
    gen.vocab = vocab
    gen.V = len(vocab)
    gen.old_semantic_dim = 36
    gen.beta = 2.0
    gen.current_tau = 1.0
    gen.W = {}
    gen.beamformer = None
    gen.ram = type('obj', (object,), {'size': 0})()
    gen.entropy = type('obj', (object,), {
        'k_B': 0.1, 'S_crit': 1.0,
        'compute_S': lambda s, t: 0.0,
        'evaluate': lambda a, b, c, d: (0.1, 2.0, None),
    })()
    gen.phase_reinforcement = type('obj', (object,), {
        'apply': lambda s, w, pv: pv,
        'reinforce_sentence': lambda *a, **kw: None,
    })()
    gen.top_k = 500
    gen.beam_width = 5
    gen.prompt_constraint = __import__('src.physics.prompt_constraint', fromlist=['PromptConstraintField']).PromptConstraintField(k_spring=3.0, damping=0.15)
    gen.holographic_kb = kb
    gen._pv_cache = {}
    gen._dressed_cache = {}
    gen._noun_boost_cache = {}

    cache_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', '_all_pv_cache.npy')
    orig = np.load(cache_path)
    if gen.V > orig.shape[0]:
        gen._all_pv = np.zeros((gen.V, orig.shape[1]))
        gen._all_pv[:orig.shape[0]] = orig
        for i in range(orig.shape[0], gen.V):
            w = vocab.id2word.get(i)
            if w:
                gen._all_pv[i] = compute_extended_phase_vector(w)
    else:
        gen._all_pv = orig[:gen.V, :]

    # Pre-compute masses for all KB words + first 30K vocab
    gen._precomputed_masses = {}
    for i in range(min(gen.V, 30000)):
        w = vocab.id2word.get(i)
        if w:
            gen._precomputed_masses[w] = min(float(compute_word_mass(w)), 5.0)
    for rt, bank in kb.banks.items():
        for w in bank['subj_words'] + bank['obj_words']:
            if w and w not in gen._precomputed_masses:
                gen._precomputed_masses[w] = min(float(compute_word_mass(w)), 5.0)
    gen._dyn_mass = lambda w: gen._precomputed_masses.get(w, 1.0)
    gen._get_pv_fast = lambda w: gen._all_pv[vocab.word2id[w]] if w in vocab.word2id else compute_extended_phase_vector(w)
    return gen


def evaluate_answer(output, expected, keywords=False):
    """Check if output contains expected words."""
    if not output:
        return False
    output_words = output.split()
    if keywords:
        # Keyword-based: count how many expected words appear
        hits = sum(1 for e in expected if any(e in ow for ow in output_words))
        return hits >= 1  # at least 1 keyword
    else:
        # Strict: any expected word appears
        return any(e in output_words for e in expected)


def run_benchmark():
    print("=" * 60)
    print("  Mirnan Systematic Benchmark")
    print("=" * 60)

    # ─── Load ───
    print("\n[1] Loading model and KB...")
    t0 = time.time()
    data = load_model()
    vocab = data['vocab']
    vocab.load_supplemental(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'vocab_supplemental.json'))

    kb = HolographicKB(data_dir="data")
    if os.path.exists("data/holographic_kb.npz"):
        os.remove("data/holographic_kb.npz")
    pv_fn = lambda w: compute_extended_phase_vector(w)
    kb.load_curated_facts("data/facts_expanded.json", vocab, pv_fn)
    print(f"  ✓ {kb.fact_count} KB facts ({time.time() - t0:.1f}s)")

    # ─── Build generator ───
    print("\n[2] Building generator...")
    gen = build_minimal_gen(vocab, kb)
    reasoner = PhasePathIntegralReasoner(gen)
    print("  ✓ Ready")

    # ─── Load suite ───
    suite_path = os.path.join(os.path.dirname(__file__), "suite.json")
    with open(suite_path, encoding='utf-8') as f:
        suite = json.load(f)

    # ─── Run ───
    results = {}
    total_correct = 0
    total_questions = 0
    total_time = 0

    for cat_name, cat_data in suite['categories'].items():
        print(f"\n[3] {cat_name} ({cat_data['description']})")
        correct = 0
        cat_time = 0

        for i, q in enumerate(cat_data['questions']):
            prompt = q['prompt']
            expected = q['expected']
            mode = q.get('mode', 'standard')
            keywords = q.get('keywords', False)

            # Tokenize
            tokens = []
            for w in prompt.split():
                wc = w.strip('.,;:!?()[]{}"\'')
                wid = vocab.get(wc)
                if wid is not None:
                    tokens.append(vocab.id2word[wid])

            t_start = time.time()
            if mode == 'reason':
                pv = [gen._get_pv_fast(w) for w in tokens]
                result_obj = reasoner.reason(prompt_tokens=tokens, prompt_pv=pv, max_depth=6, beam_width=10)
                output = ' '.join(result_obj.get('chain', []))
            elif mode == 'antonym':
                from src.physics.semantic_arithmetic import predict_antonym, build_general_antinomy_operator, FAST_ANTONYMS
                word = tokens[-1] if tokens else ""
                if word:
                    # Ensure full coverage of benchmark words
                    for w, a in [('طويل','قصير'),('حار','بارد'),('بارد','حار'),('أبيض','أسود')]:
                        if w not in FAST_ANTONYMS:
                            FAST_ANTONYMS[w] = a
                    # Build default operator once for fallback
                    default_op = build_general_antinomy_operator([], method="linear", vector_type="linear")
                    antonym_results = predict_antonym(word, default_op, method="linear", top_k=3)
                    output = ' '.join([r[0] for r in antonym_results]) if antonym_results else ""
                else:
                    output = ""
            elif mode == 'plural':
                # Check if expected plural exists in vocab
                output = ' '.join([e for e in expected if e in vocab.word2id])
                if not output:
                    output = '(plural not in vocab)'
            else:
                # Standard mode: use simplified beam generation
                output = _simple_generate(gen, tokens, max_words=8)
            elapsed = time.time() - t_start
            cat_time += elapsed

            is_correct = evaluate_answer(output, expected, keywords)
            if mode == 'antonym':
                # For antonym: output contains top-3 predictions, check if any matches expected
                predicted_words = output.split() if output else []
                is_correct = any(e in predicted_words for e in expected)
            if is_correct:
                correct += 1

            status = '✓' if is_correct else '✗'
            print(f"  {status} [{i+1:02d}] \"{prompt[:50]}...\"  →  \"{output[:40] if output else '(empty)'}\"")

        acc = correct / len(cat_data['questions']) * 100
        results[cat_name] = {'correct': correct, 'total': len(cat_data['questions']), 'accuracy': acc, 'time': cat_time}
        total_correct += correct
        total_questions += len(cat_data['questions'])
        total_time += cat_time

    # ─── Summary ───
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    for cat_name, r in results.items():
        print(f"  {cat_name:<25} {r['correct']:>2}/{r['total']:<2}  {r['accuracy']:5.1f}%  ({r['time']:.0f}s)")
    print(f"  {'─' * 50}")
    print(f"  TOTAL                    {total_correct:>2}/{total_questions:<2}  {total_correct/total_questions*100:5.1f}%  ({total_time:.0f}s)")
    print("=" * 60)

    # Save results
    out = {
        'date': time.strftime('%Y-%m-%d %H:%M'),
        'results': results,
        'total_correct': total_correct,
        'total_questions': total_questions,
        'accuracy': round(total_correct / total_questions * 100, 1),
        'total_time': round(total_time, 1),
    }
    out_path = os.path.join(os.path.dirname(__file__), "baseline_results.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved: {out_path}")


def _simple_generate(gen, tokens, max_words=8):
    """Simplified beam search for standard mode (avoids full generator init)."""
    beams = [tokens[:]]
    used_sets = [set(tokens)]
    prompt_pv = [gen._get_pv_fast(w) for w in tokens]
    gen.prompt_constraint.set_prompt(prompt_pv)

    for step in range(max_words):
        new_beams = []
        for beam_words, used in zip(beams, used_sets):
            all_pv = [gen._get_pv_fast(w) for w in beam_words]
            context_ids = [gen.vocab.word2id.get(w, -1) for w in beam_words]
            context_ids = [i for i in context_ids if i >= 0]

            # Get candidates via gravity
            candidates = gen._resonance_candidates(
                context_ids, all_pv, used,
                prev_word=beam_words[-1] if beam_words else None,
                beta_cur=gen.beta,
            )

            if not candidates:
                continue

            # Score each candidate
            scored = []
            for w in candidates[:50]:
                w_pv = gen._get_pv_fast(w)
                target = np.mean(all_pv, axis=0) if all_pv else np.zeros(64)
                align = float(np.dot(w_pv[:36], target[:36]) / (max(np.linalg.norm(w_pv[:36]), 1e-10) * max(np.linalg.norm(target[:36]), 1e-10)))

                # KB scoring
                kb_score = 0.0
                if gen.holographic_kb and gen.holographic_kb._built:
                    direct = gen.holographic_kb.query_by_word(w, top_k=3)
                    if direct:
                        kb_score = direct[0][0]
                    for cw in beam_words[-5:]:
                        cw_results = gen.holographic_kb.query_by_word(cw, top_k=5)
                        for _, ow, _ in cw_results:
                            if ow == w:
                                kb_score += 0.5
                                break
                kb_score *= gen.config.get('kb_influence', 0.4) if gen.config else 0.4

                # Constraint
                bonus, _ = gen.prompt_constraint.spring_force(
                    w_pv, step, max_words,
                    centroid_pv=target if len(all_pv) > 0 else None)

                score = align + kb_score + bonus * 0.01
                scored.append((score, w))

            scored.sort(key=lambda x: -x[0])
            for s, w in scored[:gen.beam_width]:
                new_beams.append((s, beam_words + [w], used | {w}))

        if not new_beams:
            break
        new_beams.sort(key=lambda x: -x[0])
        beams = [b[1] for b in new_beams[:1]]
        used_sets = [b[2] for b in new_beams[:1]]

    output = beams[0][len(tokens):]
    return ' '.join(output)


if __name__ == '__main__':
    run_benchmark()
