# -*- coding: utf-8 -*-
"""
محرك المؤثرات السياقية — Contextual Operators Engine.

يكتشف الكلمات التي تعدّل العلاقة الفيزيائية بين الكلمات المتعاكسة،
مثل كلمات النفي (غياب، عدم)، التضخيم (يطغى، يشتد)، التباين (رغم، لكن)،
والشرط (إذا، لو). هذه المؤثرات تخلق جسوراً سببية بين المتضادات.

الفكرة: "عند غياب الشمس يطغى الظلام"
- "غياب" = مؤثر نفي ← يلغي متجه شمس ← يصبح قريباً من ظلام
- "يطغى" = مؤثر تضخيم ← يُقوي متجه ظلام
- النتيجة: الجملة منطقية رغم التعارض الفيزيائي بين شمس وظلام

المؤثرات تُحمّل من ملف JSON خارجي — يمكن إضافتها وتعديلها دون لمس الكود.

الاستخدام:
    engine = ContextualOperators()
    adjusted_pv = engine.apply(candidate_pv, context_words, operator_pvs)
    boost = engine.compute_boost(candidate_word, context_words)
"""

import os
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


class ContextualOperators:
    """محرك تطبيق المؤثرات السياقية على المتجهات الطورية."""

    def __init__(self, json_path=None):
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), "contextual_operators.json")
        self.operators = {}
        self._word_to_operator = {}  # word → (operator_type, strength)
        self._load(json_path)

    def _load(self, json_path):
        if not os.path.exists(json_path):
            logger.warning(f"  ⚠ مؤثرات سياقية غير موجودة: {json_path}")
            return
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ops = data.get("operators", {})
        for op_type, op_data in ops.items():
            strength = op_data.get("strength", 0.0)
            words = op_data.get("words", [])
            self.operators[op_type] = {
                "description": op_data.get("description", ""),
                "strength": strength,
                "words": set(words),
            }
            for w in words:
                self._word_to_operator[w] = (op_type, strength)
        logger.info(f"  ✓ مؤثرات سياقية: {len(self._word_to_operator)} كلمة في {len(self.operators)} نوع")

    def get_operator(self, word):
        """الاستعلام عن نوع المؤثر وقوته لكلمة معينة."""
        return self._word_to_operator.get(word)

    def has_operator(self, word):
        return word in self._word_to_operator

    def detect_chain(self, context_words):
        """كشف سلسلة المؤثرات في السياق.

        يُرجع قائمة من (word_index, word, operator_type, strength)
        لكل كلمة في السياق لها مؤثر معروف.

        مثال:
            السياق: ["عند", "غياب", "الشمس", "يطغى", "الظلام"]
            تُرجع: [(1, "غياب", "negation", -0.8), (3, "يطغى", "amplify", 1.5)]
        """
        chain = []
        for i, w in enumerate(context_words):
            op = self._word_to_operator.get(w)
            if op:
                chain.append((i, w, op[0], op[1]))
        return chain

    def apply_negation(self, pv, strength):
        """تطبيق مؤثر النفي — عكس الأبعاد المهيمنة."""
        indices = np.argsort(np.abs(pv))[::-1][:5]
        adjusted = pv.copy()
        adjusted[indices] *= (1.0 + strength)  # strength سالب ← يعكس
        norm = np.linalg.norm(adjusted)
        if norm > 1e-10:
            adjusted /= norm
        return adjusted

    def apply_amplify(self, pv, strength):
        """تطبيق مؤثر التضخيم — تقوية المتجه."""
        adjusted = pv.copy() * strength
        norm = np.linalg.norm(adjusted)
        if norm > 1e-10:
            adjusted /= norm
        return adjusted

    def apply_operator(self, pv, operator_type, strength):
        """تطبيق مؤثر واحد على متجه."""
        if operator_type == "negation":
            return self.apply_negation(pv, strength)
        elif operator_type == "amplify":
            return self.apply_amplify(pv, strength)
        elif operator_type == "contrast":
            return self.apply_negation(pv, strength * 0.5)
        elif operator_type == "conditional":
            return pv  # الشرط لا يغير المتجه — يغير المسار فقط
        return pv

    def compute_boost(self, candidate_word, context_words, vocab, pv_fn):
        """حساب تعزيز للمرشح بناءً على المؤثرات في السياق.

        افحص الكلمتين السابقتين للمرشح:
        - إذا كانت إحداهما مؤثر نفي والأخرى متعاكسة مع المرشح ← تعزيز
        - إذا كانت إحداهما مؤثر تضخيم والمرشح متوافق مع السياق ← تعزيز

        Returns:
            float: درجة التعزيز [0, 1]
        """
        if len(context_words) < 2:
            return 0.0

        boost = 0.0
        # فحص آخر كلمتين
        recent = context_words[-2:]

        for i, cw in enumerate(recent):
            op = self._word_to_operator.get(cw)
            if op is None:
                continue

            op_type, op_strength = op

            if op_type == "negation":
                # المؤثر يلغي الكلمة التي بعده — المرشح هو الذي بعد المؤثر
                # إذا كان هناك كلمة قبل المؤثر تتعارض مع المرشح ← المؤثر يصلح العلاقة
                if i == 0 and len(recent) > 1:
                    prev_word = recent[0]  # الكلمة قبل المؤثر
                    candidate_pv = pv_fn(candidate_word)
                    prev_pv = pv_fn(prev_word)
                    sim = float(np.dot(candidate_pv, prev_pv) / (
                        np.linalg.norm(candidate_pv) * np.linalg.norm(prev_pv) + 1e-10))
                    if sim < 0.1:  # تعارض فيزيائي
                        boost = abs(op_strength) * 2.0  # المؤثر يصلح التعارض

            elif op_type == "amplify":
                # المؤثر يضخم الكلمة التالية — المرشح يحصل على تعزيز
                boost = op_strength * 1.5

            elif op_type == "contrast":
                # المؤثر يضعف التعارض — تعزيز معتدل
                boost = abs(op_strength) * 1.0

            elif op_type == "conditional":
                # المؤثر ينشئ مساراً سببياً — تعزيز للمرشحات الجديدة
                boost = op_strength * 1.0

        return min(boost, 3.0)  # سقف التعزيز

    def modify_phase(self, target_pv, context_words, pv_fn, vocab):
        """تعديل المتجه المستهدف بناءً على المؤثرات في السياق.

        يفحص الكلمات بين الهدف الحالي والكلمة السابقة:
        - إذا وجد مؤثر نفي ← يعكس الطور المستهدف
        - إذا وجد مؤثر تضخيم ← يضخم الطور المستهدف

        يُستخدم عند بناء goal_concept لتوجيه الاستدلال بشكل صحيح.

        Returns:
            np.ndarray: المتجه المعدَّل
        """
        if not context_words or target_pv is None:
            return target_pv

        chain = self.detect_chain(context_words)
        modified = target_pv.copy()

        for _, _, op_type, strength in chain:
            modified = self.apply_operator(modified, op_type, strength)

        return modified
