#!/usr/bin/env python3
"""Diagnostic: trace KB injection in the reasoner."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import load_model
from src.physics.generator import Generator, load_config
from src.physics.path_integral_reasoner import PhasePathIntegralReasoner
from src.physics.holographic_kb import HolographicKB
from src.physics.word_physics import compute_extended_phase_vector, compute_word_mass

data = load_model()
vocab = data['vocab']
vocab.load_supplemental(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', 'vocab_supplemental.json'))

kb = HolographicKB(data_dir="data")
if os.path.exists("data/holographic_kb.npz"):
    os.remove("data/holographic_kb.npz")
pv_fn = lambda w: compute_extended_phase_vector(w)
kb.load_curated_facts("data/facts_minimal.json", vocab, pv_fn)

# Check KB queries
for w in ['الثلج','ماء','بخار','باريس','فرنسا','سكين','السكين','معدن','خام','جبال']:
    r = kb.query_by_word(w)
    print(f"  KB[{w}]: {r}")

print()

# Minimal gen
gen = Generator.__new__(Generator)
gen.config = {'goal_gravity_weight':0.3,'reasoning':{'beam_width':10,'max_depth':8,'min_depth':2,'convergence_threshold':0.75}}
gen.vocab = vocab
gen.V = len(vocab)
gen.old_semantic_dim = 36
gen.beta = 2.0; gen.current_tau = 1.0; gen.W = {}
gen.beamformer = None
gen.ram = type('obj',(object,),{'size':0})()
gen.entropy = type('obj',(object,),{'k_B':0.1,'S_crit':1.0,'compute_S':lambda s,t:0.0,'evaluate':lambda a,b,c,d:(0.1,2.0,None)})()
gen.phase_reinforcement = type('obj',(object,),{'apply':lambda s,w,pv:pv,'reinforce_sentence':lambda *a,**kw:None})()
gen.top_k = 500
gen._get_pv_fast = lambda w: gen._all_pv[vocab.word2id[w]] if w in vocab.word2id else pv_fn(w)
gen._dyn_mass = lambda w: min(float(compute_word_mass(w)), 5.0)
from src.physics.prompt_constraint import PromptConstraintField
gen.prompt_constraint = PromptConstraintField(k_spring=3.0,damping=0.15)
gen.holographic_kb = kb
cache_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', '_all_pv_cache.npy')
orig = np.load(cache_path)
gen._all_pv = np.zeros((gen.V, orig.shape[1]))
gen._all_pv[:orig.shape[0]] = orig
for i in range(orig.shape[0], gen.V):
    w = vocab.id2word.get(i)
    if w: gen._all_pv[i] = pv_fn(w)
gen._precomputed_masses = {}
for i in range(min(gen.V,20000)):
    w = vocab.id2word.get(i)
    if w: gen._precomputed_masses[w] = min(float(compute_word_mass(w)),5.0)
for rt,bank in kb.banks.items():
    for w in bank['subj_words']+bank['obj_words']:
        if w and w not in gen._precomputed_masses:
            gen._precomputed_masses[w] = min(float(compute_word_mass(w)),5.0)
gen._dyn_mass = lambda w: gen._precomputed_masses.get(w,1.0)

reasoner = PhasePathIntegralReasoner(gen)

prompt = 'السكين مصنوع من معدن. المعدن يستخرج من خام. الخام يوجد في جبال. من أين يأتي السكين'
tokens = []
for w in prompt.split():
    wc = w.strip('.,;:!?()[]{}""')
    wid = vocab.get(wc)
    if wid is not None:
        tokens.append(vocab.id2word[wid])
print(f'Tokens: {tokens}')
print(f'Tokens[-6:]: {tokens[-6:]}')
pv = [gen._get_pv_fast(w) for w in tokens]

# Trace the reasoner manually
goal = gen.prompt_constraint.compute_goal_concept(pv, holographic_kb=kb)
print(f'Goal norm: {np.linalg.norm(goal):.3f}')

# Smart start
start_word = tokens[-1]
for token in tokens:
    r = kb.query_by_word(token, top_k=1)
    if r:
        start_word = token
        print(f'Start word: {start_word} (KB match)')
        break

# Step 1: candidate injection
path = [start_word]
curr_pv = gen._get_pv_fast(start_word)
used = set(tokens)
all_context_words = list(tokens)

injected = set()
for cw in tokens[-6:] + [path[-1]]:
    kb_results = kb.query_by_word(cw, top_k=4)
    for _, obj_word, _ in kb_results:
        if obj_word and obj_word not in used:
            if obj_word in gen.vocab.word2id:
                injected.add(obj_word)
                print(f'  Injected from {cw}: {obj_word}')
print(f'Injected words: {injected}')

if injected:
    candidates = list(injected)
    print(f'Candidates: {candidates}')
    for w in candidates:
        wpv = gen._get_pv_fast(w)
        wm = gen._dyn_mass(w)
        cm = np.mean([gen._dyn_mass(cw) for cw in tokens[-5:] + [start_word]])
        rl = np.linalg.norm(wpv - curr_pv) + 1e-10
        fl = wm * cm / rl**2 * max(0, float(np.dot(wpv, curr_pv)/(np.linalg.norm(wpv)*np.linalg.norm(curr_pv)+1e-10)))
        rg = np.linalg.norm(wpv - goal) + 1e-10
        fg = wm / rg**2
        combined = fl + 0.3 * fg + 10.0
        print(f'  {w}: F_local={fl:.3f} F_goal={fg:.3f} combined={combined:.3f}')
else:
    print('  NO KB MATCHES — falling back to gravity')
