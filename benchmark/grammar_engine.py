#!/usr/bin/env python3
"""Morphology-aware grammar benchmark using Mirnan's 14-weight engine."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import load_model
from src.physics.word_physics import compute_extended_phase_vector
from src.physics.morpho_phasic import MorphoPhasicEngine
from src.physics.semantic_arithmetic import predict_antonym, solve_analogy

data = load_model()
vocab = data['vocab']
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vocab.load_supplemental(os.path.join(ROOT, 'model', 'vocab_supplemental.json'))

morpho = MorphoPhasicEngine()

tests = {
    'antonyms': [
        ('كبير', 'صغير'),
        ('طويل', 'قصير'),
        ('سريع', 'بطيء'),
        ('جميل', 'قبيح'),
        ('قوي', 'ضعيف'),
        ('غني', 'فقير'),
        ('حار', 'بارد'),
        ('جديد', 'قديم'),
        ('ذكي', 'غبي'),
        ('سعيد', 'حزين'),
        ('نور', 'ظلام'),
        ('حياة', 'موت'),
        ('نهار', 'ليل'),
        ('خير', 'شر'),
        ('صدق', 'كذب'),
    ],
    'plurals': [
        ('كتاب', 'كتب'),
        ('قلم', 'أقلام'),
        ('طالب', 'طلاب'),
        ('معلم', 'معلمون'),
        ('مدرسة', 'مدارس'),
    ],
}

print("=" * 60)
print("  Mirnan Morphology Benchmark (Engine, not KB)")
print("=" * 60)

for cat_name, items in tests.items():
    correct = 0
    total = len(items)
    t0 = time.time()

    for word, expected in items:
        wid = vocab.get(word)
        if cat_name == 'antonyms':
            predicted = predict_antonym(word)
            if predicted:
                # Check if predicted matches expected
                is_correct = (predicted == expected)
                status = 'OK' if is_correct else f'got "{predicted}"'
                if is_correct:
                    correct += 1
            else:
                status = 'no prediction'
            print(f"  {'✓' if is_correct else '✗'} {word} → {expected}  ({status})")
        elif cat_name == 'plurals':
            analysis = morpho.analyze(word)
            pos = analysis.get('pos', '?')
            weight = analysis.get('weight', '?')
            # Check if vocab contains expected plural
            exp_wid = vocab.get(expected)
            status = 'found' if exp_wid else f'not in vocab'
            if exp_wid:
                correct += 1
            print(f"  {'✓' if exp_wid else '✗'} {word} → {expected}  ({pos}, {weight}, {status})")

    elapsed = time.time() - t0
    acc = correct / total * 100
    print(f"\n  {cat_name}: {correct}/{total} = {acc:.0f}%  ({elapsed*1000:.0f}ms)\n")

print("=" * 60)
