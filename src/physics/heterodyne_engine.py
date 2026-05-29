# -*- coding: utf-8 -*-
"""Heterodyne Engine — محرك التغاير الترددي لعزل رفقاء الكلمة.

المبدأ الفيزيائي:
  - كل كلمة لها تردد ω₀ وترددات سياق (من الكلمات المحيطة).
  - بجمع وطرح ترددات السياق مع تردد الكلمة، نحصل على نطاقات جانبية (sidebands).
  - الكلمات المرافقة التي تقع تردداتها على هذه النطاقات هي الرفقاء الحقيقيون
    في هذا السياق المحدد.
  - هذا يحاكي مستقبل الراديو: التردد الحامل = تردد الكلمة،
    التضمين = السياق، النطاقات الجانبية تكشف الإشارة الحقيقية.

الاستخدام في التوليد:
  1. لكل كلمة مرشحة، نحسب نطاقاتها الجانبية من ترددات سياقها الحالي.
  2. نقارن النطاقات مع ترددات الكلمات في K-matrix.
  3. الكلمات ذات التطابق الترددي العالي مع النطاقات تحصل على وزن أكبر.
"""

import numpy as np
from src.physics.word_physics import compute_word_frequency
from src.physics.letter_db import LetterDB

_letter_db = None


def _get_db():
    global _letter_db
    if _letter_db is None:
        _letter_db = LetterDB()
    return _letter_db


class HeterodyneEngine:
    """محرك التغاير الترددي.

    يحاكي عملية كشف الراديو:
      f_carrier = ω₀ (تردد الكلمة الحامل)
      f_mod = ترددات كلمات السياق (إشارة التضمين)
      f_sidebands = f_carrier ± f_mod (النطاقات الجانبية)

    الكلمات المرافقة التي تقع تردداتها قرب النطاقات الجانبية هي
    الرفقاء النشطون في هذا السياق تحديداً.
    """

    def __init__(self, bandwidth=0.15, context_window=8):
        self.bandwidth = bandwidth
        self.context_window = context_window
        self._freq_cache = {}

    def get_word_freq(self, word):
        if word not in self._freq_cache:
            self._freq_cache[word] = compute_word_frequency(word)
        return self._freq_cache[word]

    def compute_sidebands(self, carrier_word, context_words):
        """حساب النطاقات الجانبية لكلمة حاملة ضمن سياق.

        لكل كلمة سياق، ننتج ترددين جانبيين:
          f_plus  = f_carrier + f_context
          f_minus = |f_carrier - f_context|

        Returns:
            dict: {context_word: (f_plus, f_minus, weight)}
                  weight = 1/rank — الأقرب في السياق له وزن أكبر
        """
        f_carrier = self.get_word_freq(carrier_word)
        sidebands = {}

        ctx = context_words[-self.context_window:] if context_words else []

        for rank, ctx_word in enumerate(reversed(ctx), 1):
            if ctx_word == carrier_word:
                continue
            f_ctx = self.get_word_freq(ctx_word)
            f_plus = f_carrier + f_ctx
            f_minus = abs(f_carrier - f_ctx)
            weight = 1.0 / rank
            sidebands[ctx_word] = (f_plus, f_minus, weight)

        return sidebands

    def compute_candidate_resonance(self, candidate_word, freq, sidebands):
        """حساب مدى رنين الكلمة المرشحة مع النطاقات الجانبية للسياق.

        كلما كان تردد المرشح أقرب إلى أحد النطاقات الجانبية، زادت درجة الرنين.

        Returns:
            float: درجة الرنين [0, 1]
        """
        if not sidebands:
            return 0.0

        total_resonance = 0.0
        total_weight = 0.0

        for ctx_word, (f_plus, f_minus, weight) in sidebands.items():
            dist_plus = abs(freq - f_plus) / max(f_plus, 1e-10)
            dist_minus = abs(freq - f_minus) / max(f_minus, 1e-10)
            closest = min(dist_plus, dist_minus)

            if closest < self.bandwidth:
                resonance = 1.0 - (closest / self.bandwidth)
                total_resonance += resonance * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0
        return total_resonance / total_weight

    def score_candidate(self, candidate_word, context_words):
        """تسجيل مرشح بناءً على التغاير الترددي مع السياق.

        Returns:
            float: درجة التغاير [0, ∞)
        """
        if not context_words or len(context_words) < 1:
            return 0.0

        f_cand = self.get_word_freq(candidate_word)
        sidebands = self.compute_sidebands(candidate_word, context_words)
        resonance = self.compute_candidate_resonance(candidate_word, f_cand, sidebands)
        return resonance

    def context_filter_companions(self, carrier_word, candidate_words,
                                   context_words, top_k=None):
        """فلترة الرفقاء: إرجاع الكلمات المرشحة مرتبة حسب الرنين الترددي.

        هذا هو جوهر الآلية: من بين كل الكلمات المرافقة لكلمة ما
        (حسب K-matrix)، نختار فقط تلك التي تتطابق ترددياً مع السياق الحالي.

        Args:
            carrier_word: الكلمة الحاملة
            candidate_words: قائمة الكلمات المرافقة (من K-matrix مثلاً)
            context_words: كلمات السياق الحالي
            top_k: عدد النتائج المطلوبة (None = الكل)

        Returns:
            list of (word, score): مرتبة تنازلياً حسب درجة الرنين
        """
        f_carrier = self.get_word_freq(carrier_word)
        sidebands = self.compute_sidebands(carrier_word, context_words)

        scored = []
        for cand in candidate_words:
            if cand == carrier_word:
                continue
            f_cand = self.get_word_freq(cand)
            res = self.compute_candidate_resonance(cand, f_cand, sidebands)
            if res > 0:
                scored.append((cand, res))

        scored.sort(key=lambda x: x[1], reverse=True)
        if top_k is not None:
            scored = scored[:top_k]
        return scored

    def compute_context_signature(self, context_words):
        """توقيع ترددي للسياق: مصفوفة النطاقات الجانبية لكل كلمات السياق.

        هذا يعطي "بصمة ترددية" فريدة للسياق الحالي، تمكّن من:
          - مقارنة السياقات المختلفة
          - كشف متى يتغير الموضوع (عندما تتغير البصمة الترددية)

        Returns:
            np.ndarray: (n_ctx, 2) — لكل كلمة سياق: (f_plus_avg, f_minus_avg)
        """
        if not context_words:
            return np.zeros((0, 2))

        n = min(len(context_words), self.context_window)
        ctx = context_words[-n:]
        signature = np.zeros((n, 2))

        for i, word in enumerate(ctx):
            f_word = self.get_word_freq(word)
            sidebands = self.compute_sidebands(word, ctx[:i] + ctx[i + 1:])
            if sidebands:
                plus_vals = [s[0] for s in sidebands.values()]
                minus_vals = [s[1] for s in sidebands.values()]
                signature[i, 0] = np.mean(plus_vals)
                signature[i, 1] = np.mean(minus_vals)
            else:
                signature[i, 0] = f_word
                signature[i, 1] = f_word

        return signature

    def compute_k_weighted_resonance(self, wid, context_ids, K_matrix,
                                      vocab, context_words):
        """حساب رنين مرجح بـ K-matrix للكلمة المرشحة.

        يجمع بين:
          1. قيم K-matrix (التلازم الإحصائي العالمي)
          2. الرنين الترددي (التغاير السياقي)

        بهذه الطريقة، الكلمات التي تتلازم إحصائياً مع الكلمة
        وتتناغم ترددياً مع السياق الحالي تحصل على أعلى الدرجات.

        Args:
            wid: معرف الكلمة المرشحة
            context_ids: معرفات كلمات السياق
            K_matrix: مصفوفة التلازم
            vocab: كائن المفردات
            context_words: كلمات السياق (نصاً)

        Returns:
            float: درجة مرجّحة
        """
        if K_matrix is None or not context_ids:
            return 0.0

        candidate_word = vocab.id2word.get(wid, '')
        if not candidate_word:
            return 0.0

        f_cand = self.get_word_freq(candidate_word)

        total_score = 0.0
        total_weight = 0.0

        for rank, cid in enumerate(reversed(context_ids[-self.context_window:]), 1):
            if cid is None or cid >= K_matrix.shape[0] or wid >= K_matrix.shape[1]:
                continue

            k_val = float(K_matrix[cid, wid])
            if k_val <= 0:
                continue

            ctx_word = vocab.id2word.get(cid, '')
            if not ctx_word:
                continue

            f_ctx = self.get_word_freq(ctx_word)
            f_plus = f_cand + f_ctx
            f_minus = abs(f_cand - f_ctx)

            dist_plus = abs(f_cand - f_plus) / max(f_plus, 1e-10)
            dist_minus = abs(f_cand - f_minus) / max(f_minus, 1e-10)
            closest = min(dist_plus, dist_minus)

            if closest < self.bandwidth:
                freq_match = 1.0 - (closest / self.bandwidth)
                weight = 1.0 / rank
                total_score += k_val * freq_match * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_score / total_weight

    def clear_cache(self):
        self._freq_cache.clear()
