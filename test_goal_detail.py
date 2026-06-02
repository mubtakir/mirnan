#!/usr/bin/env python3
"""Detailed goal concept test with multiple prompts."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_model
from src.physics.word_physics import compute_extended_phase_vector, phase_similarity
from src.physics.prompt_constraint import PromptConstraintField

data = load_model()
vocab = data['vocab']

# Add missing words
for w in ['capital','japan','tokyo','paris','france','city','country','question','briefly']:
    try: vocab.add(w)
    except: pass
for w in ['طوكيو','باريس','اليابان','عاصمة']:
    try: vocab.add(w)
    except: pass

def get_pv(w):
    return compute_extended_phase_vector(w)

pcf = PromptConstraintField(k_spring=3.0, damping=0.15)

prompts = [
    ('AR 3-word',  'ما عاصمة اليابان'),
    ('AR 7-word',  'ما هي عاصمة اليابان أجب بإيجاز من فضلك'),
    ('EN 3-word',  'what capital japan'),
    ('EN 8-word',  'what is the capital of japan answer briefly please'),
]

for label, prompt in prompts:
    is_arabic = any('\u0600' <= c <= '\u06ff' for c in prompt)
    words = prompt.split()
    pvs = [get_pv(w) for w in words]
    goal = pcf.compute_goal_concept(pvs)
    print(f'\n[{label}] "{prompt}" ({len(words)} words)')
    print(f'  Goal norm: {np.linalg.norm(goal):.4f}')

    if is_arabic:
        targets = [('طوكيو','capital'),('باريس','wrong'),('تفاحة','fruit'),('سيارة','car'),('مطر','weather')]
    else:
        targets = [('tokyo','capital'),('paris','wrong'),('apple','fruit'),('car','vehicle'),('rain','weather')]
        for t,_ in targets:
            try: vocab.add(t)
            except: pass

    scores = []
    for w, label2 in targets:
        wid = vocab.get(w)
        if wid is not None:
            pv = get_pv(w)
            if np.linalg.norm(pv) > 0.01:
                sim = phase_similarity(goal, pv)
                scores.append((sim, w, label2))
    scores.sort(key=lambda x: -x[0])
    if len(scores) >= 2:
        gap = scores[0][0] - scores[-1][0]
        print(f'  Top: {scores[0][1]:8s} ({scores[0][0]:+.4f})  Worst: {scores[-1][1]:8s} ({scores[-1][0]:+.4f})  Gap: {gap:+.4f}')
        for s, w, lbl in scores:
            print(f'    {w:8s} {s:+.4f}  ({lbl})')
    else:
        print('  Not enough valid targets')
