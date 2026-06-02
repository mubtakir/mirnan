#!/usr/bin/env python3
"""اختبار استخراج goal_concept — التوافق الطوري مع الكلمات المستهدفة.

1. يأخذ prompt (مثلاً "ما عاصمة اليابان")
2. يستخرج goal_concept عبر PromptConstraintField.compute_goal_concept()
3. يطبع:
   - أول 10 أبعاد للمتجه
   - تشابه جيب التمام مع كلمة "طوكيو" (الكلمة الصحيحة)
   - تشابه جيب التمام مع 3 كلمات غير مرتبطة للمقارنة

الاستخدام:
  python test_goal_concept.py
  python test_goal_concept.py "ما هي عاصمة فرنسا"
"""

import sys, os, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import load_model
from src.physics.word_physics import compute_extended_phase_vector, phase_similarity
from src.physics.prompt_constraint import PromptConstraintField


def _get_pv(word):
    return compute_extended_phase_vector(word)


def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "ما عاصمة اليابان"

    print("=" * 70)
    print("   اختبار goal_concept — استخراج هدف من prompt")
    print("=" * 70)

    # ─── تحميل المعجم ───
    print("\n[1] تحميل المعجم...")
    t0 = time.time()
    data = load_model()
    vocab = data['vocab']
    print(f"    ✓ {len(vocab):,} كلمة ({time.time()-t0:.1f}s)")

    # ─── تحليل prompt ───
    print(f"\n[2] الـ prompt:  \"{prompt}\"")
    prompt_words = prompt.split()
    prompt_tokens = []
    for w in prompt_words:
        wid = vocab.get(w)
        if wid is not None:
            prompt_tokens.append(vocab.id2word[wid])
        else:
            prompt_tokens.append(w)

    prompt_pvs = [_get_pv(w) for w in prompt_tokens]

    print(f"    الكلمات: {prompt_tokens}")
    print(f"    المتجهات: {len(prompt_pvs)} × ({len(prompt_pvs[0])}D)" if prompt_pvs else "    ✗ لا توجد كلمات صالحة")

    if not prompt_pvs:
        print("\n✗ لا توجد كلمات صالحة في الـ prompt")
        return

    # ─── استخراج goal_concept ───
    print("\n[3] استخراج goal_concept...")
    pcf = PromptConstraintField(k_spring=3.0, damping=0.15)
    goal = pcf.compute_goal_concept(prompt_pvs, alpha=0.6)

    if goal is None:
        print("    ✗ فشل الاستخراج")
        return

    print(f"    ✓ تم الاستخراج — |goal| = {np.linalg.norm(goal):.4f}")
    print(f"    الأبعاد العشرة الأولى: {np.round(goal[:10], 4)}")

    # ─── مقارنة مع كلمات محددة ───
    print("\n[4] مقارنة تشابه جيب التمام...")
    print("-" * 70)

    # قائمة كلمات للاختبار
    test_words = []

    # تحديد لغة الـ prompt
    is_arabic = any('\u0600' <= c <= '\u06ff' for c in prompt)

    if is_arabic:
        test_words = [
            ("طوكيو", "✓ الكلمة الصحيحة المتوقعة"),
            ("اليابانية", "○ مرتبطة جزئياً"),
            ("تفاحة", "✗ غير مرتبطة (فاكهة)"),
            ("سيارة", "✗ غير مرتبطة (مركبة)"),
            ("مطر", "✗ غير مرتبطة (طقس)"),
            ("اليابان", "○ مرتبطة (مذكورة في الـ prompt)"),
        ]
    else:
        test_words = [
            ("Tokyo", "✓ expected correct answer"),
            ("Japan", "○ mentioned in prompt"),
            ("apple", "✗ unrelated (fruit)"),
            ("car", "✗ unrelated (vehicle)"),
            ("rain", "✗ unrelated (weather)"),
        ]

    scores = []
    for word, label in test_words:
        wid = vocab.get(word)
        if wid is not None:
            word_pv = _get_pv(word)
            sim = phase_similarity(goal, word_pv)
            scores.append((sim, word, label))
            print(f"    cos(goal, \"{word:<12}\") = {sim:+.4f}    {label}")

    # ─── تحليل ───
    print("\n[5] تحليل...")
    if scores:
        scores.sort(key=lambda x: -x[0])
        best_word, best_sim = scores[0][1], scores[0][0]
        worst = scores[-1]
        gap = best_sim - worst[0]
        print(f"    الأعلى:  \"{best_word}\" ({best_sim:+.4f})")
        print(f"    الأدنى:  \"{worst[1]}\" ({worst[0]:+.4f})")
        print(f"    الفجوة:  {gap:.4f}")
        if gap > 0.15:
            print("    ✓ فجوة جيدة — goal_concept يميّز بين المرتبط وغير المرتبط")
        elif gap > 0.05:
            print("    ○ فجوة ضعيفة — goal_concept يحتاج ضبطاً (جرب تغيير alpha)")
        else:
            print("    ✗ لا توجد فجوة — goal_concept لا يميّز، يحتاج إعادة تصميم")
    else:
        print("    ✗ لا توجد كلمات اختبار في المعجم — أضفها أولاً")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
