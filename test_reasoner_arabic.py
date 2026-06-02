#!/usr/bin/env python3
"""Multi-hop reasoning test with Arabic prompts."""
import sys, os, time, logging, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

from model import load_model
from src.physics.generator import Generator, load_config
from src.physics.path_integral_reasoner import PhasePathIntegralReasoner

data = load_model()
vocab = data['vocab']
config = load_config()

# Check key words
for w in ['باريس', 'فرنسا', 'أوروبا', 'سكين', 'معدن', 'جبل', 'ثلج', 'ماء', 'بخار',
          'ice', 'water', 'steam', 'metal', 'ore']:
    wid = vocab.get(w)
    print(f'  {w}: {"YES" if wid else "NO"}')

print()

# Minimal generator
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
from src.physics.word_physics import compute_extended_phase_vector, compute_word_mass
gen._get_pv_fast = lambda w: gen._all_pv[vocab.word2id[w]] if w in vocab.word2id else compute_extended_phase_vector(w)
gen._dyn_mass = lambda w: float(compute_word_mass(w))
from src.physics.prompt_constraint import PromptConstraintField
gen.prompt_constraint = PromptConstraintField(k_spring=3.0, damping=0.15)
gen.holographic_kb = None

cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model', '_all_pv_cache.npy')
gen._all_pv = np.load(cache_path)[:gen.V, :]
print(f'  Loaded {gen._all_pv.shape[0]} PVs')

# Pre-compute masses to avoid O(167K) loop
print('  Pre-computing masses...', end=' ', flush=True)
gen._precomputed_masses = {}
for i in range(min(gen.V, 20000)):
    w = vocab.id2word.get(i)
    if w:
        gen._precomputed_masses[w] = float(compute_word_mass(w))
gen._dyn_mass = lambda w: gen._precomputed_masses.get(w, 1.0)
print(f'OK ({len(gen._precomputed_masses)} words)')

reasoner = PhasePathIntegralReasoner(gen)

# Arabic prompts with words IN the vocabulary
prompts = [
    ('AR 2-hop',  'الثلج يذوب ويصبح ماء. الماء يغلي ويصبح بخار. ماذا يصبح الثلج إذا سخن'),
    ('AR geo',    'باريس في فرنسا. فرنسا في أوروبا. أين باريس'),
    ('AR 3-hop',  'السكين مصنوع من حديد. الحديد يأتي من خام. الخام يوجد في جبال. من أين يأتي السكين'),
]

for label, prompt in prompts:
    tokens = [vocab.id2word[vocab.get(w)] for w in prompt.split() if vocab.get(w) is not None]
    pv = [gen._get_pv_fast(w) for w in tokens]
    t0 = time.time()
    result = reasoner.reason(prompt_tokens=tokens, prompt_pv=pv, max_depth=6, beam_width=10)
    elapsed = time.time() - t0
    chain = result.get('chain', [])
    conv = result.get('converged', False)
    sim = result.get('final_similarity', 0.0)
    steps = result.get('path_length', 0)
    print(f'[{label}] steps={steps} converged={conv} sim={sim:.4f} time={elapsed*1000:.0f}ms')
    print(f'  Chain: {chain}')
    print()
