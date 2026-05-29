# -*- coding: utf-8 -*-
import numpy as np
from src.physics.density_matrix import QuantumDensityMatrix
from src.physics.causal_flow import CausalFlowField
from src.physics.synchronize import synchronize
from src.physics.generator import Generator
from src.physics.causal_engine import CausalPhaseEngine


class TestV8Features:
    def test_density_matrix_basic(self):
        # 1. Initialize density matrix
        dm = QuantumDensityMatrix(dim=64, decay_rate=0.8)
        
        # 2. Build from empty list
        rho_empty = dm.build([])
        assert rho_empty.shape == (64, 64)
        assert np.allclose(rho_empty, 0.0)
        assert dm.get_trace() == 0.0
        assert dm.get_purity() == 0.0
        assert dm.get_entanglement_entropy() == 0.0
        
        # 3. Build from a set of dummy phase vectors
        pvs = [np.random.randn(64) for _ in range(5)]
        rho = dm.build(pvs)
        assert rho.shape == (64, 64)
        assert dm.n_words == 5
        
        # Trace of density matrix should be approximately 1.0 (since vectors are normalized)
        assert abs(dm.get_trace() - 1.0) < 1e-9
        
        # Purity should be between 0 and 1.0
        purity = dm.get_purity()
        assert 0.0 < purity <= 1.0
        
        # Entropy should be non-negative
        entropy = dm.get_entanglement_entropy()
        assert entropy >= 0.0
        
        # Resonance with a candidate
        candidate = np.random.randn(64)
        res = dm.resonance(candidate)
        assert 0.0 <= res <= 1.0
        
        # Dominant context
        dominant = dm.dominant_context(pvs, top_k=2)
        assert len(dominant) <= 2
        assert dominant[0][0] >= dominant[1][0]

    def test_causal_flow_basic(self):
        # Setup dummy causal engine
        vocab, K, syntax = synchronize(["علم كشف دراسة"])
        causal_engine = CausalPhaseEngine()
        causal_engine.build_from_corpus(["علم كشف دراسة"], vocab)
        
        flow_field = CausalFlowField(causal_engine=causal_engine, dim=64, flow_strength=1.0)
        
        current_pv = np.random.randn(64)
        context_pvs = [np.random.randn(64) for _ in range(3)]
        context_ids = [0, 1, 2]
        
        # Compute flow without word_to_pv_fn
        flow = flow_field.compute_flow(current_pv, context_pvs, context_ids, vocab)
        assert 'flow_vector' in flow
        assert flow['flow_vector'].shape == (64,)
        assert 0.0 <= flow['logical_score'] <= 1.0
        
        # Compute flow with word_to_pv_fn
        dummy_pv = np.ones(64) * 0.1
        flow_with_fn = flow_field.compute_flow(
            current_pv, context_pvs, context_ids, vocab,
            word_to_pv_fn=lambda w: dummy_pv
        )
        assert 'flow_vector' in flow_with_fn
        assert flow_with_fn['flow_vector'].shape == (64,)
        
        # Flow alignment score
        candidate = np.random.randn(64)
        align = flow_field.flow_alignment_score(candidate, current_pv, flow['flow_vector'])
        assert 0.0 <= align <= 1.0
        
        # Transitive flow
        trans = flow_field.compute_transitive_flow([0, 1, 2], vocab)
        assert 'flow_strength' in trans

    def test_generator_v8_integration(self):
        vocab, K, syntax = synchronize(["السلام عليكم ورحمة الله وبركاته"])
        gen = Generator(vocab, K, syntax_field=syntax)
        
        # Verify V8 components are initialized
        assert isinstance(gen.density_matrix, QuantumDensityMatrix)
        assert isinstance(gen.causal_flow, CausalFlowField)
        
        # Test partonic resonance helper
        w_pv = np.random.randn(64)
        ctx_pvs = [np.random.randn(64) for _ in range(3)]
        partonic = gen._partonic_resonance(w_pv, ctx_pvs)
        assert 'core_sim' in partonic
        assert 'sem_sim' in partonic
        assert 'cross_coherence' in partonic
        assert 0.0 <= partonic['cross_coherence'] <= 1.0
        
        # Test density matrix helper
        res = gen._density_resonance(ctx_pvs, w_pv)
        assert 0.0 <= res <= 1.0
        
        # Test causal flow helper
        c_flow_align = gen._causal_flow_alignment(w_pv, w_pv, [0, 1], ctx_pvs[:2])
        assert 0.0 <= c_flow_align <= 1.0
        
        # Test hierarchical modulation helper
        h_mod = gen._hierarchical_modulation(w_pv)
        assert 0.0 <= h_mod <= 1.0

    def test_string_to_token_list_conversion(self):
        vocab, K, syntax = synchronize(["السلام عليكم ورحمة الله وبركاته"])
        gen = Generator(vocab, K, syntax_field=syntax)
        
        # Test passing string directly to generator methods instead of list of tokens
        q_res = gen._quantum_generate("السلام عليكم", max_words=2)
        assert isinstance(q_res, str)
        
        m_res = gen._multiverse_generate("السلام عليكم", max_words=2)
        assert isinstance(m_res, str)
        
        w_res = gen._wave_generate("السلام عليكم", max_words=2)
        assert isinstance(w_res, str)
        
        p_res = gen._poetic_generate("السلام عليكم", max_words=2, meter='kamil')
        assert isinstance(p_res, str)

