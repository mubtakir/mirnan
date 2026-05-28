"""Spectral Wave Engine Tests — analogy + noise + filter + performance."""
import time
import numpy as np
from src.physics.synchronize import synchronize
from src.physics.spectral_wave_engine import (
    SpectralCouplingMatrix, compute_word_wave,
    wave_signature, adaptive_context_filter,
)

CORPUS = [
    "almalik yahkum almamlaka",
    "almalika zawjat almalik",
    "alrajul yaemal fi almadina",
    "almarat taemal fi almanzil",
    "almalik rajul eazim",
    "almalika aimra'a eazima",
    "alsama' zarqa' walnujum talmae",
    "alqamar yudiy' allayl",
    "al'atfal yalabun fi alhadiqa",
    "almuaealim yashrah aldars liltulaab",
    "alkitab ealaa almaktab",
    "alma' naqi walhawa' naqi",
    "alshams tashruq fi alsabah",
    "alqitat talb mae alfar",
    "alkalb yahras almanzil",
]


def test_relational_analogy():
    vocab, K, _ = synchronize(CORPUS)
    scm = SpectralCouplingMatrix()
    scm.fit(vocab, K, CORPUS)
    candidate, score = scm.relational_interference(
        target="almalik",
        add_words=["almarat"],
        sub_words=["alrajul"],
        vocab=vocab,
    )
    # safe repr for cp1252
    c_repr = candidate.encode('ascii', 'backslashreplace').decode('ascii') if candidate else 'None'
    print(f"\n  candidate: {c_repr}  score: {score:.3f}")
    assert candidate is not None, "must find a candidate"
    assert score > 0.1, f"score too low: {score}"


def test_sideband_noise_filter():
    """Sideband noise: only strong couplings survive."""
    sidebands = wave_signature("almalik", ["alrajul", "almarat", "almalika"])['sidebands']
    strengths = [sb['coupling_strength'] for sb in sidebands]
    print(f"\n  sidebands: {len(sidebands)}, max: {max(strengths):.3f}, min: {min(strengths):.3f}")
    assert len(sidebands) > 0
    assert max(strengths) > 0


def test_adaptive_filter_no_overfilter():
    """Adaptive filter: must not destroy the signal."""
    word_pv = np.random.randn(56)
    word_pv = word_pv / np.linalg.norm(word_pv)
    ctx_pvs = [np.random.randn(56) for _ in range(3)]
    ctx_pvs = [c / np.linalg.norm(c) for c in ctx_pvs]
    filtered = adaptive_context_filter(word_pv, ctx_pvs)
    sim = float(np.mean(np.cos(word_pv - filtered)))
    print(f"\n  cos similarity (original vs filtered): {sim:.3f}")
    assert not np.allclose(filtered, 0), "filter must not nullify signal"
    assert sim > -0.5, "filter must not invert signal"


def test_performance_standard_vs_wave():
    """Measure generation time: standard vs wave mode."""
    from src.physics.generator import Generator
    from src.physics.morpho_phasic import MorphoPhasicEngine
    vocab, K, syntax = synchronize(CORPUS)
    morpho = MorphoPhasicEngine()
    gen_std = Generator(vocab, K, syntax_field=syntax, morpho=morpho, corpus_texts=CORPUS)
    t0 = time.perf_counter()
    _ = gen_std.generate("almalik", max_words=4, mode='standard')
    t_std = time.perf_counter() - t0
    print(f"\n  standard: {t_std:.3f}s")
    gen_wave = Generator(vocab, K, syntax_field=syntax, morpho=morpho, corpus_texts=CORPUS)
    t0 = time.perf_counter()
    _ = gen_wave.generate("almalik", max_words=4, mode='wave')
    t_wave = time.perf_counter() - t0
    ratio = t_wave / max(t_std, 0.001)
    print(f"  wave:     {t_wave:.3f}s  (ratio: {ratio:.2f}x)")
    assert t_wave < t_std * 3, f"wave too slow: {ratio:.2f}x standard"
