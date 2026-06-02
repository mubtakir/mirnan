#!/usr/bin/env python3
"""Demo: Prompt Constraint Field ON vs OFF.

Shows how the Dirichlet spring forces pull candidate words toward
prompt-aligned regions of phase space.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import load_model
from src.physics.word_physics import compute_extended_phase_vector, phase_similarity
from src.physics.prompt_constraint import PromptConstraintField


def get_pv(word):
    return compute_extended_phase_vector(word)


def main():
    data = load_model()
    vocab = data['vocab']

    pcf = PromptConstraintField(k_spring=3.0, damping=0.15)

    # ─── Take a concrete prompt ───
    prompt = "الجو جميل اليوم"
    prompt_words = prompt.split()
    prompt_pvs = [get_pv(w) for w in prompt_words]
    pcf.set_prompt(prompt_pvs)

    print("=" * 70)
    print(f'  Prompt Constraint Field DEMO:  "{prompt}"')
    print("=" * 70)
    print()

    # ─── Show the constraints ───
    print("Spring anchors (constraints):")
    for i, (w, pv) in enumerate(zip(prompt_words, prompt_pvs)):
        pos = i / max(len(prompt_pvs) - 1, 1)
        print(f"  [{i}] \"{w}\"  at progress={pos:.0%}  |pv|={np.linalg.norm(pv):.3f}")
    print()

    # ─── Test candidates: some RELATED, some UNRELATED ───
    candidates = [
        ("شمس",    "related - weather"),
        ("سماء",   "related - sky"),
        ("مطر",    "related - rain"),
        ("هواء",   "related - air"),
        ("سيارة",  "unrelated - car"),
        ("تفاحة",  "unrelated - apple"),
        ("حديد",   "unrelated - iron"),
    ]

    n_steps = 4
    print(f"{'Candidate':<10} {'Type':<20} ", end="")
    for step in range(n_steps):
        progress = step / max(n_steps, 1)
        target_idx = int(progress * (len(prompt_pvs) - 1))
        target_word = prompt_words[target_idx]
        print(f"  step={step} ", end="")
    print()
    print("-" * 70)

    for word, label in candidates:
        pv = get_pv(word)
        print(f"{word:<10} {label:<20}", end="")

        for step in range(n_steps):
            constraint_score, force_vec = pcf.spring_force(pv, step, n_steps)
            # Also compute gravity score without constraint (cosine to centroid)
            centroid = np.mean(prompt_pvs, axis=0)
            centroid = centroid / max(np.linalg.norm(centroid), 1e-10)
            gravity_only = phase_similarity(pv, centroid)

            # Visual bar
            bar_len = int(constraint_score * 20)
            if constraint_score > gravity_only:
                marker = "+"  # constraint HELPS
            elif constraint_score < gravity_only - 0.01:
                marker = "-"  # constraint HURTS
            else:
                marker = "="  # neutral

            print(f"  {marker}{'#'*bar_len}{'.'*(20-bar_len)} {constraint_score:.3f}", end="")
        print()

    print()
    print("Legend:  + = constraint PULLS toward prompt (higher = stronger pull)")
    print("         = = neutral (constraint ≈ gravity)")
    print("         - = constraint PUSHES away (unrelated word penalized)")
    print()

    # ─── Show numeric comparison for step=2 ───
    print("Detailed comparison at step=2 (mid-generation):")
    centroid = np.mean(prompt_pvs, axis=0)
    centroid = centroid / max(np.linalg.norm(centroid), 1e-10)
    step = 2

    for word, label in candidates:
        pv = get_pv(word)
        cs, _ = pcf.spring_force(pv, step, n_steps)
        grav = phase_similarity(pv, centroid)
        delta = cs - grav
        tag = "BENEFIT(+)" if delta > 0.03 else ("PENALTY(-)" if delta < -0.03 else "NEUTRAL")
        print(f"  {word:<10}  constraint={cs:.4f}  gravity={grav:.4f}  delta={delta:+.4f}  {tag}  ({label})")


if __name__ == "__main__":
    main()
