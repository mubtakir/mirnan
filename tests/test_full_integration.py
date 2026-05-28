"""اختبار تكاملي شامل — كل شيء معاً.

يختبر:
1. محلل الكلمات (letter meanings + articulation)
2. PhysicsTranslator (ترجمة عبر sidebands ثنائي اللغة)
3. Wave mode generation (توليد إنجليزي)
4. جميع الاختبارات السابقة لا تتراجع
"""
import sys, os, json, time
import numpy as np

from src.physics.word_physics import (
    compute_word_frequency, compute_word_mass, compute_word_phase_vector,
    _normalize_letters,
)
from src.physics.synchronize import synchronize, Vocabulary
from src.physics.spectral_wave_engine import (
    SpectralCouplingMatrix, PhysicsTranslator, PhysicsGenerativeNetwork,
    compute_word_wave, wave_at,
)
from src.physics.generator import Generator
from src.physics.morpho_phasic import MorphoPhasicEngine


# ── 1. Word Analyzer ──
def analyze_word(word):
    from src.physics.letter_db import LetterDB, DIM_NAMES
    db = LetterDB()
    norm = _normalize_letters(word)
    letters_info = []
    for ch in norm:
        if db.has(ch):
            info = db.data[ch]
            v = info.get('vector', np.zeros(22))
            omega = db.get_omega_0(ch)
            art = info.get('articulation', '?')
            man = info.get('manner', '?')
            meaning = info.get('meaning', '')
            top = sorted([(DIM_NAMES[i], v[i]) for i in range(len(v))],
                         key=lambda x: -abs(x[1]-0.5))[:2]
            letters_info.append({
                'ch': ch, 'omega': round(omega,2),
                'art': art, 'manner': man,
                'meaning': meaning[:60],
                'top': [(n,round(v,2)) for n,v in top],
            })
    return {
        'word': word,
        'freq': round(compute_word_frequency(word), 3),
        'mass': round(compute_word_mass(word), 6),
        'letters': letters_info,
    }


# ── 2. Bilingual Corpus + Translator ──
BILINGUAL_CORPUS = [
    "the sky is blue    السماء زرقاء",
    "water is life      الماء حياة",
    "fire burns         النار تحرق",
    "the king rules     الملك يحكم",
    "the queen is kind  الملكة لطيفة",
    "a man works        الرجل يعمل",
    "a woman reads      المرأة تقرأ",
    "the book is on the table  الكتاب على الطاولة",
    "the sun rises      الشمس تشرق",
    "the moon shines    القمر يضيء",
    "the cat sleeps     القطة تنام",
    "the dog runs       الكلب يجري",
    "the bird sings     العصفور يغرد",
    "the fish swims     السمكة تسبح",
    "the tree grows     الشجرة تنمو",
    "the flower blooms  الزهرة تتفتح",
    "the river flows    النهر يتدفق",
    "the mountain stands high  الجبل شامخ",
    "the night is dark  الليل مظلم",
    "the day is bright  النهار مشرق",
]


def test_translator():
    """اختبار المترجم الفيزيائي: ترجمة إنجليزي ← عربي عبر الاقتران الطيفي."""
    print("\n" + "="*60)
    print("  PhysicsTranslator — Bilingual Spectral Translation")
    print("="*60)
    
    vocab, K, syntax = synchronize(BILINGUAL_CORPUS)
    scm = SpectralCouplingMatrix()
    scm.fit(vocab, K, BILINGUAL_CORPUS)
    translator = PhysicsTranslator(scm, vocab)
    
    test_pairs = [
        'sky', 'water', 'fire', 'king', 'queen',
        'sun', 'moon', 'book', 'night', 'day',
    ]
    results = {}
    for w in test_pairs:
        translations = translator.translate(w, top_k=2)
        results[w] = translations
        if translations:
            t = translations[0]
            try:
                print(f"  {w:10s} -> {t[1]:12s}  (score={t[0]:.3f})")
            except UnicodeEncodeError:
                print(f"  {w:10s} -> [Arabic Text]  (score={t[0]:.3f})")
        else:
            print(f"  {w:10s} -> —  (no translation found)")
    
    return results


# ── 3. Wave Generation (English) ──
def test_wave_generation():
    """اختبار توليد Wave Mode بالإنجليزية."""
    print("\n" + "="*60)
    print("  Wave Mode Generation (English)")
    print("="*60)
    
    vocab, K, syntax = synchronize(BILINGUAL_CORPUS)
    morpho = MorphoPhasicEngine()
    gen = Generator(vocab, K, syntax_field=syntax, morpho=morpho, corpus_texts=BILINGUAL_CORPUS)
    
    prompts = ['the king', 'the water', 'the sky']
    for prompt in prompts:
        t0 = time.perf_counter()
        result = gen.generate(prompt, max_words=5, mode='wave')
        elapsed = time.perf_counter() - t0
        try:
            print(f"  '{prompt:12s}' -> {result:30s}  ({elapsed:.3f}s)")
        except UnicodeEncodeError:
            print(f"  '{prompt:12s}' -> [Arabic Text]  ({elapsed:.3f}s)")


# ── 4. Word Analysis Demo ──
def test_word_analysis():
    """تحليل الكلمات: فيزياء ومعاني الحروف."""
    print("\n" + "="*60)
    print("  Word Analysis — Letter Physics + Meanings")
    print("="*60)
    
    words = ['water', 'fire', 'sky', 'king', 'mother', 'night', 'song', 'bird']
    for w in words:
        a = analyze_word(w)
        letters_str = ' + '.join(
            f"{l['ch']}({l['art']}: {l['meaning'][:30]})"
            for l in a['letters']
        )
        print(f"  {w:8s} freq={a['freq']:.1f}  mass={a['mass']:.3f}")
        print(f"           {letters_str}")
        print()


def test_semantic_analogy():
    """اختبار القياس اللفظي: king − man + woman"""
    print("="*60)
    print("  Relational Analogy: king - man + woman")
    print("="*60)
    
    vocab, K, _ = synchronize(BILINGUAL_CORPUS)
    scm = SpectralCouplingMatrix()
    scm.fit(vocab, K, BILINGUAL_CORPUS)
    
    candidate, score = scm.relational_interference(
        target="the king",     # English normalized: "the king"
        add_words=["woman"],
        sub_words=["man"],
        vocab=vocab,
    )
    print(f"  king - man + woman = {candidate}  (score: {score:.3f})")


def test_benchmark():
    """اختبار benchmark — cloze task على جمل عربية."""
    from eval.benchmark import run_benchmark

    corpus = ["الملك حكم البلاد", "السماء زرقاء", "الطالب يدرس الدرس"]
    from src.physics.synchronize import synchronize
    from src.physics.generator import Generator
    vocab, K, syntax = synchronize(corpus)
    gen = Generator(vocab, K, corpus_texts=corpus, syntax_field=syntax)

    def scorer(context, top_k=50):
        words = context.split()
        all_pv = [gen._get_pv_fast(w) for w in words]
        context_ids = [vocab.word2id[w] for w in words if w in vocab.word2id]
        prev_word = words[-1] if words else None
        candidates = gen._resonance_candidates(context_ids, all_pv, set(), prev_word=prev_word)
        if not candidates:
            return []
        _prev_freqs = None
        if len(words) >= 2 and hasattr(gen, 'resonant_chain'):
            _prev_freqs = []
            for k in range(1, len(words)):
                wa, wb = words[k - 1], words[k]
                _prev_freqs.append(gen.resonant_chain.pair_freq(
                    gen._dyn_mass(wa), gen._dyn_mass(wb),
                    gen._get_pv_fast(wa), gen._get_pv_fast(wb)))
        scored = [(gen._score(w, set(), all_pv, [], len(words), len(words) + 10,
                              prev_word, context_ids, words, gen.entropy.k_B, gen.beta, None,
                              _prev_freqs=_prev_freqs), w)
                  for w in candidates[:top_k]]
        scored.sort(key=lambda x: -x[0])
        return scored

    result = run_benchmark(scorer)
    assert result['samples'] >= 3
    assert 0 <= result['precision@1'] <= 1
    assert result['pseudo_perplexity'] >= 0


def test_code_engine():
    """اختبار محرك البرمجة — K_code + توليد قوالب + تحقق نحوي."""
    from src.physics.code_engine import (
        CodeEngine, tokenize_code, validate_syntax, compile_check,
        CodeVocabulary, build_K_code,
    )
    import numpy as np

    corpus = [
        'def foo(x):\n    return x + 1\n',
        'for i in range(10):\n    print(i)\n',
    ]
    cv, ck = build_K_code(corpus)
    assert len(cv) >= 8
    assert ck.shape[0] == len(cv)

    engine = CodeEngine(code_vocab=cv, K_code=ck)
    code = engine.generate_python('create a function named test')
    assert 'def test' in code
    ok, err = engine.validate(code)
    assert ok, f'validation failed: {err}'

    toks = tokenize_code('x = 1\n')
    assert validate_syntax(toks)
    ok, err = compile_check('x = 1\n')
    assert ok

    suggs = engine.suggest_next(toks)
    assert len(suggs) > 0


def test_code_mode():
    """اختبار نمط code في Generator."""
    from src.physics.synchronize import synchronize
    from src.physics.generator import Generator

    corpus = [
        'def add(a, b):\n    return a + b\n',
    ]
    vocab, K, syntax = synchronize(["test code create a function"])
    gen = Generator(vocab, K, syntax_field=syntax, corpus_texts=corpus)
    result = gen.generate('create a function', mode='code', skip_bridge=True)
    assert isinstance(result, str)
    assert len(result) > 0
