#!/usr/bin/env python3
"""Fast test for PhasePathIntegralReasoner — minimal dependencies."""
import sys, os, time, logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

from model import load_model
from src.physics.generator import Generator, load_config
from src.physics.path_integral_reasoner import PhasePathIntegralReasoner


def main():
    data = load_model()
    vocab = data['vocab']
    config = load_config()

    # Build generator with minimal expensive init
    gen = Generator.__new__(Generator)
    gen.config = config
    gen.vocab = vocab
    gen.V = len(vocab)
    gen.alpha = 0.5
    gen.old_semantic_dim = 36

    # Preload PV cache
    import os as _os
    cache_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'model', '_all_pv_cache.npy')
    if _os.path.exists(cache_path):
        gen._all_pv = np.load(cache_path)[:gen.V, :]
        print(f"  ✓ Loaded {gen._all_pv.shape[0]} cached PVs")
    else:
        print("  ✗ No PV cache found")
        return

    # Minimal required attributes
    gen._pv_cache = {}
    gen._dressed_cache = {}
    gen._noun_boost_cache = {}
    gen.beta = 2.0
    gen.current_tau = 1.0
    gen.W = {}
    gen.beamformer = None
    gen.ram = type('obj', (object,), {'size': 0})()
    from src.physics.word_physics import compute_extended_phase_vector, compute_word_mass
    gen._get_pv_fast = lambda w: gen._all_pv[vocab.word2id[w]] if w in vocab.word2id else compute_extended_phase_vector(w)
    gen._dyn_mass = lambda w: compute_word_mass(w)
    from src.physics.prompt_constraint import PromptConstraintField
    gen.prompt_constraint = PromptConstraintField(k_spring=3.0, damping=0.15)
    gen.holographic_kb = None
    from src.physics.entropy_gate import EntropyGate
    gen.entropy = EntropyGate()
    gen.phase_reinforcement = type('obj', (object,), {
        'apply': lambda self, w, pv: pv,
        'reinforce_sentence': lambda *a, **kw: None,
    })()
    gen.top_k = 500
    # Pre-compute masses so _resonance_candidates is fast
    print("  Pre-computing word masses (one-time)...", end=' ', flush=True)
    from src.physics.word_physics import compute_word_mass
    gen._precomputed_masses = {}
    for i in range(min(gen.V, 10000)):  # Only top 10K for testing
        w = vocab.id2word.get(i)
        if w:
            gen._precomputed_masses[w] = float(compute_word_mass(w))
    gen._dyn_mass = lambda w: gen._precomputed_masses.get(w, 1.0)
    print(f"✓ ({len(gen._precomputed_masses)} words)")

    # Build reasoner with config
    gen.config = {**config, 'goal_gravity_weight': 0.3, 'reasoning': {
        'beam_width': 10, 'max_depth': 8, 'min_depth': 2, 'convergence_threshold': 0.75,
    }}
    reasoner = PhasePathIntegralReasoner(gen)

    prompts = [
        ("2-hop (ice→water→steam)",        "If ice melts it becomes water. If water boils it becomes steam. What does ice become if heated enough"),
        ("2-hop (Paris→France→Europe)",     "Paris is in France. France is in Europe. Where is Paris"),
        ("3-hop (knife→metal→ore→mountain)","A knife is made of metal. Metal comes from ore. Ore is found in mountains. Where does a knife ultimately come from"),
    ]

    for label, prompt in prompts:
        tokens = [vocab.id2word[vocab.get(w)] for w in prompt.split() if vocab.get(w) is not None]
        prompt_pv = [gen._get_pv_fast(w) for w in tokens]

        t0 = time.time()
        result = reasoner.reason(
            prompt_tokens=tokens,
            prompt_pv=prompt_pv,
            max_depth=5,
            beam_width=8,
        )
        elapsed = time.time() - t0

        chain = result.get('chain', [])
        converged = result.get('converged', False)
        final_sim = result.get('final_similarity', 0.0)
        path_len = result.get('path_length', 0)

        print(f"\n  [{label}] \"{prompt}\"")
        print(f"  Chain ({path_len} steps): {chain}")
        print(f"  Converged: {converged}  Final sim: {final_sim:.4f}  Time: {elapsed*1000:.0f}ms")

        if chain:
            print(f"  ✓ Produced chain")
        else:
            print(f"  ✗ Empty (fallback would activate in full generator)")


if __name__ == "__main__":
    main()
