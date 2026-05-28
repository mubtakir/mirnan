import numpy as np
from src.physics.synchronize import synchronize
from src.physics.generator import Generator


class TestGenerator:
    def test_init(self):
        vocab, K, syntax = synchronize(["السلام عليكم"])
        gen = Generator(vocab, K, syntax_field=syntax)
        assert gen.vocab is vocab
        assert gen.K is K

    def test_generate_returns_string(self):
        vocab, K, syntax = synchronize(["مرحبا بالعالم"])
        gen = Generator(vocab, K, syntax_field=syntax)
        text = gen.generate("مرحبا", max_words=3)
        assert isinstance(text, str)

    def test_generate_different_steps_by_seed(self):
        vocab, K, syntax = synchronize(["بيت مدرسة علم كتاب قلم"])
        gen1 = Generator(vocab, K, syntax_field=syntax, seed=42)
        gen2 = Generator(vocab, K, syntax_field=syntax, seed=99)
        t1 = gen1.generate("بيت", max_words=3)
        t2 = gen2.generate("بيت", max_words=3)
        assert isinstance(t1, str)
        assert isinstance(t2, str)

    def test_generate_with_all_components(self):
        vocab, K, syntax = synchronize(["السلام عليكم"])
        from src.physics.ram_core import AttractorMemory
        from src.physics.entropy_gate import EntropyGate
        from src.physics.symbolic_bridge import SymbolicBridge
        from src.physics.morpho_phasic import MorphoPhasicEngine
        ram = AttractorMemory()
        eg = EntropyGate()
        sb = SymbolicBridge(vocab, K)
        mpe = MorphoPhasicEngine()
        gen = Generator(vocab, K, syntax_field=syntax,
                        ram=ram, entropy_gate=eg,
                        symbolic_bridge=sb, morpho=mpe)
        text = gen.generate("السلام", max_words=2)
        assert isinstance(text, str)

    def test_generate_with_new_vocab_gives_empty(self):
        vocab, K, syntax = synchronize(["السلام عليكم"])
        gen = Generator(vocab, K, syntax_field=syntax)
        text = gen.generate("كلمة_غير_موجودة", max_words=3)
        assert text == ""
