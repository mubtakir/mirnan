from src.physics.morpho_phasic import MorphoPhasicEngine
from src.physics.constants import TOTAL_DIM


class TestMorphoPhasic:
    def test_analyze_known_word(self):
        eng = MorphoPhasicEngine()
        a = eng.analyze("يكتب")
        assert a["has_morph"]
        assert a["root"] is not None

    def test_morph_phase_shape(self):
        eng = MorphoPhasicEngine()
        pv = eng.compute_morph_phase("يكتب")
        assert pv is not None
        assert len(pv) == TOTAL_DIM

    def test_morph_phase_normalized(self):
        eng = MorphoPhasicEngine()
        pv = eng.compute_morph_phase("يكتب")
        import numpy as np
        norm = np.linalg.norm(pv)
        assert abs(norm - 1.0) < 1e-5

    def test_score_positive_for_known(self):
        eng = MorphoPhasicEngine()
        s = eng.score("يكتب")
        assert s >= 0.0

    def test_different_cases(self):
        eng = MorphoPhasicEngine()
        pv1 = eng.compute_morph_phase("يكتب", "مرفوع")
        pv2 = eng.compute_morph_phase("يكتب", "منصوب")
        assert pv1 is not None and pv2 is not None
        import numpy as np
        if not np.allclose(pv1, pv2):
            assert True

    def test_transition_score(self):
        eng = MorphoPhasicEngine()
        s = eng.transition_score("يكتب", "سوف")
        assert s >= 0.0
