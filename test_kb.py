#!/usr/bin/env python3
"""اختبار بنك المرشحات الرنّان — Holographic Knowledge Base.

يقوم بتحميل البنك، واختيار 10 حقائق عشوائية، وطباعة:
- السؤال (الفاعل)
- الجواب المتوقع (المفعول المخزن)
- الجواب المسترجع (أفضل كلمة من الاستعلام)
- نسبة الدقة في النهاية

الاستخدام:
  python test_kb.py
"""

import sys, os, random, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.physics.holographic_kb import HolographicKB, RELATION_TYPES
from model import load_model
from src.physics.word_physics import compute_extended_phase_vector


def _get_pv(word):
    return compute_extended_phase_vector(word)


def main():
    print("=" * 65)
    print("   اختبار بنك المرشحات الرنّان — Holographic KB")
    print("=" * 65)

    # ─── تحميل المعجم ───
    print("\n[1] تحميل المعجم...")
    t0 = time.time()
    data = load_model()
    vocab = data['vocab']
    print(f"    ✓ {len(vocab):,} كلمة ({time.time()-t0:.1f}s)")

    # ─── تحميل أو بناء البنك ───
    print("\n[2] تحميل/بناء بنك المرشحات...")
    kb = HolographicKB(data_dir="data")
    if kb.load():
        print(f"    ✓ تم التحميل: {kb.fact_count} حقيقة")
    else:
        print("    ⚠ البنك غير موجود — جاري البناء من النصوص...")
        corpus_paths = ["data/corpus.txt", "data/dialogue_corpus.txt"]
        texts = []
        for path in corpus_paths:
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    texts.append(f.read())
        if not texts:
            print("    ✗ لا توجد نصوص — جاري بناء بنك تجريبي...")
        kb.build_from_texts(texts if texts else [], vocab, _get_pv, max_facts=200)

    if not kb._built or kb.fact_count == 0:
        print("    ✗ البنك فارغ — لا يمكن الاختبار.")
        print("    تلميح: أضف نصوصاً إلى data/corpus.txt تحتوي على جمل مثل:")
        print('           "باريس هي عاصمة فرنسا" أو "Paris is the capital of France"')
        return

    all_banks = list(kb.banks.keys())
    print(f"    ✓ جاهز: {kb.fact_count} حقيقة في {len(all_banks)} بنكاً")
    for rt, bank in kb.banks.items():
        print(f"      - {rt}: {len(bank['keys'])} حقيقة")

    # ─── اختبار 10 حقائق عشوائية ───
    print("\n[3] اختبار 10 حقائق عشوائية...")
    print("-" * 65)

    # جمع كل الحقائق
    all_facts = []
    for rt, bank in kb.banks.items():
        for i in range(len(bank['keys'])):
            all_facts.append((
                bank['subj_words'][i],
                bank['obj_words'][i],
                rt,
                bank['keys'][i],
            ))

    if len(all_facts) < 10:
        print(f"    ⚠ عدد الحقائق ({len(all_facts)}) أقل من 10 — اختبار الكل")
        sample = all_facts
    else:
        sample = random.sample(all_facts, 10)

    correct = 0

    for idx, (subj_word, expected_word, rel_type, subj_pv) in enumerate(sample):
        print(f"\n  [{idx+1}] السؤال:  ماذا عن \"{subj_word}\"؟  (علاقة: {rel_type})")

        # استرجاع
        results = kb.query(subj_pv, rel_type=rel_type, top_k=5, sharpening=3.0)

        if results:
            top_score, top_word, top_rt = results[0]

            # البحث في قائمة النتائج عن الكلمة المتوقعة
            expected_in_results = False
            expected_rank = None
            for rank, (s, w, rt) in enumerate(results):
                if w == expected_word:
                    expected_in_results = True
                    expected_rank = rank + 1
                    break

            is_correct = (top_word == expected_word) or (expected_in_results and expected_rank <= 3)
            if is_correct:
                correct += 1
                status = "✓"
            else:
                status = "✗"

            print(f"       المتوقع:    {expected_word}")
            print(f"       المسترجع:   {top_word} (ثقة: {top_score:.4f})")
            if not is_correct:
                print(f"       كل النتائج: {', '.join(f'{w}({s:.2f})' for s,w,_ in results[:5])}")
            print(f"       النتيجة:    {status}")
        else:
            print(f"       ✗ لا توجد نتائج")

    print("\n" + "=" * 65)
    accuracy = correct / len(sample) * 100
    print(f"  الدقة: {correct}/{len(sample)} = {accuracy:.1f}%")
    if accuracy >= 90:
        print("  ✓ ممتاز! البنك جاهز للاستخدام.")
    elif accuracy >= 70:
        print("  ⚠ جيد — يحتاج مزيداً من الحقائق لتحسين الدقة.")
    else:
        print("  ✗ ضعيف — أضف المزيد من النصوص أو زِد sharpening.")
    print("=" * 65)


if __name__ == "__main__":
    main()
