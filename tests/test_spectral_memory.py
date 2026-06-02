import numpy as np
from src.physics.spectral_memory import GlobalSpectralMemory, build_contexts_map
from src.physics.synchronize import Vocabulary
from src.physics.constants import TOTAL_DIM


def _make_vocab():
    v = Vocabulary()
    for w in ["الملك", "حكم", "البلاد", "الملكة", "حكمت", "المملكة"]:
        v.add(w)
    return v


def test_build_contexts_map_shape():
    v = _make_vocab()
    cm = build_contexts_map(["الملك حكم البلاد", "الملكة حكمت المملكة"], v, half_window=3)
    assert len(cm) > 0
    for wid, vecs in cm.items():
        assert len(vecs) >= 1
        assert vecs[0].shape[0] == TOTAL_DIM


def test_global_signatures_empty():
    gsm = GlobalSpectralMemory(data_dir='data')
    gsm.build_global_signatures(_make_vocab(), {})
    assert len(gsm.gss_cache) == 0
    assert gsm.is_loaded is True


def test_global_resonance_zero_for_unknown():
    gsm = GlobalSpectralMemory(data_dir='data')
    gsm.gss_cache = {1: np.ones(TOTAL_DIM)}
    gsm.is_loaded = True
    res = gsm.get_global_resonance(999, np.ones(TOTAL_DIM))
    assert res == 0.0


def test_global_resonance_same_vector():
    gsm = GlobalSpectralMemory(data_dir='data')
    vec = np.ones(TOTAL_DIM) / np.linalg.norm(np.ones(TOTAL_DIM))
    gsm.gss_cache = {1: vec}
    gsm.is_loaded = True
    res = gsm.get_global_resonance(1, vec)
    assert res > 0.5


def test_phase_opposition_contradiction():
    from src.physics.pragmatic_field import PragmaticBindingEngine
    eng = PragmaticBindingEngine()
    # diff ≈ π/2 → |cos| ≈ 0 → contradiction score -1.0
    w_pv = np.zeros(TOTAL_DIM)
    ctx_pvs = [np.ones(TOTAL_DIM) * (np.pi / 2)]
    score = eng.phase_opposition_score(w_pv, ctx_pvs)
    assert score == -1.0


def test_phase_opposition_alignment():
    from src.physics.pragmatic_field import PragmaticBindingEngine
    eng = PragmaticBindingEngine()
    w_pv = np.ones(TOTAL_DIM)
    ctx_pvs = [np.ones(TOTAL_DIM)]
    score = eng.phase_opposition_score(w_pv, ctx_pvs)
    assert score == 0.5


def test_phase_opposition_neutral():
    from src.physics.pragmatic_field import PragmaticBindingEngine
    eng = PragmaticBindingEngine()
    # diff ≈ 1.0 → |cos| ≈ 0.54 → between 0.15 and 0.7 → neutral (0.0)
    w_pv = np.zeros(TOTAL_DIM)
    ctx_pvs = [np.ones(TOTAL_DIM) * 1.0]
    score = eng.phase_opposition_score(w_pv, ctx_pvs)
    assert score == 0.0


def test_phase_opposition_empty():
    from src.physics.pragmatic_field import PragmaticBindingEngine
    eng = PragmaticBindingEngine()
    assert eng.phase_opposition_score(None, []) == 0.0
    assert eng.phase_opposition_score(np.ones(10), []) == 0.0


def test_causal_engine_build():
    from src.physics.causal_engine import CausalPhaseEngine
    from src.physics.synchronize import Vocabulary
    v = Vocabulary()
    for w in ["السبب", "النتيجة", "إذا"]:
        v.add(w)
    eng = CausalPhaseEngine()
    eng.build_from_corpus(["السبب يؤدي إلى النتيجة إذا", "إذا كان السبب فالنتيجة"], v)
    assert eng.is_built
    assert eng.causal_K is not None


def test_causal_strength():
    from src.physics.causal_engine import CausalPhaseEngine
    import numpy as np
    from scipy import sparse
    eng = CausalPhaseEngine()
    V = 3
    rows, cols, data = [0, 1], [1, 2], [0.8, 0.6]
    eng.causal_K = sparse.csr_matrix((data, (rows, cols)), shape=(V, V))
    eng.is_built = True
    assert eng.causal_strength(0, 1) == 0.8
    assert eng.causal_strength(1, 0) == 0.0
    assert eng.causal_strength(999, 0) == 0.0


def test_transitive_score():
    from src.physics.causal_engine import CausalPhaseEngine
    import numpy as np
    from scipy import sparse
    eng = CausalPhaseEngine()
    V = 5
    # 0→1, 1→2, AND 0→2 (transitive closure)
    rows, cols, data = [0, 1, 0], [1, 2, 2], [0.8, 0.7, 0.5]
    eng.causal_K = sparse.csr_matrix((data, (rows, cols)), shape=(V, V))
    eng.is_built = True
    score = eng.transitive_score([0, 1, 2])
    assert score > 0


def test_causal_score_candidate():
    from src.physics.causal_engine import CausalPhaseEngine
    import numpy as np
    from scipy import sparse
    eng = CausalPhaseEngine()
    V = 5
    rows, cols, data = [0, 1], [2, 2], [0.7, 0.6]
    eng.causal_K = sparse.csr_matrix((data, (rows, cols)), shape=(V, V))
    eng.is_built = True
    # context [0,1] both cause 2 → positive score
    score = eng.score_candidate(2, [0, 1])
    assert score > 0
    # unknown word → 0
    score = eng.score_candidate(4, [0])
    assert score == 0.0


def test_assimilate_text():
    from src.physics.synchronize import synchronize, assimilate_text
    vocab, K1, _ = synchronize(["الملك حكم البلاد"])
    v2, K2, _ = synchronize(["الملكة حكمت المملكة"], vocab=vocab)
    K_mixed = assimilate_text(["الملكة حكمت المملكة"], vocab, K1, window=5, alpha_blend=0.3)
    assert K_mixed.shape[0] == len(vocab)
    assert K_mixed.shape[1] == len(vocab)


def test_resonant_chain_pair_freq():
    from src.physics.resonant_chain import ResonantChain
    import numpy as np
    rc = ResonantChain()
    pv_a = np.ones(TOTAL_DIM) / np.linalg.norm(np.ones(TOTAL_DIM))
    pv_b = pv_a.copy()
    f = rc.pair_freq(1.0, 1.0, pv_a, pv_b)
    assert f > 0


def test_resonant_chain_coherence():
    from src.physics.resonant_chain import ResonantChain
    import numpy as np
    rc = ResonantChain()
    v = np.ones(TOTAL_DIM) / np.linalg.norm(np.ones(TOTAL_DIM))
    masses = [1.0, 1.0, 1.0]
    pvs = [v, v, v]
    c = rc.sentence_coherence(masses, pvs)
    assert c > 0.9


def test_resonant_chain_score_candidate():
    from src.physics.resonant_chain import ResonantChain
    import numpy as np
    rc = ResonantChain()
    v = np.ones(TOTAL_DIM) / np.linalg.norm(np.ones(TOTAL_DIM))
    prev_freqs = [0.5, 0.52, 0.49]
    score = rc.score_candidate(1.0, 1.0, v, v, prev_freqs)
    assert score > 0


def test_resonant_chain_bad_pair():
    from src.physics.resonant_chain import ResonantChain
    import numpy as np
    rc = ResonantChain()
    v1 = np.ones(TOTAL_DIM) / np.linalg.norm(np.ones(TOTAL_DIM))
    v2 = -v1.copy()
    f = rc.pair_freq(1.0, 999.0, v1, v2)
    assert f > 0
    assert np.isfinite(f)


def test_noun_boost():
    from src.physics.synchronize import synchronize
    from src.physics.generator import Generator
    vocab, K, syntax = synchronize(["الملك حكم البلاد", "السماء زرقاء"])
    gen = Generator(vocab, K, syntax_field=syntax)
    b1 = gen._noun_boost("الملك")
    assert b1 in (1.0, 1.5)
    with_boost = gen._dyn_mass("الملك")
    assert with_boost > 0
