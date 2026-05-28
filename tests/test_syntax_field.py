import numpy as np
from src.physics.syntax_field import (
    _get_syntax_anchor, compute_syntax_vector, expected_syntax,
    SYNTAX_ANCHORS, SyntaxFieldCache
)
from src.physics.constants import SYNTAX_DIMS


def _l2(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-10 else v


class TestSyntaxField:
    def test_anchor_shapes(self):
        for k, v in SYNTAX_ANCHORS.items():
            assert v.shape == (SYNTAX_DIMS,), f"{k} shape is {v.shape}"

    def test_anchor_normalized(self):
        for k, v in SYNTAX_ANCHORS.items():
            u = _l2(v)
            assert abs(np.linalg.norm(u) - 1.0) < 1e-5, f"{k} not unit: {np.linalg.norm(u)}"

    def test_prep_noun_closer_than_prep_verb(self):
        prep = _l2(SYNTAX_ANCHORS["prep"])
        noun = _l2(SYNTAX_ANCHORS["noun"])
        verb = _l2(SYNTAX_ANCHORS["verb"])
        d_pn = np.linalg.norm(prep - noun)
        d_pv = np.linalg.norm(prep - verb)
        assert d_pn < d_pv, f"d(prep,noun)={d_pn:.3f} >= d(prep,verb)={d_pv:.3f}"

    def test_verb_noun_separated(self):
        verb = _l2(SYNTAX_ANCHORS["verb"])
        noun = _l2(SYNTAX_ANCHORS["noun"])
        dot = np.dot(verb, noun)
        assert dot < 0.5, f"verb·noun dot={dot:.3f} too high"

    def test_get_syntax_anchor_prep(self):
        for w in ["في", "من", "على", "إلى", "عن"]:
            a = _get_syntax_anchor(w)
            assert np.argmax(a) == 2, f"{w} not classified as prep"

    def test_get_syntax_anchor_kana(self):
        for w in ["كان", "ليس", "أصبح"]:
            a = _get_syntax_anchor(w)
            assert np.argmax(a) == 5, f"{w} not classified as kana"

    def test_get_syntax_anchor_noun(self):
        for w in ["البيت", "الكتاب", "العلم", "الماء"]:
            a = _get_syntax_anchor(w)
            assert np.argmax(a) == 1, f"{w} not classified as noun"

    def test_get_syntax_anchor_verb(self):
        for w in ["يكتب", "يذهب", "يقول", "يعمل", "يفعل"]:
            a = _get_syntax_anchor(w)
            assert np.argmax(a) == 0, f"{w} not classified as verb"

    def test_compute_syntax_vector_shape(self):
        v = compute_syntax_vector("في")
        assert len(v) == SYNTAX_DIMS

    def test_compute_syntax_vector_normalized(self):
        v = compute_syntax_vector("البيت")
        assert abs(np.linalg.norm(v) - 1.0) < 1e-5

    def test_kana_in_anchors(self):
        assert "kana" in SYNTAX_ANCHORS

    def test_all_anchors_distinct(self):
        keys = list(SYNTAX_ANCHORS.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                u = _l2(SYNTAX_ANCHORS[keys[i]])
                v = _l2(SYNTAX_ANCHORS[keys[j]])
                assert np.linalg.norm(u - v) > 0.01, f"{keys[i]} and {keys[j]} too similar"
