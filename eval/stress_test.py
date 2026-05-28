#!/usr/bin/env python3
"""Stress Test — اختبار إجهاد شامل لمحرك مرنان.

يقيس أداء 4 مراحل:
1. تحميل الملفات النصية من مجلد data/
2. مزامنة (synchronize) بناءً على 7+ ملفات
3. تهيئة المولد
4. التوليد بـ 3 أنماط (standard/quantum/multiverse)
5. اختبار Memory-Mapped K matrix

النتائج:
  Vocab ~14.9K, K nnz ~280K
  standard: 0.17s | quantum: 1.32s | multiverse: 2.83s
"""
import sys, io, os, time, gc, tracemalloc
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.physics.synchronize import synchronize, save_k_mmap
from src.physics.generator import Generator

CORPUS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
REPORT = []

def log(msg):
    print(msg)
    REPORT.append(msg)

def load_all_corpora():
    texts = []
    total_chars = 0
    total_tokens = 0
    for fname in sorted(os.listdir(CORPUS_DIR)):
        if fname.endswith('.txt'):
            path = os.path.join(CORPUS_DIR, fname)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            words = content.split()
            log(f"  {fname}: {len(content)} chars, {len(words)} words")
            texts.append(content)
            total_chars += len(content)
            total_tokens += len(words)
    log(f"\n  Total: {len(texts)} files, {total_chars} chars, {total_tokens} tokens")
    return texts

def stress_test():
    log("=" * 60)
    log("  STRESS TEST: mirnan QPSRA Performance Benchmark")
    log("=" * 60)

    log("\n[1/4] Loading all corpora...")
    texts = load_all_corpora()
    if not texts:
        log("  No corpus files found. Aborting.")
        return

    log("\n[2/4] Synchronization (training)...")
    gc.collect()
    t0 = time.time()
    tracemalloc.start()
    vocab, K, syntax = synchronize(texts, window=5, alpha=0.25)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    sync_time = time.time() - t0
    sync_mem_mb = peak / 1024 / 1024

    log(f"  Vocabulary: {len(vocab)} words")
    log(f"  K matrix: {K.shape}, non-zero: {K.nnz}")
    log(f"  Density: {K.nnz / (K.shape[0] * K.shape[1]) * 100:.4f}%")
    log(f"  Time: {sync_time:.2f}s")
    log(f"  Peak memory: {sync_mem_mb:.1f} MB")

    log("\n[3/4] Generator initialization...")
    t0 = time.time()
    gc.collect()
    tracemalloc.start()
    gen = Generator(vocab, K, syntax_field=syntax, seed=42)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    gen_init_time = time.time() - t0
    gen_mem_mb = peak / 1024 / 1024
    log(f"  Beam width: {gen.beam_width}, Top-K: {gen.top_k}")
    log(f"  PV matrix: {gen._all_pv.shape}")
    log(f"  RAM attractors: {gen.ram.size}")
    log(f"  Time: {gen_init_time:.2f}s")
    log(f"  Peak memory: {gen_mem_mb:.1f} MB")

    log("\n[4/4] Generation modes benchmark...")
    prompts = ["السلام", "العلم", "في", "كيف", "الرجل"]
    results = {}
    for mode in ['standard', 'quantum', 'multiverse']:
        times = []
        outputs = []
        for prompt in prompts:
            t0 = time.time()
            result = gen.generate(prompt, max_words=8, mode=mode)
            elapsed = time.time() - t0
            times.append(elapsed)
            outputs.append((prompt, result, elapsed))
        avg_time = sum(times) / len(times)
        log(f"\n  Mode '{mode}':")
        log(f"    Average time: {avg_time:.3f}s")
        log(f"    Total time: {sum(times):.3f}s")
        for prompt, result, elapsed in outputs:
            result_preview = (result[:60] + '...') if len(result) > 60 else result
            log(f"    [{elapsed:.3f}s] '{prompt}' -> '{result_preview}'")
        results[mode] = {'avg_time': avg_time, 'total_time': sum(times)}

    log("\n[5/4] Memory-mapped K matrix test...")
    mmap_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'mmap_test')
    os.makedirs(mmap_dir, exist_ok=True)
    base_path = os.path.join(mmap_dir, 'K')
    t0 = time.time()
    save_k_mmap(K, base_path)
    save_time = time.time() - t0
    files_size = sum(os.path.getsize(os.path.join(mmap_dir, f)) for f in os.listdir(mmap_dir) if os.path.isfile(os.path.join(mmap_dir, f)))
    log(f"  Save time: {save_time:.3f}s")
    log(f"  Files size: {files_size / 1024:.1f} KB")

    from src.physics.synchronize import load_k_mmap
    t0 = time.time()
    K_loaded = load_k_mmap(base_path)
    load_time = time.time() - t0
    log(f"  Load time: {load_time:.3f}s")
    log(f"  Shape match: {K_loaded.shape == K.shape}")
    log(f"  Non-zero match: {K_loaded.nnz == K.nnz}")

    import shutil
    del K_loaded
    gc.collect()
    shutil.rmtree(mmap_dir)

    log("\n" + "=" * 60)
    log("  STRESS TEST SUMMARY")
    log("=" * 60)
    log(f"  Vocabulary size:     {len(vocab)}")
    log(f"  K matrix entries:     {K.nnz}")
    log(f"  K density:            {K.nnz / (K.shape[0] * K.shape[1]) * 100:.4f}%")
    log(f"  Sync time:            {sync_time:.2f}s")
    log(f"  Sync peak memory:     {sync_mem_mb:.1f} MB")
    log(f"  Generator init time:  {gen_init_time:.2f}s")
    log(f"  Generator peak mem:   {gen_mem_mb:.1f} MB")
    for mode, r in results.items():
        log(f"  Generation '{mode}':     avg {r['avg_time']:.3f}s, total {r['total_time']:.3f}s")
    log("=" * 60)

if __name__ == '__main__':
    stress_test()
