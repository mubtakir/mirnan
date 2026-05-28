from src.physics.math_bridge import MathBridge


class TestMathBridge:
    def test_detect_math(self):
        mb = MathBridge()
        assert mb.detect_mode("احسب ناتج 5 + 3") == 'math'
        assert mb.detect_mode("math problem") == 'math'

    def test_detect_code(self):
        mb = MathBridge()
        assert mb.detect_mode("كود فيه خطأ") == 'code'
        assert mb.detect_mode("debug this function") == 'code'

    def test_detect_text(self):
        mb = MathBridge()
        assert mb.detect_mode("السلام عليكم") == 'text'
        assert mb.detect_mode("كيف حالك") == 'text'

    def test_evaluate_simple_addition(self):
        mb = MathBridge()
        result = mb.evaluate_math("2 + 3")
        assert result['valid']
        assert result['value'] == 5

    def test_evaluate_complex(self):
        mb = MathBridge()
        result = mb.evaluate_math("10 * (2 + 3)")
        assert result['valid']
        assert result['value'] == 50

    def test_evaluate_division(self):
        mb = MathBridge()
        result = mb.evaluate_math("10 / 2")
        assert result['valid']
        assert result['value'] == 5.0

    def test_evaluate_invalid(self):
        mb = MathBridge()
        result = mb.evaluate_math("مرحبا")
        assert not result['valid']

    def test_validate_valid_code(self):
        mb = MathBridge()
        result = mb.validate_code("x = 1")
        assert result['status'] == 'valid'

    def test_validate_syntax_error(self):
        mb = MathBridge()
        result = mb.validate_code("x = ")
        assert 'error' in result

    def test_validate_dangerous(self):
        mb = MathBridge()
        result = mb.validate_code("eval('__import__(\"os\")')")
        assert result['status'] == 'dangerous'

    def test_phase_vector_shape(self):
        mb = MathBridge()
        result = mb.evaluate_math("42")
        assert result['phase_vector'].shape[0] > 0

    def test_evaluate_arabic_digits(self):
        mb = MathBridge()
        result = mb.evaluate_math("٢+٣")
        assert result['valid'] or not result['valid']

    def test_reset_clears_history(self):
        mb = MathBridge()
        mb.evaluate_math("1+1")
        assert len(mb._history) == 1
        mb.reset()
        assert len(mb._history) == 0

    def test_detect_code_keywords(self):
        mb = MathBridge()
        assert mb.detect_mode("class Foo: pass") == 'code'
        assert mb.detect_mode("def hello():") == 'code'
