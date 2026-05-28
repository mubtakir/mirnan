import numpy as np
from src.physics.constants import PHASE_DIM
from src.physics.word_physics import (
    compute_word_frequency,
    compute_word_mass,
    compute_word_phase_vector,
)
from src.physics.oscillator import OscillatorEngine


class TestOscillatorEngine:
    def test_simulate_two_words(self):
        words = ["\u0642\u0644\u0645", "\u0643\u062A\u0628"]
        n = len(words)
        omega = np.array([[compute_word_frequency(w)] * PHASE_DIM for w in words])
        phases = np.random.uniform(0, 2*np.pi, (n, PHASE_DIM))
        masses = np.array([compute_word_mass(w) for w in words])
        pv = np.array([compute_word_phase_vector(w) for w in words])
        K = np.eye(n) * 0.5
        eng = OscillatorEngine()
        final, history = eng.simulate(omega, phases, masses, pv, K, dt=0.01, steps=500)
        assert final.shape == (n, PHASE_DIM), f"shape={final.shape}"
        assert not np.any(np.isnan(final)), "NaN in phases"

    def test_three_words_stable(self):
        words = ["\u0627\u0644\u0644\u0647", "\u0631\u062D\u0645\u0646", "\u0631\u062D\u064A\u0645"]
        n = len(words)
        omega = np.array([[compute_word_frequency(w)] * PHASE_DIM for w in words])
        phases = np.zeros((n, PHASE_DIM))
        masses = np.array([compute_word_mass(w) for w in words])
        pv = np.array([compute_word_phase_vector(w) for w in words])
        K = np.ones((n, n)) * 0.3
        np.fill_diagonal(K, 0)
        eng = OscillatorEngine()
        final, history = eng.simulate(omega, phases, masses, pv, K, dt=0.05, steps=200)
        assert final.shape == (n, PHASE_DIM)
        last_diff = np.mean(np.abs(history[-1] - history[-2]))
        assert last_diff < 1.0, f"phases not stabilizing: {last_diff}"
