#!/usr/bin/env python3
"""Multi-hop reasoning test with cleaned vocab + curated KB facts."""
import sys, os, time, logging, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

from model import load_model
from src.physics.generator import Generator, load_config
from src.physics.path_integral_reasoner import PhasePathIntegralReasoner
from src.physics.holographic_kb import HolographicKB

data = load_model()
vocab = data['vocab']
config = load_config()

# Load supplemental words (must be done BEFORE KB build for new facts to work)
import json
supp_path = "data/supplemental_words.json"
if os.path.exists(supp_path):
    with open(supp_path, encoding='utf-8') as f:
        supp = json.load(f)
    for w in supp.get('words', []):
        try:
            vocab.add(w)
        except Exception:
            pass
    print(f"  ✓ Loaded {supp.get('added',0)} supplemental words\n")

# ─── Load Holographic KB with curated facts ───
kb = HolographicKB(data_dir="data")
# Delete old KB to force rebuild
if os.path.exists("data/holographic_kb.npz"):
    os.remove("data/holographic_kb.npz")

from src.physics.word_physics import compute_extended_phase_vector
def pv_fn(w):
    return compute_extended_phase_vector(w)

n = kb.load_curated_facts("data/facts_minimal.json", vocab, pv_fn)
print(f"  ✓ Loaded {n} curated facts into KB\n")

# Check which facts were stored
for rt, bank in kb.banks.items():
    if rt == "CURATED":
        for i in range(len(bank['keys'])):
            print(f"    {bank['subj_words'][i]} → {bank['obj_words'][i]}")

print()

# ─── Minimal generator ───
gen = Generator.__new__(Generator)
gen.config = {
    'goal_gravity_weight': 0.3,
    'reasoning': {'beam_width': 10, 'max_depth': 8, 'min_depth': 2, 'convergence_threshold': 0.75},
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
from src.physics.word_physics import compute_word_mass
gen._get_pv_fast = lambda w: gen._all_pv[vocab.word2id[w]] if w in vocab.word2id else pv_fn(w)
gen._dyn_mass = lambda w: float(compute_word_mass(w))
from src.physics.prompt_constraint import PromptConstraintField
gen.prompt_constraint = PromptConstraintField(k_spring=3.0, damping=0.15)
gen.holographic_kb = kb  # Use the curated KB

cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', '_all_pv_cache.npy')
original_pvs = np.load(cache_path)
if gen.V > original_pvs.shape[0]:
    # Pad with zeros for newly added words
    gen._all_pv = np.zeros((gen.V, original_pvs.shape[1]))
    gen._all_pv[:original_pvs.shape[0], :] = original_pvs
    # Compute PVs on-the-fly for new words
    for i in range(original_pvs.shape[0], gen.V):
        w = vocab.id2word.get(i)
        if w:
            gen._all_pv[i] = pv_fn(w)
    print(f'  Padded {gen.V - original_pvs.shape[0]} new PVs (total: {gen.V})')
else:
    gen._all_pv = original_pvs[:gen.V, :]
    print(f'  Loaded {gen._all_pv.shape[0]} PVs')

# Pre-compute masses
print('  Pre-computing masses...', end=' ', flush=True)
gen._precomputed_masses = {}
for i in range(min(gen.V, 20000)):
    w = vocab.id2word.get(i)
    if w:
        gen._precomputed_masses[w] = float(compute_word_mass(w))
# Also add mass for all KB words (they need non-zero mass)
if kb is not None:
    for rt, bank in kb.banks.items():
        for w in bank['subj_words'] + bank['obj_words']:
            if w and w not in gen._precomputed_masses:
                gen._precomputed_masses[w] = float(compute_word_mass(w))
gen._dyn_mass = lambda w: gen._precomputed_masses.get(w, 1.0)
print(f'OK ({len(gen._precomputed_masses)} words)')

reasoner = PhasePathIntegralReasoner(gen)

# ─── Multi-hop tests ───
prompts = [
    ('2-hop (ثلج→ماء→بخار)',
     'الثلج يذوب ويصبح ماء. الماء يغلي ويصبح بخار. ماذا يصبح الثلج إذا سخن'),
    ('2-hop (باريس→فرنسا→أوروبا)',
     'باريس في فرنسا. فرنسا في أوروبا. أين باريس'),
    ('3-hop (سكين→معدن→خام→جبال)',
     'السكين مصنوع من معدن. المعدن يستخرج من خام. الخام يوجد في جبال. من أين يأتي السكين'),
]

for label, prompt in prompts:
    # Strip punctuation from tokens
    tokens = []
    for w in prompt.split():
        w_clean = w.strip('.,;:!?()[]{}""''\'')
        wid = vocab.get(w_clean)
        if wid is not None:
            tokens.append(vocab.id2word[wid])
    pv = [gen._get_pv_fast(w) for w in tokens]
    t0 = time.time()
    result = reasoner.reason(prompt_tokens=tokens, prompt_pv=pv, max_depth=6, beam_width=10)
    elapsed = time.time() - t0
    chain = result.get('chain', [])
    conv = result.get('converged', False)
    sim = result.get('final_similarity', 0.0)
    steps = result.get('path_length', 0)
    print(f'\n  [{label}]')
    print(f'    Steps: {steps}  Converged: {conv}  Sim: {sim:.4f}  Time: {elapsed*1000:.0f}ms')
    print(f'    Chain: {chain}')

    # Check correctness
    expected_words = {
        '2-hop': ['ماء', 'بخار'],
        'geo': ['فرنسا', 'أوروبا'],
        '3-hop': ['معدن', 'خام', 'جبال'],
    }
    correct = any(w in chain for w in expected_words.get('2-hop', []) + expected_words.get('geo', []) + expected_words.get('3-hop', []))
    print(f'    Correct? {"YES" if correct else "NO"}')

print("\n" + "=" * 60)
