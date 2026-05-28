# الدليل المعماري — mirnan V6 (Physics Orchestrator)

---

## هيكل المشروع

```
mirnan/
├── src/physics/            # النواة الفيزيائية ومعادلات Kuramoto والحقول الدلالية
│   ├── constants.py        # ثوابت فيزيائية (PHASE_DIM=22, …, TOTAL_DIM=64)
│   ├── letter_db.py        # 30 حرفاً عربياً + 26 إنجليزياً + operator + ω₀
│   ├── word_physics.py     # E=hf → m=E/c²، DDE، بُعد دلالي-فلسفي 16D
│   ├── weight_resonance.py # 14 وزناً صرفياً عربياً + جداول انتقالية
│   ├── english_morpheme.py # **V5.3** — EnglishMorphology + EnglishGrammar + EnglishWeightResonance
│   ├── spectral_wave_engine.py # **V5.3** — FFT, K_spectral, PGN, PhysicsTranslator
│   ├── spectral_memory.py  # **V5.4** — توقيع طيفي عالمي لكل كلمة (Coherence-Weighted Sum + Ground State)
│   ├── concept_matrix.py   # **V5.4** — ConceptMatrix + build_multi_k() → (K_syn, K_sem, K_conc) هرمياً
│   ├── causal_engine.py    # **V5.4** — CausalPhaseEngine: استدلال سببي موجه + transitive_score
│   ├── resonant_chain.py  # **V5.4** — ResonantChain: سلسلة دوائر LC بين كل كلمتين متجاورتين
│   ├── code_engine.py    # **V5.4** — CodeEngine: توليد كود Python + K_code + بوابة نحوية
│   ├── model_bundle.py   # **V5.4** — MirnanModelBundle: حفظ/تحميل كل البنى في مجلد واحد
│   ├── tafsir.py          # **V5.4** — Machine Tafsīr: تفكيك معنى الكلمة (حرف + جذر + طيف + شرح)
│   ├── generator.py        # توليد (standard/wave/quantum/multiverse/poetic/code) + V5.4: global_resonance + phase_opposition
│   ├── synchronize.py      # synchronize() + mmap save/load
│   ├── entropy_gate.py     # EntropyGate + تسجيل تلقائي
│   ├── ram_core.py         # AttractorMemory + Temporal Decay
│   ├── symbolic_bridge.py  # 6 قواعد رمزية
│   ├── syntax_field.py     # فضاء نحوي 6D غير متعامد + دعم عربي/إنجليزي تلقائي
│   ├── morpho_phasic.py    # صرف طوري (150 جذر + 15 وزن + 3 حالات)
│   ├── pragmatic_field.py  # V5.4: فضاء قصدي 6D + phase_opposition_score (غرفة رنين قصدي)
│   ├── poetic_gravity.py   # **مُحدّث V6** — 16 بحراً عربياً + كشف تلقائي + تقطيع عربي
│   ├── gravity.py          # جاذبية دلالية
│   ├── oscillator.py       # Kuramoto RK4
│   ├── dccf.py             # **جديد V6** — Dynamic Contextual Coupling Field (بديل self-attention)
│   ├── dialogue_engine.py  # **جديد V6** — DialogueEngine (محرك حوار يمنع الاستكمال الإحصائي)
│   ├── ppm.py              # **جديد V6** — Prompt Phase Modulation (In-Context Learning فيزيائي)
│   ├── amfs.py             # **جديد V6** — Adaptive Mass & Frequency Shift (contextual embeddings فيزيائية)
│   ├── orchestrator.py     # **جديد V6** — PhysicsOrchestrator (موحّد مركزي يدير كل المحركات)
│   ├── phase_reinforcement.py # **جديد V6** — PhaseReinforcement (تعزيز طوري ذاتي)
│   ├── potential_cascade.py   # **جديد V6** — PotentialCascadeLayer (هوي جهدي تراكمي حتمي)
│   └── math_bridge.py      # جسر رياضي
├── src/semantics/          # المحللات الدلالية والمورفولوجية
├── src/grammar/            # القواعد النحوية والإعراب
├── rust_core/              # **V5.4** — mirnan_core: FFT + Kuramoto (Rust PyO3, تسريع 12.9×)
├── eval/                   # اختبارات الأداء + validate_incremental.py
├── data/                   # corpus.txt, letter_physics_matrix.json, spectral_gss.npz
├── tests/                  # 108 اختباراً
├── README.md, PLAN.md, PIDLM_*.md, docs/
└── requirements.txt
```

---

## تدفق البيانات

```
نص → synchronize() → vocab, K, syntax
Generator(vocab, K, syntax, ram, entropy, bridge, morpho)
  → generate(prompt)
    ← resonance candidates من K × RAM × سياق
     ← لكل مرشح: 30+ معيار تسجيل
      syntax_phase_align = mean(cos(φ_syn(candidate) - φ_syn(expected)))
      حيث φ_syn = L2(anchor غير متعامد)، φ_syn(expected) = Σ K[prev][neighbor]·anchor / W
    ← تخزين المخرجات في RAM كجاذب جديد
```

---

## الطبقات الفيزيائية

### Layer 1 — الثوابت (`constants.py`)
```python
PHASE_DIM = 22       # أبعاد طورية أساسية
ROOT_DIMS = 8        # أبعاد جذرية
EXTRA_DIMS = 6       # أبعاد إضافية (DDE)
SYNTAX_DIMS = 6      # أبعاد نحوية
SEMANTIC_DIMS = 16   # أبعاد دلالية-فلسفية
PRAGMATIC_DIMS = 6   # أبعاد قصديّة
TOTAL_DIM = 64       # 22 + 8 + 6 + 6 + 16 + 6
```

### Layer 2 — الحروف (`letter_db.py`)
30 حرفاً، كل حرف بمتجه 22D و operator (+1 بنائي / -1 تدميري / 0 محايد).

### Layer 3 — الكلمات (`word_physics.py`)
- `compute_word_phase_vector(word)` — متجه 22D بترجيح موضعي
- `compute_extended_phase_vector(word)` — متجه 64D (22 طوري + 8 جذري + 6 إضافي + 6 نحوي + 16 دلالي + 6 قصدي)
- `_compute_extra_dims(word)` — operator_score, word_length, freq_norm, energy_norm, op_var, diversity
- `dress_phase_vector()` / `dress_extended_phase_vector()` — تطويق سياقي

### Layer 4 — المكونات

**RAM** (`ram_core.py`):
- `observe(words)`: يحسب φ_center، يدمج مع الجواذب المتشابهة (cos > 0.92)
- `resonate(φ, top_k)`: exp(-‖φ-φ_k‖²/2σ²)
- `retrieve_context(φ)`: يسترجع كلمات كسياق إضافي

**EntropyGate** (`entropy_gate.py`):
- `compute_S(pvs, target)`: S = -Σ p_i log p_i
- `evaluate(S)`: إذا S > S_crit → k_B/2, β×1.5

**جسر رمزي** (`symbolic_bridge.py`):
- 6 قواعد مسجلة في `_RULES` تُقيّم بالتكرار دون تعلم

**صرف طوري** (`morpho_phasic.py`):
- 150 جذراً ثلاثياً/رباعياً → φ_root
- 15 وزناً صرفياً → trajectory متجه 34D
- 3 حالات إعراب → case_anchor (مرفوع: 0.4, منصوب: 0.2, مجرور: 0.1)

**فضاء نحوي 6D** (`syntax_field.py`):
- 6 مرتكزات غير متعامدة: verb=[1,0.2,0,0,0.15,0.1], noun=[0.2,1,0.7,0,0.3,0.4], prep=[0,0.7,1,0,0.1,0]
- `compute_syntax_vector(word)` → L2(anchor), لا Hebbian dilution
- `expected_syntax(prev_word)` → Σ K[prev][neighbor]·anchor(neighbor) / W → L2
- `_get_syntax_anchor(word)` ← lookup → prefix → indeclinable → noun-like → morpho
- discriminates جار+اسم vs جار+فعل: Δ=0.825, 100%

**الذاكرة الطيفية العالمية** (`spectral_memory.py`) — **V5.4**:
- `build_contexts_map(corpus_texts, vocab, half_window=7)`: يجمع لكل كلمة متجهات السياق من كل ظهور في الكوربوس
- `GlobalSpectralMemory.build_global_signatures()`: يبني التوقيع الطيفي لكل كلمة عبر Coherence-Weighted Summation (يعزز السياقات المتسقة طورياً، يهمل الشواذ)
- `get_global_resonance(candidate_id, ctx_vector)`: يقيس توافق المرشح مع كل سياقاته المخزّنة — هذا هو "فهم" الكلمة على مستوى النص الكامل
- تخزين/تحميل سريع عبر `npz` — يُبنى لمرة واحدة في `synchronize()`

**المعمارية الهرمية لـ 3 مصفوفات K** (`concept_matrix.py`, `synchronize.py`) — **V5.4**:
- `K_syn` (نافذة 2): مزامنة نحوية — تلتقط التراكيب القصيرة (حرف جر + اسم، فعل + فاعل)
- `K_sem` (نافذة 5): مزامنة دلالية — المصفوفة الأصلية للترابط السياقي المتوسط
- `K_conc` (GSS): مصفوفة مفاهيمية من التوقيعات الطيفية — `cos(gss_i, gss_j)` تربط الكلمات المتشابهة دلالياً حتى لو لم تظهر معاً
- `build_multi_k()`: تبني الثلاث معاً من vocab واحد
- أوزان ديناميكية في `_score()`: أول 3 كلمات ← K_syn بـوزن 1.5، بعدها ← K_conc بـوزن 1.5

**غرفة الرنين القصدي** (`pragmatic_field.py`):
- `phase_opposition_score(w_pv, ctx_pvs)`: يحسب متوسط `|cos|` بين الكلمة وكل كلمات السياق بعد طرح ground state
- |cos| < 0.15 → تناقض منطقي (−1.0)
- |cos| > 0.70 → توافق طوري (+0.5)
- غير ذلك → محايد (0.0)

**محرك الاستدلال السببي** (`causal_engine.py`) — **V5.4**:
- `build_from_corpus(corpus, vocab)`: يبني مصفوفة سببية موجهة `causal[i,j] = (before - after)/(before + after)`
- `causal_strength(i, j)`: درجة 0..1 أن i تسبب j
- `transitive_score(ids)`: يتحقق من اتساق السلاسل المنطقية (A→B, B→C ⇒ A→C)
- `score_candidate(wid, ctx_ids)`: يُضاف إلى `_score()` بوزن `causal=2.0`
- `save(path) / load(path, V)`: حفظ وتحميل `causal_K.npz` — لا حاجة لإعادة بناء عند كل تشغيل

**السلسلة الرنانة LC** (`resonant_chain.py`) — **V5.4**:
- كل كلمتين متجاورتين = صفيحتان لمكثف (سعة دلالية C) + سلك محاثة (محاثة دلالية L)
- `C(i,j) = mass_i * mass_j * (1 + cos(pv_i, pv_j))` — كلما زاد التوافق الطوري زادت السعة
- `L(i,j) = 1 / (1 + |sin(Δφ/2)|)` — المحاثة تعكس قوة الاقتران
- `f_res(i,j) = 1 / (2π√(LC))` — تردد الرنين الطبيعي للزوج
- `sentence_coherence(masses, pvs)`: اتساق ترددات الرنين عبر الجملة (0..1)
- `score_candidate(m_prev, m_cand, pv_prev, pv_cand, prev_freqs)`: درجة توافق المرشح مع السلسلة الحالية — يُضاف إلى `_score()` بوزن `resonant_chain=3.0`
- كلما كانت ترددات الرنين للجملة بأكملها متقاربة، زاد التماسك — وهذا يكافئ جملة واحدة متماسكة رنينياً كسلك معدني منتظم

- `step(prev, chosen, w_pv)`: يرصد R_syn لكل انتقال
- `report()`: SyntaxLock mean, min, decay rate, drift events, rebel dimension
- عتبة إنذار: R < 0.65 → تسجيل البعد المتمرد

**محرك البرمجة** (`code_engine.py`) — **V5.4**:
- `tokenize_code(source)`: تحليل كود Python إلى 16 نوع token (KEYWORD, IDENTIFIER, OPERATOR, LITERAL_NUM, …)
- `CodeVocabulary`: معجم للـ tokens البرمجية (مثل Vocabulary لكن للـ code)
- `build_K_code(corpus)`: بناء مصفوفة K_code (اقتران tokens) من كوربس Python
- `validate_syntax(tokens)`: بوابة نحوية عبر مصفوفة VALID_NEXT (16×16) + compile_check حقيقي
- `CodePhaseVector`: متجه طوري 64D لكل token برمجي
- `CodeEngine.generate_python(prompt)`: توليد عبر قوالب (function/loop/class) + رنين K_code
- `CodeEngine.suggest_next(tokens)`: اختيار الـ token التالي من K_code + القواعد النحوية
- `_code_generate(prompt, max_tokens)` في Generator: نمط `mode='code'` للتوليد البرمجي

**طبقة الهوي التراكمي** (`potential_cascade.py`) — **جديد V6**:
- `compute_score(candidate_pv, context_pvs, context_masses, syntax_valid, used_words, word_to_pv_fn)`: يحسب الجهد الكلي للمرشح عبر قانون تربيع عكسي (γ=2.0) مع كتلة دلالية × توافق طوري / مسافة موضعية
- **Phase Lock Gate**: يرفض المرشح (`-inf`) إذا كان `cos(candidate, last_context) < 0.65`
- **Syntax Wall**: يرفض المرشح (`-inf`) إذا كان مخالفاً نحوياً
- **Pauli Repulsion**: تنافر عكسي مع مربع المسافة في فضاء الطور لمنع تكرار الكلمات القريبة
- يُدمج في `_score()` بوزن `W['cascade'] = 1.50` ويُفعّل عبر `orch.set_cascade()`

**محرك الحوار** (`dialogue_engine.py`) — **جديد V6**:
- `compute_dialogue_score(candidate_pv, response_target_pv, user_last_word, recent_words)`: يسجل المرشح وفق 4 معايير — توافق مع هدف الاستجابة، عقوبة الاستكمال (cos > 0.7 مع آخر كلمة), مكافأة بدء الجملة (إن، قد، this, the), عقوبة التكرار
- `detect_need_for_dialogue(prompt, intent_detector)`: يقرر إذا كان الإدخال يحتاج رداً حوارياً
- `get_response_seeds(intent)`: يسترجع بذور الرد المناسبة حسب القصد (تحية ← وعليكم/أهلا، سؤال ← السؤال/الجواب، …)
- `_dialogue_generate(prompt, max_tokens)`: توليد مع إلقاح ببادئة رد وإيقاف عند أول جملة تامة
- يُدمج في `_score()` بوزن `W['dialogue'] = 3.00` ويُفعّل عبر `orch.set_dialogue(True)` أو `--dialogue`

### Layer 5 — التوليد (`generator.py`)
30+ معيار تسجيل (V5.4):
```
score = w_align·align + w_prompt·prompt + w_diversity·diversity + w_syntax·syntax
      + w_resonance·resonance - w_repulsion·repulsion + ram_boost
      + w_symbolic·symbolic + w_morpho·morpho + w_morpho_trans·morpho_trans
      + w_sentence·sentence + w_pos_alt·pos_alt + w_irab·irab
      + w_syntax_gate·syntax_gate + w_phil_semantic·phil_semantic
      + w_root_align·root_align + w_ram_plan·ram_plan + w_gravity·gravity
      + w_pragmatic·pragmatic + w_weight_resonance·weight_resonance
      + w_poetic·poetic + w_rhyme·rhyme + w_spectral·spectral
      + w_thermo·thermo + w_dialogue_gravity + w_dialogue_spectral
      + w_intent_align + w_associative_plan + w_entity_align
      + w_plan_fidelity + w_sentiment + w_anchor_affinity
      + w_semantic_density + w_novelty
      + w_relational_resonance·relational_resonance (spectral wave)
      + w_context_wave_filter·adaptive_context_filter (spectral wave)
      + w_eng_morpho·english_morpho_score (للإنجليزية فقط)
      + w_eng_morpho_trans·english_transition_score
      + w_eng_grammar·english_grammar_score
      + w_eng_agreement·english_agreement_score
      + w_eng_stem_align·english_stem_align
      + w_global_resonance·global_resonance_score  **← V5.4**
      + w_phase_opposition·phase_opp_score         **← V5.4**
      + w_syn·dyn_syn·K_syn_score·act              **← V5.4 مصفوفة هرمية**
      + w_sem·dyn_sem·K_sem_score·act              **← V5.4**
      + w_conc·dyn_conc·K_conc_score·act           **← V5.4**
      + w_causal·causal_score                      **← V5.4 محرك سببي**
      + w_resonant_chain·resonant_chain_score      **← V5.4 سلسلة LC رنانة**
+ w_cascade·cascade_score                    **← V6 طبقة الهوي التراكمي**
+ w_dialogue·dialogue_score                  **← V6 محرك الحوار**
```

حيث `weight_resonance` يدعم كلاً من العربية (14 وزناً صرفياً) والإنجليزية (14 وزناً إنجليزياً) مع كشف لغة تلقائي.

`mode='wave'` يستخدم PhysicsGenerativeNetwork (PGN) للبحث عن مسار الطاقة القصوى في رسم بياني للرنين الطيفي، وهو أسرع من standard (0.015s vs 0.018s).

### Layer 6 — التقرير الفيزيائي (`get_physics_report()`)
```python
report = gen.get_physics_report(prompt, result)
# → {
#     "word_masses": {word: mass},        # كتلة كل كلمة
#     "phase_angles": [0.0–1.0, ...],     # زاوية طور كل كلمة
#     "alignments": ["متوافق_0.99", ...], # محاذاة للهدف
#     "morph_weights": {weight: count},   # توزيع الأوزان الصرفية
#     "ram_size": int,                    # عدد الجواذب
#     "vocab_size": int,                  # حجم المفردات
#     "top_k": [word, ...]               # الكلمات المولدة
# }
```

---

## مسار التوسع — مكتمل

1. [x] توسيع قاعدة الجذور (150 → لا نهائي عبر ArabicRootExtractor الخوارزمي)
2. [x] إضافة قواعد رمزية (YAML config في `data/rules/symbolic_rules.yaml`)
3. [x] اختبار تغيير الموضوع المفاجئ (RAM Temporal Decay + SyntaxMonitor)
4. [x] Anchor Drift المشروط (SyntaxMonitor يرصد R_syn لكل انتقال)
5. [x] تسريع multiverse عبر PV cache و candidate reduction (2× speedup)
6. [x] واجهة تفاعلية Web مع Physics Dashboard و Particles.js
7. [x] WeightResonanceEngine للرنين الصرفي العربي
8. [x] **Spectral Wave Engine** — FFT، K_spectral، PGN، PhysicsTranslator
9. [x] **English LetterDB** — 26 حرفاً بترددات COCA ومعاني دلالية
10. [x] **EnglishMorphology** — POS tagging (12 صنف)، تحليل صرفي، stemmer
11. [x] **EnglishGrammarEngine** — SVO، a/an، توافق الفعل والفاعل
12. [x] **EnglishWeightResonance** — 14 وزناً إنجليزياً + مصفوفة انتقالية
13. [x] **English Poetic Meters** — 6 أبحُر إنجليزية
14. [x] **English Syntax Anchors** — 8 مرتكزات نحوية
15. [x] **GlobalSpectralMemory** — توقيع طيفي عالمي لكل كلمة (V5.4)
16. [x] **Phase Opposition Chamber** — كشف التناقض المنطقي عبر التعاكس الطوري (V5.4)
17. [x] حذف واجهات المستخدم (اختبار وكيل عبر Python API مباشرة)
18. [x] **المعمارية الهرمية 3K** — K_syn + K_sem + K_conc بأوزان ديناميكية (V5.4)
19. [x] **ConceptMatrix** — `build_multi_k()` يبني الثلاث معاً من vocab واحد
20. [x] **التعلم التزايدي** — `assimilate_text()` للإضافة المستمرة
21. [x] **CausalPhaseEngine** — استدلال سببي موجه + transitive_score + score_candidate
22. [x] **ResonantChain** — سلسلة دوائر LC بين كل كلمتين لتقييم التماسك الرنيني
23. [x] **إيقاف مبكر رنيني** — قطع التوليد إذا انخفض التماسك تحت 0.3
24. [x] **كتلة ديناميكية** — `_dyn_mass()` من K matrix + مرساة نحوية
25. [x] **حفظ/تحميل causal_K** — `causal_K.npz` للتشغيل السريع
26. [x] **CodeEngine** — توليد كود Python + K_code + بوابة VALID_NEXT + compile_check
27. [x] **SyntaxField.save/load** — serialize كل الحقول النحوية إلى JSON
28. [x] **GlobalSpectralMemory.save/load** — دوال عامة لحملة GSS إلى npz
29. [x] **CodeVocabulary.save/load** — serialize معجم البرمجة إلى JSON
30. [x] **MirnanModelBundle** — حزمة موحدة تحفظ وتحمّل كل البنى في مجلد واحد
31. [x] **Machine Tafsīr** — `tafsir.py`: تفكيك معنى الكلمة (تحليل حرف + جذر + طيف FFT + كتلة + شرح عربي)
32. [x] **Rust Core (mirnan_core)** — `rust_core/`: PyO3 bindings لـ FFT + Kuramoto (تسريع 12.9×)
33. [x] **التحقق التزايدي** — `eval/validate_incremental.py`: قياس K_diff + مقارنة التوليد بعد assimilate_text()

33. [x] **DCCF** — Dynamic Contextual Coupling Field (بديل self-attention)
34. [x] **PPM** — Prompt Phase Modulation (In-Context Learning فيزيائي)
35. [x] **AMFS** — Adaptive Mass & Frequency Shift (contextual embeddings)
36. [x] **PhysicsOrchestrator** — موحّد مركزي يدير كل المحركات + كشف تلقائي للوضع
37. [x] **PhaseReinforcement** — تعزيز طوري ذاتي (تعلّم بدون backprop)
38. [x] **PoeticGravityEngine كامل** — 16 بحراً عربياً + كشف تلقائي + تقطيع عربي
39. [x] **CLI تفاعلية** — python cli.py -i مع أوامر /beta, /k_B, /mode, /report
40. [x] **PotentialCascadeLayer** — طبقة هوي جهدي تراكمي حتمي، لا softmax ولا temperature، قانون تربيع عكسي (γ=2.0)
41. [x] **DialogueEngine** — محرك حوار يمنع الاستكمال الإحصائي: كشف القصد، استرجاع قالب الرد، إلقاح ببادئة رد، إيقاف عند أول جملة تامة

## مسار التوسع — مستقبلي

1. **بصمة كاتب (Author Fingerprint)**: توقيع طوري فريد لكل كاتب يُكتشف من نصوصه.
2. **تداخل موسيقي (Music-Text Resonance)**: تحويل النص إلى MIDI عبر ترددات ω₀.
3. **PhysicsTranslator باستخدام WordNet:** معجم ثنائي اللغة (عربي-إنجليزي) مع align spectral.
4. **فك الغموض الدلالي:** تفرع كمومي للسياقات المجازية المعقدة.
5. **حوار طويل المدى:** PhaseReinforcement يتعلم من التقييم البشري المباشر.
6. **Rust Core شامل:** نقل DCCF coupling و FFT السريع إلى Rust للسرعة القصوى.
