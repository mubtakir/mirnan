#!/usr/bin/env python3
"""تنظيف معجم مرنان — إزالة الرموز والإيموجي والعلامات الصرفية.

يحتفظ فقط بالكلمات التي:
1. تحتوي على حرف عربي أو لاتيني واحد على الأقل
2. لا تبدأ برقم (علامات تحليل صرفي)
3. طولها بين 2 و 20 حرفاً
4. لا تحتوي على تتابعات متكررة (> 4 أحرف متطابقة)

يُنتج:
- model/vocab_clean.json: معجم نظيف مع الأرقام التسلسلية
- إحصائيات عن الكلمات المحذوفة والمحتفظ بها

الاستخدام:
  python scripts/clean_vocab.py
"""

import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import load_model


def is_valid_word(word: str) -> bool:
    """التحقق من صلاحية الكلمة للاحتفاظ بها."""
    if not word or not isinstance(word, str):
        return False

    # 1. الطول بين 2 و 20
    if len(word) < 2 or len(word) > 20:
        return False

    # 2. تحتوي على حرف عربي أو لاتيني
    has_arabic = any('\u0600' <= c <= '\u06ff' for c in word)
    has_latin = any('a' <= c.lower() <= 'z' for c in word)
    if not (has_arabic or has_latin):
        return False

    # 3. لا تبدأ برقم (علامات التحليل الصرفي مثل "1234مذكررفع")
    if word[0].isdigit():
        return False

    # 4. لا تحتوي على تتابعات متكررة مفرطة (إيموجي مكرر)
    #    أي حرف يتكرر أكثر من 4 مرات متتالية
    if re.search(r'(.)\1{4,}', word):
        return False

    # 5. لا تحتوي على رموز برمجية بحتة (> 3 رموز غير أبجدية)
    non_alpha = sum(1 for c in word if not c.isalpha())
    if non_alpha > 3 and len(word) <= 6:
        return False

    return True


def main():
    print("=" * 60)
    print("  معجم نظيف — Clean Vocabulary Generator")
    print("=" * 60)

    # ─── تحميل المعجم الأصلي ───
    print("\n[1] تحميل المعجم الأصلي...")
    data = load_model()
    vocab = data['vocab']
    original_count = len(vocab)
    print(f"    ✓ {original_count:,} كلمة")

    # ─── تصنيف وتحليل ───
    words = list(vocab.word2id.items())  # (word, id) pairs
    kept = []
    removed = {'short': [], 'symbol': [], 'digit': [], 'repeated': [], 'no_letters': []}

    for word, wid in words:
        if is_valid_word(word):
            kept.append((word, wid))
        else:
            if len(word) < 2:
                removed['short'].append(word)
            elif word and word[0].isdigit():
                removed['digit'].append(word)
            elif not any(('\u0600' <= c <= '\u06ff') or ('a' <= c.lower() <= 'z') for c in word):
                removed['symbol'].append(word)
            elif re.search(r'(.)\1{4,}', word):
                removed['repeated'].append(word)
            else:
                removed['no_letters'].append(word)

    # ─── إحصائيات ───
    print(f"\n[2] نتائج التصفية:")
    print(f"    المحتفظ بها:  {len(kept):,} ({len(kept)/original_count*100:.1f}%)")
    print(f"    المحذوفة:     {original_count - len(kept):,}")
    for cat, items in removed.items():
        if items:
            print(f"      - {cat}: {len(items):,}  مثال: {items[:3]}")

    # ─── حفظ المعجم النظيف ───
    print(f"\n[3] حفظ المعجم النظيف...")
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "model", "vocab_clean.json"
    )

    clean_vocab = {}
    for i, (word, _) in enumerate(kept):
        clean_vocab[word] = i

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "word2id": clean_vocab,
            "next_id": len(kept),
            "original_count": original_count,
            "filtered_count": len(kept),
            "kept": len(kept),
            "removed": len(removed),
        }, f, ensure_ascii=False, indent=2)

    print(f"    ✓ محفوظ: {output_path}")
    print(f"    ✓ {len(kept):,} كلمة (من أصل {original_count:,})")

    # ─── عينة ───
    print(f"\n[4] عينة من الكلمات المحتفظ بها (20 عشوائية):")
    import random
    sample = random.sample(kept, min(20, len(kept)))
    for word, _ in sample[:10]:
        lang = "EN" if any('a' <= c.lower() <= 'z' for c in word) else "AR"
        print(f"    [{lang}] {word}")
    if len(sample) > 10:
        print(f"    ... و {len(sample)-10} أخرى")

    print(f"\n[5] عينة من الكلمات المحذوفة:")
    for cat, items in removed.items():
        if items:
            print(f"    {cat}: {items[:5]}")

    print("\n" + "=" * 60)
    print("  ✓ اكتمل التنظيف")
    print("=" * 60)


if __name__ == "__main__":
    main()
