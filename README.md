# مِرنان V7 — Physics Orchestrator

**Physics-Inspired Dynamical Language Model** — توليد اللغة العربية والإنجليزية من الموجات الطيفية، فيزياء الحروف، ميكانيكا الكم، والجاذبية الدلالية، بدون شبكات عصبية أو backpropagation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Modules: 50+](https://img.shields.io/badge/Modules-50+-purple.svg)](src/physics/)
[![Vocabulary: 167K](https://img.shields.io/badge/Vocabulary-167K-green.svg)](model/)

---

## المبدأ

الحرف مذبذب بتردد ذاتي ω₀ في فضاء 64 بُعداً. الكلمة = حزمة موجية (wave packet) من تداخل مذبذبات حروفها. المعنى = رنين طوري بين الكلمات. لا embeddings ولا backprop — فقط موجات.

```
ψ_word(t) = Σ letter A₀ · sin(ω₀ · t + φ₀)
K(w₁, w₂) = PMI × phase_similarity × co_occurrence  ← ارتباط دلالي فيزيائي
score(w) = Σ 40+ مصطلحاً فيزيائياً  ← تقييم كل مرشح
φ_64 = [φ_22, root(8), extra(6), φ_syn(6), φ_sem(16), φ_prag(6)]
```

---

## التشغيل

```bash
pip install -r requirements.txt

# تدريب كامل
python train.py

# تدريب تزايدي (إضافة بيانات بدون إعادة تدريب)
python assimilate.py --data new_data.txt

# واجهة تفاعلية
python cli.py -i

# توليد
python cli.py "السلام عليكم" --mode dialogue
python cli.py "الصياد في" --mode quantum --report
python cli.py "تخيل عالماً" --mode creative --max-words 15
python cli.py "يا ليت قومي يعلمون" --mode poetic --meter kamil

# خادم API
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### برمجياً
```python
import model  # استيراد النموذج مباشرة
from src.physics.generator import Generator
from src.physics.orchestrator import PhysicsOrchestrator

data = model.load_model()
gen = Generator(data['vocab'], data['K_sem'],
                syntax_field=data['syntax'], K_dialogue=data['K_dial'])
orch = PhysicsOrchestrator(gen)

# حوار
orch.set_dialogue(True)
print(orch.generate('السلام عليكم', mode='dialogue'))  # → ورحمه الله
print(orch.generate('شكراً', mode='dialogue'))           # → العفو جزيلاً
print(orch.generate('ما اسمك', mode='dialogue'))         # → اسمي مِرنان

# معرفة
print(orch.generate('ما هي الفيزياء', mode='standard'))  # → والكموميه
```

---

## النظام الحواري

مِرنان V7 يقدّم حواراً بلا قوالب: **مصفوفتان تعملان معاً بتناغم**.

| المكوّن | الوظيفة |
|---------|---------|
| `K_dialogue` | مصفوفة حوارية (window=2) تعلّم أنماط الحوار فقط (شكراً → العفو) |
| `K_sem` | مصفوفة المعرفة الرئيسية — تبقى متاحة للإجابة عن الأسئلة |
| **الرنين المدمج** | blend ديناميكي بين K_sem و K_dialogue في `_resonance_candidates` |
| **مكافأة K_dialogue** | قيمة خام من K_dialogue تُضاف كـ bonus: K_dial[شكراً, العفو]=574 → +57.4 |
| **Anti-completion** | يمنع ترديد كلمات المستخدم (threshold 0.97) |
| **تصنيف دلالي** | 12 فئة: حيوان، نبات، لون، علم، كلمة_حوار... مكافأة 0.3 للتوافق |

### أمثلة حوارية

| الإدخال | المخرجات |
|---------|----------|
| السلام عليكم | ورحمه الله |
| كيف الحال | بخير انا |
| شكراً | العفو جزيلاً |
| مع السلامة | امان الله |
| ما اسمك | اسمي مرنان |
| hello | welcome are |
| ما هي الفيزياء (standard) | والكموميه |

---

## النموذج — ملفات .npz + vocab.py

```
model/
├── __init__.py       # load_model(), add_word()
├── vocab.py          # WORD2ID = {167K كلمة} — مقروء وقابل للتوسع
├── K_sem.npz         # مصفوفة K الدلالية (23 MB)
├── K_syn.npz         # مصفوفة K التركيبية (12 MB)
├── K_dial.npz        # مصفوفة K الحوارية (10 KB)
├── syntax.py         # القواعد النحوية
└── contextual_spectra.npy  # أطياف سياقية (اختياري)
```

- **vocab.py** يبقى Python — ديناميكي، مقروء، قابل للتوسع
- **K matrices** كـ `.npz` — أسرع 60× من base64+zlib في التحميل (4.7 ثانية)
- **استيراد مباشر:** `import model; data = model.load_model()`

---

## التدريب التزايدي (Incremental Learning)

بدلاً من إعادة التدريب من الصفر عند إضافة بيانات:

```bash
python assimilate.py --data new_data.txt
python assimilate.py --data data/*.txt --alpha 0.15
```

الآلية:
1. يمسح النص الجديد لكلمات غير موجودة في المعجم
2. يضيفها إلى vocab ويوسّع مصفوفات K
3. يدمج: `K_updated = K_old × (1−α) + K_new × α`
4. يحدّث SyntaxField ويحفظ النموذج

---

## النظام الفيزيائي (المحركات)

| المحرك | الملف | الوظيفة |
|--------|-------|---------|
| K_sem | `synchronize.py` | ارتباط دلالي (PMI + طور) |
| K_syn | `synchronize.py` | ارتباط تركيبي (window=2) |
| K_dialogue | `synchronize.py` | ارتباط حواري (window=2) |
| SyntaxField | `grammar_field.py` | قواعد نحوية (bigram، تعريف، وصل) |
| CausalEngine | `causal_engine.py` | علاقات سببية (O(nnz)) |
| SpectralMemory | `spectral_memory.py` | توقيع طيفي عالمي |
| IntentDetector | `intent_detector.py` | كشف قصد المستخدم |
| AssociativeMemory | `associative_memory.py` | ذاكرة ترابطية حوارية |
| DialogueMemory | `dialogue_memory.py` | ذاكرة جلسة (20 دورة) |
| SemanticCategories | `semantic_categories.py` | تصنيف دلالي (12 فئة) |
| SpectralContext | `spectral_context.py` | طيف سياقي (مجموع PV مرجح) |

### المحركات المتقدمة لكسر القيود التقليدية (Advanced Engines)

مجموعة محركات فيزيائية حديثة (`advanced_engines.py`) مصممة لحل مشكلات الحتمية والتكرار وضعف التركيز:

| المحرك | البديل عن في الـ LLM | الوظيفة |
|--------|----------------------|---------|
| **ResonantBeamformer** | Self-Attention | يعامل الكلمات كهوائيات مصفوفة طورية لتوجيه "شعاع الرنين" نحو الكلمات الأكثر صلة بالسياق، وتجاهل الضجيج. |
| **PhaseAccumulator** | Positional Encoding | يضيف دورانات في فضاء SO(3) للمتجهات أثناء التراكم لتشفير ترتيب الكلمات (A+B ≠ B+A). |
| **RefractoryGate** | Repetition Penalty | يحاكي فترة جموح العصبون؛ الكلمة المنتجة يُقلب طورها فتتنافر مع مثيلاتها لمنع التكرار (تضمحل تدريجياً). |
| **PotentialCascadeLayer** | Greedy Decoding | يخلق بئر جهد تراكمي حيث تهوي الكلمة التالية حتمياً إلى أعمق نقطة فيه بدون Sampling احتمالي. |
| **ThermalChaosEngine** | Temperature/Top-P | يولد تشويشاً حرارياً (الحركة البراونية) في متجهات الطور لإنتاج عشوائية إبداعية محكومة فيزيائياً تكسر الحتمية المطلقة. |
| **QuantumEntanglement** | Long-range Attention | ينشئ جاذبية فائقة لا تضمحل بالمسافة بين الكلمات المتشابكة دلالياً، مما يعطي النظام قدرة على التذكر السياقي العميق. |
| **MolecularBinder** | BPE Tokenization | يدمج الكلمات المتجاورة المترابطة بقوة (مثل: الأمم+المتحدة) لتكوين جزيء لغوي ذو متجه وكتلة مجمعة لتحسين النحو التركيبي. |

---

## أنماط التوليد (Generation Modes)

مِرنان يدعم عدة أنماط توليد تناسب طبيعة الطلب، أهمها:

- **الوضع الإبداعي (`creative`)**: يعالج مشكلة الحتمية عبر "فوضى متحكمة". يجمع بين:
  - **اضطراب طوري (Phase Perturbation)**: يحرف المتجهات بزاوية عشوائية صغيرة (يحاكي تقلبات كمومية).
  - **نفق كمومي (Quantum Tunneling)**: احتمال 5% للقفز دلالياً إلى كلمات بعيدة (ينتج استعارات مجازية).
  - **حرارة Boltzmann عالية**: أخذ عينات احتمالي (Sampling) بدل الاختيار الحتمي.
- **وضع الحوار (`dialogue`)**: يستخدم K_dial للاستجابة المباشرة (السلام عليكم → وعليكم السلام).
- **الوضع الشعري (`poetic`)**: يولد مقاطع محكومة بـ 16 بحراً من بحور الشعر العربي وقافية محددة.
- **الوضع الكمومي (`quantum`)**: يبني تراكباً من 15 فرعاً وينهار عند تحقق شرط الإنتروبيا (S_crit).

---

## تحسينات الطلاقة والتنوع

تم تحسين قدرات مِرنان لمقاربة الطلاقة في الـ LLMs دون التخلي عن فيزياء النظام:
- **بذرة ديناميكية (Dynamic Seed)**: كل تشغيل ينتج نصاً فريداً بفضل تفعيل بذرة الوقت العشوائية بشكل افتراضي.
- **نوافذ استشعار أوسع**: زيادة `window_sem` إلى 10 و `window_syn` إلى 4 لرؤية سياق أبعد.
- **تفعيل DCCF**: استخدام اقتران السحابة المعرفية كبديل فيزيائي لآلية الـ Self-Attention.

---

## الحروف النحوية (Particle System)

تصنيف 70+ حرفاً نحوياً في 11 فئة (`src/grammar/particles.py`):
جر، نصب اسمي/فعلي، جزم، عطف، استفهام، شرط، نفي، تعليل، تضاد، توكيد.

تأثيرها: تُضرب entries K بـ `0.15` لتحييد هيمنتها على المصفوفة.

---

## التصنيف الدلالي (Semantic Categories)

ملف `src/physics/semantic_categories.py` — يصنف الكلمات إلى 12 فئة:

| الفئة | أمثلة |
|-------|-------|
| حيوان | أسد، نمر، فيل، نسر |
| نبات | شجر، تفاح، ورد، قمح |
| جماد | حجر، حديد، ذهب، زجاج |
| لون | أحمر، أخضر، أزرق، أبيض |
| فعل_حركي | جرى، مشى، قفز، سبح |
| زمان | يوم، شهر، سنة، ساعة |
| مكان | بيت، مدرسة، جبل، بحر |
| صفة | جميل، طويل، قوي، ضعيف |
| طعام | خبز، لحم، فاكهة، عسل |
| علم | فيزياء، كيمياء، طب، برمجة |
| كلمة_حوار | شكراً، العفو، مرحباً، أهلاً |

مدمجة في `_score` — مكافأة 0.3 للكلمة إذا كانت من نفس فئة سياقها.

---

## المقارنة مع LLMs

| المعيار | LLM (GPT-4, Llama) | مِرنان V7 |
|---------|-------------------|-----------|
| الشفافية | صندوق أسود | كل كلمة مبررة بطورها وجاذبها |
| الاستهلاك | GB VRAM, GPU ساعات | MB RAM, CPU, ثوانٍ |
| التعلم | Backprop | مزامنة + رنين طوري |
| التحميل | دقائق (GPU) | 4.7 ثانية (CPU) |
| الحوار | إكمال إحصائي | K_dialogue + كشف قصد + تصنيف دلالي |
| التوسع | إعادة تدريب كامل | تزايدي — تضاف بيانات بدون خسارة |
| التنسيق | .bin, .safetensors | .npz + vocab.py (ديناميكي) |

---

## التراخيص
MIT — استخدام حر للأغراض البحثية والتطبيقية.

## تصفير النموذج

```bash
Remove-Item -Recurse -Force model\K_*.npz, model\vocab.py, model\syntax.py, model\__init__.py
Remove-Item -LiteralPath data\dialogue_corpus.txt
python train.py --rebuild-dialogue
```

## أوامر التدريب

```bash
# تدريب كامل
python train.py
# مع بناء كوربس الحوار
python train.py --rebuild-dialogue
# مع تخطي الاختبار (أسرع)
python train.py --skip-test
# تدريب تزايدي
python assimilate.py --data new_data.txt --alpha 0.15
# خادم API
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
