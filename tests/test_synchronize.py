from src.physics.synchronize import synchronize, Vocabulary


class TestVocabulary:
    def test_add_and_get(self):
        v = Vocabulary()
        v.add("كتاب")
        assert v.get("كتاب") == 0
        assert v.get("غير_موجود") is None

    def test_normalize_letters(self):
        v = Vocabulary()
        id1 = v.add("أ")
        id2 = v.add("ا")
        assert id1 == id2

    def test_id2word(self):
        v = Vocabulary()
        v.add("علم")
        assert v.id2word[0] == "علم"

    def test_len(self):
        v = Vocabulary()
        v.add("أ")
        v.add("ب")
        assert len(v) == 2
        v.add("أ")
        assert len(v) == 2

    def test_multiple_words(self):
        v = Vocabulary()
        for word in ["السلام", "عليكم", "ورحمة", "الله"]:
            v.add(word)
        assert len(v) == 4
        assert v.get("السلام") == 0


class TestSynchronize:
    def test_returns_tuple(self):
        result = synchronize(["السلام عليكم ورحمة الله وبركاته"])
        assert len(result) == 3
        vocab, K, syntax = result
        assert isinstance(K.shape[0], int)
        assert K.shape[0] == len(vocab)

    def test_vocab_grows_with_corpus(self):
        vocab, K, syntax = synchronize(["مرحبا بالعالم"])
        assert len(vocab) >= 2
        assert vocab.get("مرحبا") is not None
        assert vocab.get("بالعالم") is not None

    def test_syntax_field_observes(self):
        vocab, K, syntax = synchronize(["السلام عليكم"])
        assert syntax.transition_align is not None

    def test_empty_text_no_error(self):
        vocab, K, syntax = synchronize([""])
        assert len(vocab) == 0 or True  # should not crash

    def test_K_is_sparse(self):
        vocab, K, syntax = synchronize(["أ ب ج"])
        from scipy import sparse
        assert sparse.issparse(K)

    def test_multi_line_text(self):
        vocab, K, syntax = synchronize(["هذا سطر واحد\nوهذا سطر ثاني"])
        assert len(vocab) >= 4
