#!/usr/bin/env python3
"""Demo: KB influence on standard generation mode — KB ON vs OFF."""
import sys, os, time, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from model import load_model
from src.physics.holographic_kb import HolographicKB
from src.physics.word_physics import compute_extended_phase_vector, compute_word_mass
from src.physics.generator import Generator
import logging
logging.basicConfig(level=logging.WARNING)

data = load_model()
vocab = data['vocab']
vocab.load_supplemental(os.path.join(ROOT, 'model', 'vocab_supplemental.json'))

kb = HolographicKB(data_dir=os.path.join(ROOT, 'data'))
if os.path.exists(os.path.join(ROOT, 'data', 'holographic_kb.npz')):
    os.remove(os.path.join(ROOT, 'data', 'holographic_kb.npz'))
kb.load_curated_facts(os.path.join(ROOT, 'data', 'facts_expanded.json'), vocab, lambda w: compute_extended_phase_vector(w))
print(f"Loaded {kb.fact_count} KB facts\n")

gen = Generator.__new__(Generator)
gen.config = {'kb_influence': 0.4}
gen.vocab = vocab; gen.V = len(vocab); gen.old_semantic_dim = 36; gen.beta = 2.0; gen.current_tau = 1.0; gen.W = {}
gen.beamformer = None
gen.ram = type('obj',(object,),{'size':0})()
gen.entropy = type('obj',(object,),{'k_B':0.1,'S_crit':1.0,'compute_S':lambda s,t:0.0,'evaluate':lambda a,b,c,d:(0.1,2.0,None)})()
gen.phase_reinforcement = type('obj',(object,),{'apply':lambda s,w,pv:pv,'reinforce_sentence':lambda *a,**kw:None})()
gen.top_k = 500
gen.prompt_constraint = __import__('src.physics.prompt_constraint',fromlist=['PromptConstraintField']).PromptConstraintField(k_spring=3.0,damping=0.15)
gen.holographic_kb = kb
cache_path = os.path.join(ROOT, 'model', '_all_pv_cache.npy')
orig = np.load(cache_path)
if gen.V > orig.shape[0]:
    gen._all_pv = np.zeros((gen.V, orig.shape[1])); gen._all_pv[:orig.shape[0]] = orig
    for i in range(orig.shape[0], gen.V):
        w = vocab.id2word.get(i)
        if w: gen._all_pv[i] = compute_extended_phase_vector(w)
else:
    gen._all_pv = orig[:gen.V, :]
gen._precomputed_masses = {}
for i in range(min(gen.V, 30000)):
    w = vocab.id2word.get(i)
    if w: gen._precomputed_masses[w] = min(float(compute_word_mass(w)), 5.0)
for rt, bank in kb.banks.items():
    for w in bank['subj_words'] + bank['obj_words']:
        if w and w not in gen._precomputed_masses:
            gen._precomputed_masses[w] = min(float(compute_word_mass(w)), 5.0)
gen._dyn_mass = lambda w: gen._precomputed_masses.get(w, 1.0)
gen._get_pv_fast = lambda w: gen._all_pv[vocab.word2id[w]] if w in vocab.word2id else compute_extended_phase_vector(w)

def simple_generate(prompt, influence):
    tokens = []
    for w in prompt.split():
        wc = w.strip('.,;:!?()[]{}"')
        wid = vocab.get(wc)
        if wid is not None: tokens.append(vocab.id2word[wid])
    beams = [tokens[:]]
    used_sets = [set(tokens)]
    prompt_pv = [gen._get_pv_fast(w) for w in tokens]
    gen.prompt_constraint.set_prompt(prompt_pv)
    gen.config['kb_influence'] = influence
    for step in range(6):
        new_beams = []
        for beam_words, used in zip(beams, used_sets):
            all_pv = [gen._get_pv_fast(w) for w in beam_words]
            ctx_ids = [gen.vocab.word2id.get(w, -1) for w in beam_words]
            ctx_ids = [i for i in ctx_ids if i >= 0]
            candidates = gen._resonance_candidates(ctx_ids, all_pv, used, prev_word=beam_words[-1] if beam_words else None, beta_cur=gen.beta)
            if not candidates: continue
            scored = []
            for w in candidates[:50]:
                wpv = gen._get_pv_fast(w)
                target = np.mean(all_pv, axis=0) if all_pv else np.zeros(64)
                align = float(np.dot(wpv[:36], target[:36]) / (max(np.linalg.norm(wpv[:36]), 1e-10) * max(np.linalg.norm(target[:36]), 1e-10)))
                kbs = 0.0
                if gen.holographic_kb and gen.holographic_kb._built:
                    direct = gen.holographic_kb.query_bidirectional(w, top_k=3)
                    if direct: kbs = direct[0][0]
                    for cw in beam_words[-5:]:
                        for _, ow, _ in gen.holographic_kb.query_bidirectional(cw, top_k=5):
                            if ow == w: kbs += 0.5; break
                kbs *= influence
                bonus, _ = gen.prompt_constraint.spring_force(wpv, step, 6, centroid_pv=target if all_pv else None)
                scored.append((align + kbs + bonus * 0.01, w))
            scored.sort(key=lambda x: -x[0])
            for s, w in scored[:5]: new_beams.append((s, beam_words + [w], used | {w}))
        if not new_beams: break
        new_beams.sort(key=lambda x: -x[0])
        beams = [b[1] for b in new_beams[:1]]; used_sets = [b[2] for b in new_beams[:1]]
    return ' '.join(beams[0][len(tokens):])

prompts = [
    ("عاصمة فرنسا هي", ["باريس"]),
    ("من يصنع الخبز", ["خباز", "قمح"]),
    ("ما هو لون الثلج", ["أبيض", "صلب"]),
    ("يعمل الطبيب في", ["مستشفى"]),
    ("الورق مصنوع من", ["خشب"]),
]

print("=" * 70)
print("  KB Influence Demo: Standard Mode (ON vs OFF)")
print("=" * 70)

for prompt, expected in prompts:
    print(f"\nPrompt: '{prompt}'")
    print(f"  Expected: {expected}")
    out_off = simple_generate(prompt, 0.0)
    out_on = simple_generate(prompt, 0.6)
    hit_on = any(e in out_on for e in expected)
    hit_off = any(e in out_off for e in expected)
    print(f"  KB OFF (0.0): '{out_off}'  {'HIT' if hit_off else 'MISS'}")
    print(f"  KB ON  (0.6): '{out_on}'  {'HIT' if hit_on else 'MISS'}")
