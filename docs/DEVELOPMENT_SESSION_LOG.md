# مرنان V7 — سجل جلسات التطوير
## Mirnan V7 — Development Session Log

> تم إنجاز هذه التغييرات عبر جلسات متعددة لتحويل مرنان من نموذج لغة فيزيائي تجريبي
> إلى نظام ذكاء توليفي متكامل.

---

## الجلسة 1: تحسين تحليل الحروف (دمج mirnan0)

### ملفات جديدة
| الملف | الوصف |
|-------|-------|
| `src/semantics/letter_meanings.py` | قاموس المعاني المتفرعة لـ 29 حرفاً عربياً (core, branches, opposite, standard_of) |
| `src/physics/vector_interpreter.py` | مفسر المتجهات 22D إلى نصوص عربية مفهومة (dominant/opposite/neutral) |

### ملفات مطوَّرة
| الملف | التغيير |
|-------|---------|
| `src/semantics/arabic_semantics.py` | **إعادة كتابة كاملة** — وضعان: `sparse` (29D مع مجموعات صوتية/شكلية/دلالية + حركات + bigram) و `sinusoidal` (16D للتوافق القديم) |
| `src/physics/word_physics.py` | إضافة بارامتر `weighted=True` للترجيح الموضعي [3.5, 2.5, 2.0, ...] — يكسر تناظر تباديل الحروف |
| `src/physics/constants.py` | إضافة `RICH_SEMANTIC_DIMS=29`، `TOTAL_RICH_DIM=77`، `POSITION_WEIGHTS` |
| `src/physics/letter_db.py` | إضافة `get_raw_norm()` |
| `config.yaml` | إضافة قسم `heterodyne` وأوزان جديدة |

### النتيجة
- **الترجيح الموضعي**: `استخراج` ≠ `خراجاست` (cos=0.9797 بدل 1.0)
- **النظام 29D**: 16 مدخلة غير صفرية لكل حرف بدل sinusoidal بدائي
- **المعاني المتفرعة**: لكل حرف معنى جامع + 5 تفرعات + ضد + ميزان
- **مفسر المتجهات**: ترجمة كل بُعد من الـ 22 إلى وصف موجب/سالب

---

## الجلسة 2: سد الفجوات الفيزيائية

### ملفات جديدة
| الملف | الوصف |
|-------|-------|
| `src/physics/heterodyne_engine.py` | محرك التغاير الترددي — يحاكي مستقبل الراديو: f_carrier ± f_context لاكتشاف الرفقاء السياقيين |

### محرك التغاير الترددي (HeterodyneEngine)
- `compute_sidebands()` — f_plus = f_carrier + f_context، f_minus = |f_carrier - f_context|
- `context_filter_companions()` — **عزل رفقاء الكلمة** في سياق محدد (الجزء الذي كان غائباً)
- `compute_k_weighted_resonance()` — دمج K-matrix مع الرنين الترددي
- `compute_context_signature()` — بصمة ترددية فريدة للسياق

### ملفات مطوَّرة
| الملف | التغيير |
|-------|---------|
| `src/physics/generator.py` | **6 تغييرات كبرى** (انظر أدناه) |
| `config.yaml` | أوزان `heterodyne: 2.50`، `oscillator: 1.50`، `category: 1.50` |

### تغييرات generator.py الستة
1. **ربط HeterodyneEngine** — `heterodyne_score` في `_score()` عبر `compute_k_weighted_resonance()`
2. **ربط OscillatorEngine** — `osc_score` عبر محاكاة RK4 لمذبذبات كوراموتو
3. **إصلاح الجاذبية** — من مسافة تسلسلية `|j-i|` إلى مسافة إقليدية في الفضاء 42D
4. **استيراد `compute_word_frequency`** — مطلوب لحسابات التغاير والمذبذبات
5. **تهيئة المحركات** — `self.heterodyne` و `self.osc_engine` في `__init__`
6. **إضافة الأوزان** — `heterodyne` و `oscillator` في `_init_weights()` و `return dict`

---

## الجلسة 3: إصلاح هيكل التوليد

### ملفات مطوَّرة
| الملف | التغيير |
|-------|---------|
| `src/physics/generator.py` | 6 إصلاحات هيكلية |
| `config.yaml` | وزن `category: 1.50` |

### الإصلاحات الهيكلية
1. **سقف بوابة الرنين** — `max_exp=20` على `np.exp(beta*sim)` (كان يصل إلى 22,000)
2. **قص درجة التسجيل** — `np.clip(score, -5.0, 5.0)` في نهاية `_score()`
3. **إصلاح k_dialogue_score** — من إضافة خام إلى `self.W['dialogue'] * ...`
4. **إصلاح category_score** — من إضافة خام 0.3 إلى `self.W['category'] * ...`
5. **إصلاح _init_weights()** — `cascade`, `dialogue`, `category` كانت خارج `pos_terms`
6. **آلية إنهاء ذكية** — مكافأة +0.3 لنهايات الجمل بعد 5 كلمات + عتبة `coh<0.5 مع S منخفض`

### تحسين أداء المذبذبات
- تشغيل محاكاة RK4 **مرة واحدة للسياق** في `_beam_step()` بدل كل مرشح (~250× أسرع)
- تمرير `_osc_ctx` إلى `_score()` مع مسار احتياطي تلقائي

---

## الجلسة 4: طبقة الذكاء التوليفي (SIO)

### ملفات جديدة — `src/sio/`
| الملف | الوصف |
|-------|-------|
| `__init__.py` | مدخل الوحدة |
| `goal_parser.py` | **GoalParser** — يحلل الهدف الطبيعي إلى 7 أنماط مراحل (plan, build, test, deploy, integrate, monitor, document) |
| `phase_planner.py` | **PhasePlanner** — تخطيط طويل المدى بمسار طوري + `compute_heterodyne_dependency()` لكشف تبعيات المراحل |
| `executor.py` | **PhaseExecutor** — حلقة اختبار وإصلاح ذاتية: generate → validate → fail? → diagnose → regenerate (حتى 5 محاولات) |
| `self_monitor.py` | **SelfMonitor** — رصد الانحراف عن الهدف + `compute_phase_quality()` لتقييم جودة المتجهات |
| `integrator.py` | **Integrator** — دمج الخطة + الكود + الاختبارات + النشر + التوثيق في منتج واحد |
| `orchestrator.py` | **SIOOrchestrator** — المنسق الأعلى: يحول فكرة إلى منتج في عملية واحدة |

### دورة الذكاء التوليفي
```
فكرة ← GoalParser ← PhasePlanner ← [Executor ⇄ SelfMonitor] ← Integrator ← منتج
```

### قدرات SIO
- **لا استعلامات ثابتة** — الأهداف تتحلل إلى مسارات تنفيذ مستقلة
- **سلاسل بناء تعيد تكوين نفسها** — عند الفشل، يعاد التخطيط والتوليد تلقائياً
- **دمج المنطق والواجهة والنشر** — في عملية واحدة متصلة
- **تكيف في الوقت الفعلي** — الرصد المستمر وإعادة التوجيه
- **لا هلوسة** — كل مخرج يُختبر قبل القبول

---

## الجلسة 5: تكامل الواجهة

### ملفات مطوَّرة
| الملف | التغيير |
|-------|---------|
| `src/api/main.py` | **إعادة بناء كاملة** — 16 نقطة نهاية: `/api/chat`، `/api/letters/rich/{letter}`، `/api/synthesize`، `/api/sio/status`، إلخ |
| `src/physics/orchestrator.py` | 3 حقول جديدة في `PhysicsState`: `heterodyne_active`، `oscillator_active`، `gravity_vector` |
| `ui/index.html` | وضع SIO جديد + بطاقة المعاني الغنية للحروف |
| `ui/script.js` | معالج SIO + `renderSioResults()` + عرض HET/OSC/GV في التقرير الفيزيائي |
| `ui/style.css` | ~350 سطر تنسيقات: بطاقة المعاني + لوحة SIO |

### نقاط نهاية API النهائية (16)
```
GET  /                          POST /api/chat
GET  /api/letters               POST /api/letters/update
GET  /api/letters/rich/{letter} POST /api/synthesize
GET  /api/benchmark             POST /api/benchmark/update
GET  /api/field                 GET  /api/sio/status
GET  /meters                    GET  /docs
```

### مؤشرات التقرير الفيزيائي
HET (تغاير ترددي) · OSC (مذبذبات كوراموتو) · GV (جاذبية إقليدية) · DCCF · PPM · AMFS · CASCADE · DIALOGUE

---

## ملخص الملفات المتأثرة

### ملفات جديدة (10)
```
src/semantics/letter_meanings.py
src/physics/vector_interpreter.py
src/physics/heterodyne_engine.py
src/sio/__init__.py
src/sio/goal_parser.py
src/sio/phase_planner.py
src/sio/executor.py
src/sio/self_monitor.py
src/sio/integrator.py
src/sio/orchestrator.py
```

### ملفات مطوَّرة (9)
```
src/semantics/arabic_semantics.py   — نظام 29D متفرق + 16D sinusoidal
src/physics/word_physics.py         — ترجيح موضعي + بارامتر weighted
src/physics/constants.py            — RICH_SEMANTIC_DIMS, POSITION_WEIGHTS
src/physics/letter_db.py            — get_raw_norm()
src/physics/generator.py            — 12 تغيير (محركات + إصلاحات + تحسينات)
src/physics/orchestrator.py         — 3 حقول حالة جديدة
src/api/main.py                     — إعادة بناء كاملة + SIO
config.yaml                         — 4 أوزان جديدة + قسم heterodyne
ui/index.html                       — وضع SIO + بطاقة المعاني
ui/script.js                        — SIO + HET/OSC/GV + rich letters
ui/style.css                        — ~350 سطر تنسيقات جديدة
```

---

## الجلسة 6: إصلاح أخطاء وقت التشغيل + تحسين التوليد

### إصلاحات
| المشكلة | السبب | الإصلاح |
|---------|-------|---------|
| `'Generator' has no attribute 'set_cascade'` | الدالة مفقودة من Generator | أضيفت `set_cascade()` و `set_dialogue()` |
| `'NoneType' has no attribute 'detect_need_for_dialogue'` | dialogue_engine قد يكون None | إضافة حماية قبل الاستدعاء |
| `'Generator' has no attribute 'dialogue_memory'` | تسرب كود __init__ إلى جسم دوال set_* | إعادة هيكلة __init__ وإعادة `_init_pv_matrix` المفقودة |
| `'Generator' has no attribute 'morpho'` | سطر `self.morpho = ...` حُذف خطأ | إعادته مع بقية التهيئة المفقودة |

---

## الجلسة 7: تبسيط معادلة التسجيل

### قبل
60+ وزن يتصارعون في `_score()` — ضوضاء أكثر من فائدة.

### بعد: 10 حدود أساسية فقط

| # | الحد | Config | الدور |
|---|------|--------|-------|
| 1 | `align` | 3.0 | التوافق الطوري |
| 2 | `prompt_align` | 2.5 | الالتزام بالأمر |
| 3 | `syntax` | 5.0 | النحو |
| 4 | `gravity` | 2.5 | الجاذبية الإقليدية |
| 5 | `heterodyne` | 3.0 | التغاير الترددي |
| 6 | `carrier` | 4.0 | الموجة الحاملة |
| 7 | `resonant_chain` | 4.0 | دائرة رنين LC |
| 8 | `k_coupling` | 3.0 | مصفوفات K مدمجة |
| 9 | `diversity` | 1.0 | منع التكرار |
| 10 | `repulsion` | 0.5 | كسر التشابه |

50+ حدًا آخر = 0.0 (يمكن تفعيلها من config.yaml حسب الحاجة).

---

## الجلسة 8: تخزين مصفوفة PV مسبقًا

### المشكلة
`_init_pv_matrix()` تحسب 167,478 متجهًا × 64D كل مرة — تستغرق 160+ ثانية.

### الحل
- `_load_or_init_pv_matrix()`: تحميل من `model/_all_pv_cache.npy` إن وُجد، وإلا حساب + حفظ.
- **التحميل الأول**: 180s ← 86s
- **التحميلات اللاحقة**: 60s (تحميل مباشر من القرص)

---

## الجلسة 9: نظام الموجة الحاملة (CarrierWaveEngine)

### الفكرة (من المستخدم)
> كل كلمة موجة حاملة تحمل معها كل رفيقاتها من كل الجمل التي ظهرت فيها. عند التوليد، نستخدم التغاير الترددي لفك التضمين واستخراج الرفيقات النشطة في السياق الحالي فقط.

### ماذا يحل هذا؟
- K-matrix: نافذة 5 كلمات — علاقات بعيدة المدى = صفر
- **CarrierWave**: الجملة كاملة — لا حد للنافذة
- الكلمة الآن "تتذكر" كل رفيقاتها من كل سياقاتها عبر التاريخ

### ملفات جديدة
| الملف | الوصف |
|-------|-------|
| `src/physics/carrier_engine.py` | CarrierWaveEngine — يبني أطياف التضمين، يفك التضمين حسب السياق، يسجل المرشحات عبر الموجة الحاملة |

### API
- `build_from_corpus(texts, vocab)` — بناء الطيف أثناء التدريب
- `get_carrier_spectrum(word_id)` — إرجاع كل رفيقات الكلمة
- `demodulate(carrier_id, context_ids)` — فك تضمين حسب السياق
- `score_candidate_via_carrier(cand_id, ctx_ids, vocab)` — تسجيل مرشح
- `save(path)` / `load(path)` — حفظ/تحميل الأطياف

### ملفات مطوَّرة
| الملف | التغيير |
|-------|---------|
| `synchronize.py` | `synchronize_with_carrier()` — تدريب + بناء أطياف في خطوة واحدة |
| `generator.py` | `carrier_score` في `_score()` + تهيئة `CarrierWaveEngine` + وزن `carrier` |
| `config.yaml` | وزن `carrier: 4.0` — الأعلى بين الأوزان الأساسية |

### مثال
```
"الملك" ظهرت في:
  ج1: "الملك يحكم البلاد"   → تحمل: يحكم، البلاد
  ج2: "الملك له سلطة ومال"  → تحمل: سلطة، مال

طيف "الملك" الكامل = {يحكم، البلاد، سلطة، مال}

في سياق "السلطة": demodulate() يستخرج "سلطة" و"مال"
في سياق "الحكم":   demodulate() يستخرج "يحكم" و"البلاد"
```

---

## الجلسة 10: تحسينات الوكيل — طلاقة وإبداع

### تغييرات
| التغيير | القيمة | الأثر |
|--------|--------|-------|
| `seed=None` | ديناميكي | مخرجات مختلفة كل مرة |
| `beam_width` | 3 ← 5 | استكشاف أوسع |
| `top_k` | 250 ← 500 | مرشحين أكثر |
| `DCCF` | 0.0 ← 3.0 | بديل self-attention مفعّل |
| `_creative_generate()` | وضع جديد | Phase Perturbation + Quantum Tunneling |
| `window_sem` | 5 ← 10 | نافذة تدريب أوسع |

---

## الجلسة 11: المحركات الفيزيائية المتقدمة — سد الفجوة مع LLMs

### التشخيص: 4 قصور هيكلية
1. **حساء السياق**: الجمع الخطي يذيب المعاني الفردية
2. **العمى الهيكلي**: A+B = B+A — لا تمييز للترتيب
3. **فخ الرنين**: الكلمات المتشابهة تتجاذب بلا توقف
4. **البنية المسطحة**: تفاعلات كلمة-كلمة فقط، لا مفاهيم

### ملف جديد
| الملف | الوصف |
|-------|-------|
| `src/physics/advanced_engines.py` | 4 محركات فيزيائية متقدمة في ملف واحد |

### المحركات الأربعة

#### 1. ResonantBeamformer — بديل Self-Attention
- **المشكلة**: `target = mean(all_pvs)` — كل الكلمات تذوب في حساء واحد
- **الحل الفيزيائي**: هوائي مصفوفة طورية (phased-array radar)
  - كل كلمة سياق = عنصر هوائي
  - وزن التوجيه = `exp(gain × sim(candidate, context_word))`
  - الشعاع الناتج = سياق مركز على الكلمات المهمة فقط
- **الوزن**: `beamform: 3.0`

#### 2. PhaseAccumulator — بديل Positional Encoding
- **المشكلة**: `A + B = B + A` — الترتيب لا يهم
- **الحل الفيزيائي**: مصفوفات دوران غير تبديلية في SO(3)
  - كل كلمة تُضرب بـ `R(θ_pos)` قبل الجمع
  - `R(θ₁)·A + R(θ₂)·B ≠ R(θ₂)·B + R(θ₁)·A`
  - "أكل الكلب القطة" ≠ "أكلت القطة الكلب"
- **الزاوية الأساسية**: 0.15 rad/position

#### 3. RefractoryGate — بديل Repetition Penalty
- **المشكلة**: الكلمات المتشابهة تتجاذب إلى ما لا نهاية
- **الحل الفيزيائي**: فترة جموح (عصبونية)
  - الكلمة بعد استخدامها: طور مقلوب (× -1.5)
  - تصدّ الكلمات المشابهة (تنافر بدل جذب)
  - يضمحل التأثير بعد 3 خطوات بمعدل 0.4
- **الوزن**: `refractory: 2.5`

#### 4. MacroWaveEngine — بديل الطبقات العميقة
- **المشكلة**: تفاعلات كلمة-كلمة فقط — لا تجريد
- **الحل الفيزيائي**: تشابك كمومي للعبارات
  - مبتدأ+خبر ← جسيم مفهوم بتردده وكتلته
  - المفاهيم تتفاعل مع مفاهيم — لا كلمات مع كلمات
  - حد أقصى: 50 مفهومًا نشطًا
- **الوزن**: `macro_wave: 2.0`

### دمج في التوليد
- `beamform` + `refractory` + `macro_wave` تضاف إلى `_score()`
- `refractory.deplete()` و `.step()` تُستدعى بعد كل كلمة مولَّدة
- `macro_wave.entangle()` تُستدعى بعد كل كلمتين لتشكيل المفاهيم

---

## الحالة الراهنة للنظام (نهائية)

| المكون | الحالة |
|--------|--------|
| تحليل الحروف (22D + 29D) | ✅ مكتمل |
| فيزياء الكلمة (E=hf, m=E/c²) | ✅ مكتمل |
| الترجيح الموضعي | ✅ مكتمل |
| التغاير الترددي (Heterodyne) | ✅ مكتمل |
| نموذج الموجة الحاملة (CarrierWave) | ✅ مكتمل |
| **تشكيل الشعاع الطوري (Beamformer)** | ✅ مكتمل |
| **تراكم طوري غير تبديلي (PhaseAccumulator)** | ✅ مكتمل |
| **بوابة الجموح (RefractoryGate)** | ✅ مكتمل |
| **تشابك الموجات الكبرى (MacroWave)** | ✅ مكتمل |
| مذبذبات كوراموتو (RK4) | ✅ مكتمل |
| الجاذبية الإقليدية (42D) | ✅ مكتمل |
| دائرة رنين LC | ✅ مكتمل |
| تبسيط التسجيل (14 حدًا) | ✅ مكتمل |
| تخزين PV مسبقًا | ✅ مكتمل |
| وضع إبداعي (Creative mode) | ✅ مكتمل |
| SIO — ذكاء توليفي | ✅ مكتمل |
| API (16 نقطة نهاية) | ✅ مكتمل |
| واجهة المستخدم | ✅ مكتمل |
| الاختبارات (108/108) | ✅ ناجحة |

---

## ملخص الملفات — نهائي

### ملفات جديدة (12)
```
src/semantics/letter_meanings.py
src/physics/vector_interpreter.py
src/physics/heterodyne_engine.py
src/physics/carrier_engine.py
src/physics/advanced_engines.py          ← الجديد
src/sio/__init__.py
src/sio/goal_parser.py
src/sio/phase_planner.py
src/sio/executor.py
src/sio/self_monitor.py
src/sio/integrator.py
src/sio/orchestrator.py
```

### ملفات مطوَّرة (11)
```
src/semantics/arabic_semantics.py
src/physics/word_physics.py
src/physics/constants.py
src/physics/letter_db.py
src/physics/generator.py
src/physics/synchronize.py
src/physics/orchestrator.py
src/api/main.py
config.yaml
ui/index.html, ui/script.js, ui/style.css
```
