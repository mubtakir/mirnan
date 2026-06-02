#!/usr/bin/env python3
"""Add missing reasoning-critical words to the vocabulary."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import load_model, load_model

data = load_model()
vocab = data['vocab']

needed = [
    'أوروبا', 'آسيا', 'أفريقيا', 'أمريكا', 'بخار', 'خام', 'محيط',
    'قارة', 'غليان', 'تجمد', 'تبخر', 'تكثف', 'إنجلترا', 'بريطانيا',
    'المحيط', 'القارة', 'الغليان', 'التجمد', 'التبخر', 'التكثف',
    'أوروبي', 'آسيوي', 'أفريقي', 'أمريكي', 'فرنسي', 'بريطاني', 'ياباني',
]

added = 0
already = 0
for w in needed:
    if vocab.get(w) is None:
        try:
            vocab.add(w)
            added += 1
            print(f'  + {w}')
        except Exception as e:
            print(f'  ✗ {w}: {e}')
    else:
        already += 1

print(f'\nAdded: {added}  Already present: {already}  Total: {added + already}')

# Save supplemental list
out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'supplemental_words.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump({'words': needed, 'added': added, 'already': already}, f, ensure_ascii=False, indent=2)
print(f'  Saved to: {out_path}')
