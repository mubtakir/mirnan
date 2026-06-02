#!/usr/bin/env python3
"""Topological Invariants — Synonymy Experiment.

Tests the hypothesis that chains with the same meaning have similar
Berry Phase and Winding Number regardless of word choice.

الفرضية: الجمل التي تعبر عن نفس المعنى لها ثوابت طوبولوجية متشابهة
حتى لو اختلفت ألفاظها أو لغتها.
"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import load_model
from src.physics.word_physics import compute_extended_phase_vector
from src.physics.topological_invariants import TopologicalInvariants

data = load_model()
vocab = data['vocab']

# Load supplemental words
vocab.load_supplemental(os.path.join(os.path.dirname(__file__), 'model', 'vocab_supplemental.json'))

def pv(w):
    return compute_extended_phase_vector(w)

topo = TopologicalInvariants(dim=64, n_subspaces=5)

# ─── Test Groups ───
# Group A: State transition (ice→water→steam) — 4 variants
synonym_chains = {
    'AR-ثلج→ماء→بخار':    ['ثلج', 'ماء', 'بخار'],
    'AR-جليد→سائل→غاز':    ['جليد', 'سائل', 'غاز'],
    'AR-متجمد→ذائب→متبخر': ['متجمد', 'ذائب', 'متبخر'],
    'EN-ice→water→steam':   ['ice', 'water', 'steam'],
}

# Group B: Geographic (Paris→France→Europe)
geo_chains = {
    'AR-باريس→فرنسا→أوروبا': ['باريس', 'فرنسا', 'اوروبا'],
}

# Group C: Material (knife→metal→ore→mountains)
material_chains = {
    'AR-سكين→معدن→خام→جبال': ['سكين', 'معدن', 'خام', 'جبال'],
}

# Group D: Unrelated control
unrelated_chains = {
    'AR-تفاحة→فاكهة→طعام': ['تفاحة', 'فاكهة', 'طعام'],
    'AR-شمس→صباح→نهار':    ['شمس', 'صباح', 'نهار'],
}

# Combine all for analysis
all_chains = {}
all_chains.update(synonym_chains)
all_chains.update(geo_chains)
all_chains.update(material_chains)
all_chains.update(unrelated_chains)

print("=" * 72)
print("  Phase 3 — Topological Invariants: Synonymy Experiment")
print("=" * 72)

# ─── Compute invariants ───
print("\n[1] Computing topological invariants for each chain...")
results = {}
for name, words in all_chains.items():
    pvs = [pv(w) for w in words if vocab.get(w) is not None]
    if len(pvs) < 2:
        print(f"    ✗ {name}: insufficient words ({len(pvs)})")
        continue
    inv = topo.compute_invariants(pvs)
    results[name] = {'bp': inv['berry_phase'], 'wn': inv['winding_number'], 'pv_count': len(pvs)}
    print(f"    {name:<25} BP={inv['berry_phase']:7.3f}  WN={inv['winding_number']:+8.3f}")

# ─── Similarity matrix ───
print("\n[2] Topological Similarity Matrix...")
names = list(results.keys())
n = len(names)
matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        pvs_i = [pv(w) for w in all_chains[names[i]] if vocab.get(w) is not None]
        pvs_j = [pv(w) for w in all_chains[names[j]] if vocab.get(w) is not None]
        matrix[i, j] = topo.topological_similarity(pvs_i, pvs_j)

# Print matrix
header = "           " + "  ".join(f"{n[:15]:<15}" for n in names)
print(header)
for i, name in enumerate(names):
    row = f"  {name:<20}"
    for j in range(n):
        val = matrix[i, j]
        if i == j:
            row += f"  {'=' * 5}   "
        elif val > 0.7:
            row += f"  \033[92m{val:.3f}\033[0m   "  # green
        elif val > 0.5:
            row += f"  \033[93m{val:.3f}\033[0m   "  # yellow
        else:
            row += f"  \033[91m{val:.3f}\033[0m   "  # red
    print(row)

# ─── Analysis ───
print("\n[3] Analysis...")
# Within-group averages
for group_name, group in [('Synonym', synonym_chains), ('Geo', geo_chains),
                            ('Material', material_chains), ('Unrelated', unrelated_chains)]:
    group_names = [n for n in names if n in group]
    if len(group_names) >= 2:
        pairs = [(i, j) for i, gi in enumerate(group_names) for j, gj in enumerate(group_names) if i < j]
        avg_sim = np.mean([matrix[names.index(gi), names.index(gj)] for gi, gj in pairs])
        print(f"  {group_name:<12} intra-group similarity: {avg_sim:.3f}")

# Cross-group comparisons
syn_names = [n for n in names if n in synonym_chains]
mat_names = [n for n in names if n in material_chains]
unr_names = [n for n in names if n in unrelated_chains]

if syn_names and unr_names:
    cross_sims = []
    for sn in syn_names:
        for un in unr_names:
            cross_sims.append(matrix[names.index(sn), names.index(un)])
    print(f"  Synonym↔Unrelated cross-group: {np.mean(cross_sims):.3f}")

if syn_names and mat_names:
    cross_sims = []
    for sn in syn_names:
        for mn in mat_names:
            cross_sims.append(matrix[names.index(sn), names.index(mn)])
    print(f"  Synonym↔Material cross-group: {np.mean(cross_sims):.3f}")

# ─── Verdict ───
print("\n[4] Verdict...")
if syn_names:
    intra_syn = np.mean([matrix[names.index(s1), names.index(s2)]
                         for s1 in syn_names for s2 in syn_names if s1 < s2])
    intra_unr = np.mean([matrix[names.index(u1), names.index(u2)]
                         for u1 in unr_names for u2 in unr_names if u1 < u2])
    cross_syn_unr = np.mean([matrix[names.index(s), names.index(u)]
                             for s in syn_names for u in unr_names])

    print(f"  Intra-synonym avg: {intra_syn:.3f}")
    print(f"  Intra-unrelated avg: {intra_unr:.3f}")
    print(f"  Cross-group avg: {cross_syn_unr:.3f}")

    if intra_syn > 0.5 and cross_syn_unr < 0.3:
        print("\n  ✓ HYPOTHESIS CONFIRMED — Topological invariants distinguish related from unrelated chains")
    elif intra_syn > cross_syn_unr * 1.3:
        print("\n  ○ WEAKLY CONFIRMED — Intra-synonym > cross-group, but margin is small")
    else:
        print("\n  ✗ HYPOTHESIS REJECTED — Topological invariants do not reliably distinguish meaning")

print("\n" + "=" * 72)
