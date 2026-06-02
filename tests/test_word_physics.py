from src.physics.constants import PHASE_DIM
from src.physics.word_physics import (
    compute_word_frequency,
    compute_word_energy,
    compute_word_mass,
    compute_word_phase_vector,
)


class TestWordPhysics:
    def test_mass_allah_gt_qalam(self):
        m_allah = compute_word_mass("\u0627\u0644\u0644\u0647")
        m_qalam = compute_word_mass("\u0642\u0644\u0645")
        assert m_allah > m_qalam, f"mass(\u0627\u0644\u0644\u0647)={m_allah:.4f} <= mass(\u0642\u0644\u0645)={m_qalam:.4f}"

    def test_mass_3_letters_positive(self):
        for word in ["\u0642\u0644\u0645", "\u0643\u062A\u0628", "\u0639\u0644\u0645", "\u0628\u064A\u062A"]:
            m = compute_word_mass(word)
            assert m > 0, f"mass({word}) = {m}"

    def test_frequency_in_expected_range(self):
        for word in ["\u0627\u0644\u0644\u0647", "\u0631\u062D\u0645\u0646", "\u0643\u0631\u064A\u0645"]:
            f = compute_word_frequency(word)
            assert f > 0, f"freq({word}) = {f}"

    def test_phase_vector_shape(self):
        for word in ["\u0639\u0644\u0645", "\u064A\u0643\u062A\u0628"]:
            v = compute_word_phase_vector(word)
            assert v.shape == (PHASE_DIM,), f"shape({word}) = {v.shape}"

    def test_energy_from_frequency(self):
        f = compute_word_frequency("\u0642\u0644\u0645")
        e = compute_word_energy("\u0642\u0644\u0645")
        assert abs(e - f) < 1e-10, f"E = h*f not satisfied"

    def test_mass_from_energy(self):
        e = compute_word_energy("\u0642\u0644\u0645")
        m = compute_word_mass("\u0642\u0644\u0645")
        assert abs(m - e) < 1e-10, f"m = E/c\u00b2 not satisfied"
