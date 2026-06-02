#!/usr/bin/env python3
"""Multi-hop reasoning test — final stabilized version with auto-loaded supplemental words."""
import sys, os, time, logging, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
logging.getLogger('src.physics.path_integral_reasoner').setLevel(logging.WARNING)

from model import load_model
from src.physics.generator import Generator, load_config
from src.physics.path_integral_reasoner import PhasePathIntegralReasoner
from src.physics.holographic_kb import HolographicKB

data = load_model()
vocab = data['vocab']
config = load_config()

# Load supplemental words FIRST (before KB)
vocab.load_supplemental(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', 'vocab_supplemental.json'))

# Then load KB (so KB sees supplemental words)
kb = HolographicKB(data_dir="data")
if os.path.exists("data/holographic_kb.npz"):
    os.remove("data/holographic_kb.npz")
from src.physics.word_physics import compute_extended_phase_vector
pv_fn = lambda w: compute_extended_phase_vector(w)
n = kb.load_curated_facts("data/facts_minimal.json", vocab, pv_fn)
print(f"  KB: {n} facts loaded\n")

# Minimal generator
gen = Generator.__new__(Generator)
gen.config = {
    'goal_gravity_weight': 0.3,
    'reasoning': {'beam_width': 10, 'max_depth': 8, 'min_depth': 2, 'convergence_threshold': 0.75},
    'vocab_supplemental': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', 'vocab_supplemental.json'),
}
gen.vocab = vocab
gen.vocab.load_supplemental(gen.config['vocab_supplemental'])
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
gen._dyn_mass = lambda w: min(float(compute_word_mass(w)), 5.0)  # mass cap
from src.physics.prompt_constraint import PromptConstraintField
gen.prompt_constraint = PromptConstraintField(k_spring=3.0, damping=0.15)
gen.holographic_kb = kb

cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', '_all_pv_cache.npy')
orig = np.load(cache_path)
if gen.V > orig.shape[0]:
    gen._all_pv = np.zeros((gen.V, orig.shape[1]))
    gen._all_pv[:orig.shape[0]] = orig
    for i in range(orig.shape[0], gen.V):
        w = vocab.id2word.get(i)
        if w:
            gen._all_pv[i] = pv_fn(w)
else:
    gen._all_pv = orig[:gen.V, :]

# Pre-compute masses
gen._precomputed_masses = {}
for i in range(min(gen.V, 20000)):
    w = vocab.id2word.get(i)
    if w:
        gen._precomputed_masses[w] = min(float(compute_word_mass(w)), 5.0)
for rt, bank in kb.banks.items():
    for w in bank['subj_words'] + bank['obj_words']:
        if w and w not in gen._precomputed_masses:
            gen._precomputed_masses[w] = min(float(compute_word_mass(w)), 5.0)
gen._dyn_mass = lambda w: gen._precomputed_masses.get(w, 1.0)

reasoner = PhasePathIntegralReasoner(gen)

prompts = [
    ('2-hop (ثلج)', 'الثلج يذوب ويصبح ماء. الماء يغلي ويصبح بخار. ماذا يصبح الثلج إذا سخن', ['ماء','بخار']),
    ('2-hop (باريس)', 'باريس في فرنسا. فرنسا في أوروبا. أين باريس', ['فرنسا','أوروبا']),
    ('3-hop (سكين)', 'السكين مصنوع من معدن. المعدن يستخرج من خام. الخام يوجد في جبال. من أين يأتي السكين', ['معدن','خام','جبال']),
]

print("=" * 55)
print("  Phase 2.5 — Final Verification (5 trials each)")
print("=" * 55)

for label, prompt, expected in prompts:
    successes = 0
    best_chain = None
    total_steps = []
    
    for trial in range(5):
        tokens = []
        for w in prompt.split():
            w_clean = w.strip('.,;:!?()[]{}""''\'')
            wid = vocab.get(w_clean)
            if wid is not None:
                tokens.append(vocab.id2word[wid])
        
        pv = [gen._get_pv_fast(w) for w in tokens]
        result = reasoner.reason(prompt_tokens=tokens, prompt_pv=pv, max_depth=6, beam_width=10)
        chain = result.get('chain', [])
        correct = any(e in chain for e in expected)
        print(f"  [{label}] chain={chain}  correct={correct}")

print("\n" + "=" * 55)
