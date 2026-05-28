from src.physics.symbolic_bridge import SymbolicBridge


class TestSymbolicBridge:
    def test_empty_context(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("كتاب", [])
        assert score == 0.0

    def test_negation_no_effect(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("كتاب", ["السلام"])
        assert score == 0.0

    def test_negation_positive(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("نفي", ["لا"])
        assert score > 0.0

    def test_negation_anti_negative(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("نعم", ["لا"])
        assert score < 0.0

    def test_conjunction_boost(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("كتاب", ["و"])
        assert score > 0.0

    def test_interrogative(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("لأن", ["هل"])
        assert score > 0.0

    def test_conditional(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("فإن", ["إذا"])
        assert score > 0.0

    def test_conjunction_last_word(self):
        bridge = SymbolicBridge()
        score = bridge.evaluate("بيت", ["السلام", "و"])
        assert score >= 0.05

    def test_multiple_rules_stack(self):
        bridge = SymbolicBridge()
        score_if = bridge.evaluate("فإن", ["إذا"])
        score_neg = bridge.evaluate("نفي", ["لا"])
        assert score_if > 0.0
        assert score_neg > 0.0
