import numpy as np
from src.physics.ram_core import AttractorMemory
from src.physics.entropy_gate import EntropyGate
from src.physics.word_physics import compute_extended_phase_vector
from src.physics.constants import TOTAL_DIM


class TestRAM:
    def test_empty_memory(self):
        ram = AttractorMemory()
        phi = np.zeros(TOTAL_DIM)
        assert ram.resonate(phi) == []
        assert ram.retrieve_context(phi) == []
        assert ram.size == 0

    def test_observe_and_resonate(self):
        ram = AttractorMemory()
        words = ['السلام', 'عليكم', 'ورحمة', 'الله']
        idx = ram.observe(words)
        assert idx == 0
        assert ram.size == 1
        phi = compute_extended_phase_vector('السلام')
        hits = ram.resonate(phi, top_k=1)
        assert len(hits) == 1
        assert hits[0][1] == 0
        assert hits[0][0] > 0.1

    def test_merge_similar(self):
        ram = AttractorMemory(merge_cos=0.8)
        w1 = ['السلام', 'عليكم', 'ورحمة']
        w2 = ['السلام', 'عليكم', 'وبركاته']
        ram.observe(w1)
        ram.observe(w2)
        assert ram.size == 1

    def test_no_merge_different(self):
        ram = AttractorMemory(merge_cos=0.999)
        w1 = ['السلام', 'عليكم', 'ورحمة', 'الله', 'وبركاته']
        w2 = ['ب', 'فقط', 'لا', 'في']
        ram.observe(w1)
        ram.observe(w2)
        assert ram.size == 2

    def test_retrieve_context(self):
        ram = AttractorMemory()
        ram.observe(['السلام', 'عليكم', 'ورحمة', 'الله', 'وبركاته'])
        phi = compute_extended_phase_vector('السلام')
        ctx = ram.retrieve_context(phi, max_words=3)
        assert len(ctx) > 0
        assert 'السلام' in ctx


class TestEntropyGate:
    def test_low_entropy_no_correction(self):
        gate = EntropyGate(S_crit=2.5)
        pv = np.ones(22) / np.linalg.norm(np.ones(22))
        pvs = [pv * 0.99, pv * 1.01]
        S = gate.compute_S(pvs, pv)
        assert S < gate.S_crit
        k, b, f = gate.evaluate(pvs, pv, 0.1, 2.0)
        assert k == 0.1
        assert b == 2.0

    def test_high_entropy_correction(self):
        gate = EntropyGate(S_crit=0.5)
        pv1 = np.array([1.0] + [0.0] * 21)
        pv1 = pv1 / np.linalg.norm(pv1)
        pv2 = np.array([0.0] * 21 + [1.0])
        pv2 = pv2 / np.linalg.norm(pv2)
        pvs = [pv1, pv2, pv1, pv2, pv1]
        target = pv1
        k, b, f = gate.evaluate(pvs, target, 0.1, 2.0)
        assert k < 0.1
        assert b > 2.0

    def test_entropy_mixed_similarity(self):
        gate = EntropyGate()
        pv1 = np.ones(22) / np.linalg.norm(np.ones(22))
        pv2 = np.arange(22, dtype=float)
        pv2 = pv2 / np.linalg.norm(pv2)
        pv3 = -np.ones(22) / np.linalg.norm(np.ones(22))
        target = np.ones(22) / np.linalg.norm(np.ones(22))
        S = gate.compute_S([pv1, pv2, pv3], target)
        assert 0 < S < 2.0

    def test_empty_pv_list(self):
        gate = EntropyGate()
        assert gate.compute_S([], np.zeros(22)) == 0.0
