# mirnan V6 — Physics Orchestrator
## المواصفة المعمارية الكاملة — وثيقة تخطيط

---

## 1. فلسفة المشروع (Project Philosophy)

**المبدأ الأساسي:** اللغة ظاهرة فيزيائية قبل أن تكون ظاهرة رياضية أو إحصائية.

- **الحرف = مذبذب أساسي** بتردد ذاتي (ω₀) وأبعاد طورية
- **الكلمة = تداخل (Interference)** لمذبذبات حروفها + جذرها الصرفي + كتلتها النسبية
- **الجملة = نظام ديناميكي** من كتل دلالية تتجاذب في فضاء طوري
- **المعنى = حالة استقرار طوري (Phase Locking)** أو انهيار للدالة الموجية (Wave Collapse).
- **التعلم = مزامنة (Synchronization)** — وليس backpropagation

**لا يُستخدم:**
- شبكات عصبية من أي نوع
- خوارزميات تحسين تقليدية (SGD, Adam)
- ترميز positions (الموضع ضمن الجملة تحكمه الجاذبية والنسبية)
- حجماً عشوائياً (العشوائية فقط في thermal noise الفيزيائي)

---

## 2. الطبقات المعمارية (Architecture Layers)

```
┌──────────────────────────────────────────────────┐
│                  7. واجهة الاستخدام               │
│            (CLI / REST / Chat Interface)          │
├──────────────────────────────────────────────────┤
│              6. محرك التوليد (Generator)           │
│         تراكب كمومي + انهيار الانتروبيا + الجاذبية │
├──────────────────────────────────────────────────┤
│             5. محرك التدريب (Trainer)              │
│     synchronize() بدلاً من train() — لا خسارة       │
├──────────────────────────────────────────────────┤
│          4. محرك الجاذبية الدلالية (Gravity)        │
│        F = G·m₁·m₂/r²  +  Kuramoto + RK4          │
├──────────────────────────────────────────────────┤
│       3. محرك فيزياء الكلمة (Word Physics)          │
│      E = hf → m = E/c² → طور → كتلة → حقول        │
├──────────────────────────────────────────────────┤
│       2. محرك فيزياء الحرف (Letter Physics)         │
│    ω₀, أبعاد HD-ROV, مصفوفة الرقيم, الجذور (16D)  │
├──────────────────────────────────────────────────┤
│             1. الثوابت الفيزيائية الأساسية           │
│          h (دلالي), c (دلالي), G (دلالي)           │
└──────────────────────────────────────────────────┘
```

---

## 3. الثوابت الفيزيائية الأساسية (Layer 1)

```python
# ثوابت كوننا الدلالي — قابلة للضبط
PHYSICAL_CONSTANTS = {
    "h": 1.0,            # ثابت بلانك الدلالي (Semantic Planck)
    "c": 1.0,            # سرعة الضوء الدلالي
    "G": 1.0,            # ثابت الجاذبية الدلالي
    "kB": 0.1,           # ثابت بولتزمان (ضوضاء حرارية دلالية)
    "PHASE_DIM": 22,     # أبعاد طورية أساسية
    "EXTRA_DIMS": 6,     # أبعاد DDE إضافية
    "SYNTAX_DIMS": 6,    # أبعاد نحوية 
    "SEMANTIC_DIMS": 16, # أبعاد دلالية فلسفية وجذور
    "PRAGMATIC_DIMS": 6, # أبعاد الفضاء القصدي العلائقي
    "TOTAL_DIM": 64,     # الفضاء الكلي 64 بُعداً!
}
```

---

## 4. الميكانيكا الكمومية والنسبية والقصدية (V5.1 Innovations)

### 4.1 التراكب الكمومي والانهيار
استبدال البحث الشعاعي الكلاسيكي بخوارزمية التراكب:
- الكلمات تعيش كمتجهات تراكب ولا يُتخذ قرار نهائي لها ما دامت الإنتروبيا `$S > S_{crit}$`.
- عند الرنين، تسقط الإنتروبيا وينهار النظام إلى سلسلة كلمات محددة كواقع نهائي.

### 4.2 الانحناء النسبي (الجاذبية)
- لكل كلمة كتلة `$m = E/c^2$`.
- يتم مضاعفة كتل الأسماء لتشكيل "آبار جاذبية" عميقة تجذب الأفعال والمفاعيل حولها.

### 4.3 طاقة الربط القصدي (Pragmatic Binding Energy)
- مساحة علائقية إضافية بـ 6 أبعاد تُشتق من الدلالة والنحو.
- تضمن ترابط الكلمات وفق سياق وظيفي مقصود (مثل "مكان"، "زمان"، "سبب") باستخدام آبار الجهد القصدي.

### 4.4 إطار القواعد الرمزية (YAML)
- بدلاً من التشفير الثابت، قواعد اللغة مخزنة في `data/rules/symbolic_rules.yaml`.
- يمكن إضافة مئات القواعد ليقرأها النظام ويحولها لدوال بايثون ديناميكية فورية دون فقدان الأداء.

---

## 5. الموجات الطيفية والتكافؤ الإنجليزي (V5.3 Innovations)

### 5.1 Spectral Wave Engine
الكلمة = حزمة موجية (wave packet) ممثلة في مجال التردد عبر FFT:
- `compute_word_wave(word)` → `{freqs, magnitudes, phases, ω₀, A₀, φ₀, sidebands}`
- `wave_at(word, t)` → recontruction زمني
- `wave_spectrum(word)` → كثافة طيفية (frequency bin × intensity)
- `wave_signature(word)` → بصمة طيفية للمقارنة بين الكلمات

### 5.2 Spectral Coupling Matrix (K_spectral)
استبدال مصفوفة K الخام بمصفوفة ارتباط طيفي:
- `K_spectral[w₁][w₂] = |∫ Ψ₁*(ω) · Ψ₂(ω) dω|²`
- FFT cache + signal cache لتسريع الحساب
- sidebands من co-occurrence: sideband_ω = |ω₁ − ω₂| لكل زوج كلمات متجاورة
- تصفية الضوضاء: coupling_threshold = median × 0.15

### 5.3 PhysicsGenerativeNetwork (PGN)
التوليد عبر البحث عن مسار الطاقة القصوى في رسم بياني للرنين الطيفي:
- `find_path(start_words, max_steps)` → أعلى مسار طاقة
- أسرع من standard (0.015s vs 0.018s) بفضل التخزين المؤقت
- نمط التوليد `mode='wave'`

### 5.4 الجبر العلائقي
- `relational_interference(target, ctx_remove, ctx_add)` → ψ_result = ψ_target − ψ_remove + ψ_add
- محاكاة king − man + woman = queen دون تدريب

### 5.5 مرشح السياق التكيفي (adaptive_context_filter)
- عرض الحزمة (bandwidth) محسوب تلقائياً من median(|Δ|)
- قناع sigmoid: 1/(1+(δ/bw)²) بدلاً من exp(-δ/bw)
- خفض مزيج السياق: 0.15 بدلاً من 0.3

### 5.6 PhysicsTranslator
- `search(target_word, language='ar')` → ترجمة عبر مطابقة الطيف
- يستخدم K_spectral من معجم ثنائي اللغة، ليس مقارنة موجية مباشرة
- night → الليل (score 666), moon → القمر (344), sun → الشمس (227)

### 5.7 PhaseLogicalInference
- استنتاج متعدٍ عبر سلاسل موجية
- A → B (مباشر), B → C (مباشر), A → C (استنتاج)

### 5.8 English LetterDB
- 26 حرفاً + /ŋ/ بترددات COCA (E=12.49%, T=9.28%, A=8.04%, …)
- 22D phase vectors بمعاني دلالية من 3 أجزاء
- articulation points (throat, labial, alveolar, velar, palatal, glottal, labiodental, labial-velar)
- manner of articulation

### 5.9 البنية التحتية الإنجليزية الكاملة
- **EnglishMorphology**: POS tagging (12 صنف)، تحليل صرفي (زمن/عدد/شخص/نفي/بادئات)
- **EnglishGrammarEngine**: كشف نوع الجملة (declarative/interrogative/imperative)، توافق الفعل والفاعل (is/are, has/have, verb+s)، استخدامات a/an
- **EnglishWeightResonance**: 14 وزناً (noun_sing/pl/proper, verb_present/past/gerund/participle, adj_base/comp/sup, adv, det, prep, pron) مع مصفوفة انتقالية 14×14 ومتجهات طورية 22D
- **EnglishStemmer**: يعالج went→go, running→run, shines→shine, children→child, happily→happy
- **English Poetic Meters**: iambic pentameter/tetrameter/trimeter, trochaic tetrameter, anapestic trimeter, dactylic dimeter + syllable counter + rhyme groups (ee, ay, oo, ow, oy, ar, er, ate, ight)
- **English Syntax Anchors**: noun/verb/adj/adv/det/prep/pron/conj في syntax_field.py

### 5.10 دمج في Generator
- 5 أوزان جديدة في `_score()` للكلمات الإنجليزية
- كشف اللغة تلقائياً (`_is_english_word`)
- أوزان: eng_morpho 0.80, eng_morpho_trans 0.60, eng_grammar 1.00, eng_agreement 0.50, eng_stem_align 0.60
- إزالة الخريطة الإنجليزية→العربية من `_normalize_letters`

### 5.11 اختبارات
- 4 اختبارات تكامل جديدة (translator, wave generation, word analysis, semantic analogy)
- 4 اختبارات وحدات للموجات الطيفية (relational analogy, sideband noise, adaptive filter, performance)
- 89 اختباراً إجمالاً: 87 نجاح، 2 فشل مورفوسياسي سابق — 0 تراجعات

---

## 6. خريطة الطريق (Implementation Roadmap)

### المرحلة 0: الأسس (مكتملة)
- [x] مصفوفة الرقيم ومستخرج الجذور العربية
- [x] محرك Kuramoto + RK4 ومزامنة Hebbian

### المرحلة 1: فيزياء الكلمة والطور (مكتملة)
- [x] E = hf → m = E/c² و DDE
- [x] تطويق سياقي و RAM و EntropyGate

### المرحلة 2: النحو والصرف (مكتملة)
- [x] فضاء نحوي 6D غير متعامد
- [x] جذور وأوزان وصرف طوري

### المرحلة 3: الفيزياء اللغوية المتقدمة V5.1 (مكتملة)
- [x] دمج معاني الحروف الفلسفية في متجهات `NumPy` (`SEMANTIC_DIMS`)
- [x] الانحناء النسبي (Gravity Wells) بكتلة الكلمات
- [x] التخطيط العابر للجمل باستخدام `AttractorMemory`
- [x] نظام قواعد `YAML` الرمزي الشامل
- [x] وضع التوليد بالدالة الكمومية (`mode='quantum'`)
- [x] الفضاء القصدي وطاقة الربط (`PragmaticBindingEngine`)

### المرحلة 4: الجماليات والأداء (مكتملة)
- [x] المولد الشعري: إضافة مجالات جذب عروضية لوزن القصيدة والقافية
- [x] نظام تقييم بشري وآلي (`human_eval.py`)
- [x] الاستعانة بـ Rust لتسريع محرك المصفوفات العملاقة
- [x] واجهة رسومية لإظهار انهيار الدالة الموجية بشكل مرئي

### المرحلة 5: التوسع والاندماج (مكتملة)
- [x] محرك الجاذبية متعدد الأجسام (N-Body Gravity) للترابط بعيد المدى.
- [x] المستخرج الصرفي الخوارزمي لتوسيع قاعدة الجذور لتشمل كامل اللغة.
- [x] نشر المحرك كواجهة برمجية API (FastAPI Backend).

### المرحلة 6: واجهة الويب والتوسع العتادي (مكتملة)
- [x] بناء واجهة ويب حديثة وتفاعلية (Modern Web UI) تتصل بالـ API الخاص بمرنان.
- [x] تصميم مرئي مذهل (Premium Design) يعرض التراكب الكمومي والانهيار بأسلوب تفاعلي.
- [x] تقليل استهلاك الذاكرة العشوائية للبيانات الضخمة عبر (Memory-Mapped Files / HDF5).

### المرحلة 7: الدمج اللغوي العميق (مكتملة)
- [x] دمج "المحلل الصرفي الفطري" في `syntax_field.py` لرفع دقة توجيه الكلمات في الفضاء النحوي.
- [x] دمج محرك "المستنبط" (Mustanbit) في الفضاء القصدي `pragmatic_field.py` لاكتشاف الأزمنة والأدوار والعلاقات وبناء جاذبية قصدية فائقة الذكاء.

### المرحلة 8: مرنان V5.0 - الارتقاء الفيزيائي والوعي (مكتملة)
- [x] تحسين خوارزمية الجاذبية (Vectorized Gravity) لتجنب $O(N^2)$ والتسريع باستخدام NumPy.
- [x] تطوير آلية الانتباه الطوري اللحظي (Phase Attention) لمحاكاة المعنى السياقي المتغير للكلمات.
- [x] بناء الذاكرة الزمنية المتلاشية (Temporal Decay) في `ram_core.py` لمنع التشويش من السياقات القديمة جداً.

### المرحلة 9: مرنان V5.1 — الرنين الصرفي والتقارير الفيزيائية (مكتملة)
- [x] **WeightResonanceEngine**: 14 وزناً صرفياً عربياً (فَعَلَ، فَعَّلَ، فَاعَلَ، …) مع متجهات طورية 22D وجداول انتقالية تضمن سلاسة التحولات بين الصيغ.
- [x] **تقرير الفيزياء (Physics Report)**: `get_physics_report()` في `Generator` يعيد word_masses, phase_angles, alignments, morph_weights, ram_size, vocab_size.
- [x] **واجهة API محدثة**: نقطة النهاية `/generate` تعيد `physics` metadata إلى جانب `result`.
- [x] **لوحة الفيزياء التفاعلية**: `ui/index.html` يعرض دائرة الأطوار، كتل الكلمات، بوابة الإنتروبيا، والأوزان الصرفية لحظة التوليد.

### المرحلة 10: تحسين الأداء والاختبارات (مكتملة)
- [x] **اختبار الإجهاد (Stress Test)**: `eval/stress_test.py` يقيس أداء التزامن، التوليد، و MMAP مع 7 ملفات و 58K كلمة.
- [x] **تحسين multiverse mode**: تخفيض سعة التراكب من 20→15، تقليل المرشحين من 40→20، تخزين PV. تسريع 2x (5.76s → 2.83s).
- [x] **اختبار الفيزياء الميتاداتا**: `eval/physics_metadata_test.py` يتحقق من صحة جميع حقول التقرير الفيزيائي.
- [x] **إصلاح الأكواد الميتة**: إزالة `print` التصحيح في `generator.py`، إصلاح `_cache={}` في `word_physics.py` و `symbolic_bridge.py`.
- [x] **تسجيل الأحداث (Logging)**: استبدال `print()` بـ `logging` في API و EntropyGate.

### المرحلة 11: الموجات الطيفية والتكافؤ الإنجليزي V5.3 (مكتملة)
- [x] **Spectral Wave Engine**: compute_word_wave(), wave_at(), wave_spectrum(), wave_signature()
- [x] **SpectralCouplingMatrix**: K_spectral عبر FFT بدلاً من K الخام — مع FFT cache + signal cache
- [x] **Sidebands من co-occurrence**: sideband_ω = |ω₁−ω₂| ب coupling_threshold = median × 0.15
- [x] **PhysicsGenerativeNetwork (PGN)**: pathfinding على رسم بياني للرنين الطيفي — 0.015s (أسرع من standard)
- [x] **PhysicsTranslator**: ترجمة عبر مطابقة الطيف مع K_spectral من معجم ثنائي اللغة
- [x] **English LetterDB**: 26 حرفاً + /ŋ/ بترددات COCA، متجهات 22D، articulation + manner + meaning
- [x] **EnglishMorphology**: POS tagging (12 صنف)، تحليل صرفي كامل (زمن/عدد/شخص/نفي/بادئات)
- [x] **EnglishGrammarEngine**: كشف نوع الجملة، توافق الفعل والفاعل، a/an
- [x] **EnglishWeightResonance**: 14 وزناً إنجليزياً مع مصفوفة انتقالية 14×14
- [x] **English Poetic Meters**: 6 أبحُر إنجليزية + syllable counter + rhyme groups
- [x] **English Syntax Anchors**: noun/verb/adj/adv/det/prep/pron/conj في syntax_field.py
- [x] **5 أوزان جديدة في Generator._score()**: eng_morpho, eng_morpho_trans, eng_grammar, eng_agreement, eng_stem_align
- [x] **إزالة الخريطة الإنجليزية→العربية**: النظامان مستقلان فيزيائياً
- [x] **89 اختباراً**: 87 نجاح، 2 فشل مورفوسياسي سابق — 0 تراجعات

### المرحلة 12: V6 — Physics Orchestrator (مكتملة)
- [x] **DCCF — Dynamic Contextual Coupling Field**: مصفوفة اقتران طوري لحظي بديل self-attention (phase alignment × كتلة × اضمحلال المسافة)
- [x] **PPM — Prompt Phase Modulation**: حقل طوري خارجي يضمحل — محاكاة فيزيائية لـ In-Context Learning
- [x] **AMFS — Adaptive Mass & Frequency Shift**: تعديل الكتلة والتردد حسب السياق — contextual embeddings فيزيائياً
- [x] **PhysicsOrchestrator**: موحّد فيزيائي يدير كل المحركات — كشف تلقائي للوضع، ضبط β/k_B حياً، تقارير موحّدة
- [x] **PhaseReinforcement**: تعزيز طوري ذاتي — تعلّم بدون backprop (Hebbian learning في فضاء طوري)
- [x] **PoeticGravityEngine كامل**: 16 بحراً عربياً مع كشف تلقائي وتفعيلة فيزيائية
- [x] **CLI تفاعلية**: python cli.py -i — أوامر /beta, /k_B, /mode, /report, /history, /reset
- [x] **دمج DCCF + PPM + AMFS في _score()**: 3 أوزان جديدة في معادلة التسجيل
- [x] **108 اختبارات**: 0 تراجعات
- [x] **PotentialCascadeLayer**: طبقة هوي جهدي تراكمي حتمي — كل كلمة تهوي إلى أعمق بئر جهد في الحقل التراكمي. لا softmax ولا temperature.
- [x] **DialogueEngine**: محرك حوار يمنع الاستكمال الإحصائي — يكشف القصد (تحية/سؤال/أمر)، يسترجع قالب الرد من AssociativeMemory، يُلقّح المولد ببادئة رد بدلاً من إكمال النص، يتوقف عند أول جملة تامة

### المرحلة 13: المستقبل — الخطط
- [ ] **بصمة كاتب (Author Fingerprint)**: توقيع طوري فريد لكل كاتب يُكتشف من نصوصه
- [ ] **تداخل موسيقي (Music-Text Resonance)**: تحويل النص إلى MIDI عبر ترددات ω₀
- [ ] **PhysicsTranslator واسع**: استخدام معجم WordNet عربي-إنجليزي مع align طيفي كامل
- [ ] **فك الغموض الدلالي**: تفرع كمومي مخصص للسياقات المجازية المعقدة
- [ ] **حوار طويل المدى**: PhaseReinforcement يتعلم من التقييم البشري المباشر
- [ ] **Rust Core شامل**: نقل DCCF coupling و FFT السريع إلى Rust للسرعة القصوى
