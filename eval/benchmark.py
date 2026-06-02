"""Benchmark عربي لقياس دقة التوقع (cloze task).

يقيس:
- Precision@1: كم مرة كان المرشح الأول هو الكلمة الصحيحة
- Precision@5: كم مرة كانت الكلمة الصحيحة ضمن أول 5 مرشحين
- Pseudo-perplexity: متوسط −log(prob) للكلمة الصحيحة
"""

import sys
import math
import numpy as np

BENCH_SENTENCES = [
    ("الملك", "حكم", "البلاد"),
    ("السماء", "زرقاء", "واضحة"),
    ("الطالب", "يدرس", "الدرس"),
    ("الماء", "بارد", "جدا"),
    ("الشمس", "تشرق", "كل"),
    ("القط", "ياكل", "السمك"),
    ("المريض", "يشرب", "الدواء"),
    ("العراق", "بلد", "عربي"),
]

BENCH_PROMPTS = [
    "السلام عليكم",
    "كيف حالك",
    "ما هو اسمك",
    "من انت",
    "الحمد لله",
    "بسم الله الرحمن الرحيم",
    "العلم نور",
    "الصدق امانة",
]

def run_benchmark(generator_fn, top_k=50):
    """تشغيل benchmark على مولد معين.

    Args:
        generator_fn: دالة توقع (context, candidates) → [(score, word), ...]
    Returns:
        dict: نتائج benchmark
    """
    p1_correct = 0
    p5_correct = 0
    total_ll = 0.0
    total = 0

    for ctx, expected, _ in BENCH_SENTENCES:
        try:
            scored = generator_fn(ctx, top_k)
        except Exception:
            continue
        if not scored:
            continue
        total += 1
        words = [w for _, w in scored]
        if words and words[0] == expected:
            p1_correct += 1
        if expected in words[:5]:
            p5_correct += 1
        scores_dict = {w: s for s, w in scored}
        if expected in scores_dict:
            prob = np.exp(scores_dict[expected])
            prob = max(prob, 1e-12)
            total_ll += -math.log(prob)
        else:
            total_ll += 10.0

    precision1 = p1_correct / max(total, 1)
    precision5 = p5_correct / max(total, 1)
    perplexity = math.exp(total_ll / max(total, 1))

    return {
        "samples": total,
        "precision@1": precision1,
        "precision@5": precision5,
        "pseudo_perplexity": perplexity,
    }


if __name__ == "__main__":
    from src.physics.synchronize import synchronize
    from src.physics.generator import Generator

    corpus = [" ".join(s) for s in BENCH_SENTENCES]
    vocab, K, syntax = synchronize(corpus)
    gen = Generator(vocab, K, corpus_texts=corpus, syntax_field=syntax)

    def scorer(context, top_k=50):
        words = context.split()
        all_pv = [gen._get_pv_fast(w) for w in words]
        context_ids = [vocab.word2id.get(w, None) for w in words]
        prev_word = words[-1] if words else None
        candidates = gen._resonance_candidates(context_ids, all_pv, set(), prev_word=prev_word)
        if not candidates:
            return []
        _prev_freqs = None
        if len(words) >= 2 and hasattr(gen, 'resonant_chain'):
            from src.physics.word_physics import compute_word_mass
            _prev_freqs = []
            for k in range(1, len(words)):
                wa, wb = words[k - 1], words[k]
                _prev_freqs.append(gen.resonant_chain.pair_freq(
                    gen._dyn_mass(wa), gen._dyn_mass(wb),
                    gen._get_pv_fast(wa), gen._get_pv_fast(wb)))
        scored = [(gen._score(w, set(), all_pv, [], len(words), len(words) + 10,
                              prev_word, context_ids, words, gen.entropy.k_B, gen.beta, None,
                              _prev_freqs=_prev_freqs), w)
                  for w in candidates[:top_k]]
        scored.sort(key=lambda x: -x[0])
        return scored

    result = run_benchmark(scorer)
    print(f"Samples: {result['samples']}")
    print(f"Precision@1: {result['precision@1']:.3f}")
    print(f"Precision@5: {result['precision@5']:.3f}")
    print(f"Pseudo-perplexity: {result['pseudo_perplexity']:.3f}")

    for ctx, expected, _ in BENCH_SENTENCES:
        scored = scorer(ctx, 5)
        top_words = [w for _, w in scored[:5]]
        ok = "✓" if scored and scored[0][1] == expected else "✗"
        print(f"  {ok} {ctx} → توقع: {top_words} (الصحيح: {expected})")
