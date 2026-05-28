#!/usr/bin/env python3
"""Test that get_physics_report returns correct metadata through the generation pipeline."""
import sys, os, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.physics.synchronize import synchronize
from src.physics.generator import Generator

texts = ["الرجل العظيم يبني مجداً في العصر الذهبي. الطبيب يعالج المريض في المستشفى. العلم نور يضيء طريق البشرية نحو المستقبل."]
vocab, K, syntax = synchronize(texts, window=5)
gen = Generator(vocab, K, syntax_field=syntax, beta=2.0)

# 1. Test physics metadata from generate — use word from vocab
prompt = "العلم"  # this word is in the training corpus
result = gen.generate(prompt, max_words=6, mode="standard")
print(f"Prompt: '{prompt}' -> result: '{result}'")
report = gen.get_physics_report(prompt, result)
print(f"Report keys: {list(report.keys())}")
print("=== Physics Metadata ===")
print(f"word_masses keys: {list(report['word_masses'].keys())}")
print(f"phase_angles: {report['phase_angles']}")
print(f"alignments: {report['alignments']}")
print(f"morph_weights: {report['morph_weights']}")
print(f"ram_size: {report['ram_size']}")
print(f"vocab_size: {report['vocab_size']}")
print(f"top_k: {report['top_k'][:5]}")
assert isinstance(report['word_masses'], dict), "word_masses must be dict"
assert isinstance(report['phase_angles'], list), "phase_angles must be list"
assert isinstance(report['alignments'], list), "alignments must be list"
assert isinstance(report['morph_weights'], dict), "morph_weights must be dict"
assert report['ram_size'] >= 0, "ram_size must be non-negative"
assert report['vocab_size'] >= 0, "vocab_size must be non-negative"
assert len(report['top_k']) > 0, "top_k must not be empty"
print("\n✓ Physics metadata tests passed")

# 2. Test weight resonance on/off comparison
gen2 = Generator(vocab, K, syntax_field=syntax, beta=2.0)
# Temporarily disable weight_resonance by overriding its weight
gen2.W['weight_resonance'] = 0.0

result_without = gen2.generate(prompt, max_words=4, mode="standard")
gen2.W['weight_resonance'] = 2.0  # Boost it
result_with = gen2.generate(prompt, max_words=4, mode="standard")
gen2.W['weight_resonance'] = 1.20  # Restore default

print("\n=== Weight Resonance Comparison ===")
print(f"Without (weight=0): '{result_without}'")
print(f"With (weight=2.0):  '{result_with}'")
print(f"Different: {result_without != result_with}")

# 3. Profile multiverse mode bottleneck
print("\n=== Multiverse Mode Profiler ===")
for word in ["العلم", "في", "الرجل"]:
    t0 = time.perf_counter()
    r = gen.generate(word, max_words=6, mode="multiverse")
    t = time.perf_counter() - t0
    tokens = len(r.split())
    print(f"  '{word}': {t:.3f}s, {tokens} tokens, {t/max(tokens,1):.3f}s/token")

print("\n✓ All tests completed successfully")
