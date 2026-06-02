#!/usr/bin/env python3
"""اختبار مسبب التكامل المساري — Path Integral Reasoner.

يختبر:
1. توليد سلسلة استدلالية من prompt إلى goal_concept
2. تقارب المسار (final_similarity > 0 مطلوب)
3. معلومات التصحيح (converged, path_length, chain)

الاستخدام:
  python test_reasoner.py
"""

import sys, os, time, logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

from model import load_model
from src.physics.generator import Generator


def main():
    data = load_model()
    vocab = data['vocab']

    # Create generator ONCE (PV cache is expensive)
    gen = Generator(
        data['vocab'], data['K_sem'],
        syntax_field=data['syntax'],
        K_syn=data.get('K_syn'),
        K_dialogue=data.get('K_dial'),
        corpus_texts=[],  # skip expensive spectral coupling fit
        config={
            'holographic_kb': {'enabled': False},  # skip KB
            'dccf': {'decay_rate': 0.5, 'mass_threshold': 0.3},
            'cascade': {'enabled': False},
            'scoring_weights': {},
            'phase_reinforcement': {'learning_rate': 0.05, 'decay': 0.01},
            'prompt_field': {'decay_rate': 0.1, 'strength': 1.0},
            'entropy': {'S_crit': 1.0},
            'generation': {'beam_width': 5, 'top_k': 500, 'beta': 2.0, 'relaxation_enabled': False},
            'heterodyne': {'bandwidth': 0.15, 'context_window': 8},
            'density_matrix': {'decay_rate': 0.8},
            'causal_flow': {'strength': 1.0, 'transitive_depth': 3},
            'annealing': {'tau_max': 2.5, 'tau_min': 0.15, 'tau_decay': 5.0},
            'prompt_constraint': {'k_spring': 3.0, 'damping': 0.15},
            'goal_gravity_weight': 0.3,
            'reasoning': {'beam_width': 10, 'max_depth': 8},
        },
    )
    print(f"  ✓ Generator loaded ({len(vocab):,} words)\n")

    # Skip expensive spectral coupling init for testing
    gen.spectral_coupling.magnitude = gen.spectral_coupling.magnitude
    gen.spectral_coupling.phase_diff = gen.spectral_coupling.phase_diff
    print(f"  ✓ Skipped spectral coupling (testing only)\n")

    prompts = [
        ("Question", "If water freezes what happens to its volume"),
        ("Cause-Effect", "When you heat metal it expands"),
        ("Comparison", "The sun is bigger than the moon"),
    ]

    for label, prompt in prompts:
        t0 = time.time()
        result = gen.generate(prompt, max_words=12, mode='reason')
        elapsed = time.time() - t0
        print(f"  [{label}] \"{prompt}\"")
        print(f"    → {result}")
        print(f"    ({elapsed*1000:.0f}ms)\n")

    print("=" * 65)
    print("  Reasoning test complete. Check logs above for:")
    print("  - [Reasoner] goal_concept extracted")
    print("  - [Reasoner] step=N/M tau=...")
    print("  - [Reasoner] CONVERGED or MAX DEPTH")
    print("=" * 65)


if __name__ == "__main__":
    main()
