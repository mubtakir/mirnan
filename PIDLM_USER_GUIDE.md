# دليل المستخدم — مرنان V6 (Physics Orchestrator)

نظام توليد لغة عربية وإنجليزية من الموجات الطيفية وفيزياء الحروف والتراكب الكمومي — بدون شبكات عصبية.

---

## 1. التشغيل السريع

```bash
pip install -r requirements.txt

# واجهة أوامر تفاعلية
python cli.py -i

# توليد سريع
python cli.py "السلام عليكم" --mode quantum --report

# شعر عربي
python cli.py "يا ليت قومي يعلمون" --mode poetic --meter kamil

# مع ضبط فيزيائي
python cli.py "الصياد في" --beta 2.5 --k_B 0.8
```

لتشغيل واجهة الويب:
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

---

## 2. الوضع التفاعلي (CLI)

```bash
python cli.py -i
```

أوامر حية أثناء التوليد:

| الأمر | المفعول |
|-------|---------|
| `/beta 3.0` | ضبط β (الحرارة الفيزيائية) |
| `/k_B 0.5` | ضبط k_B (ثابت بولتزمان) |
| `/mode poetic` | تغيير وضع التوليد |
| `/report` | طباعة تقرير فيزيائي كامل |
| `/history` | آخر 10 توليدات |
| `/reset` | إعادة تعيين الحالة الفيزيائية |
| `/dialogue ON|OFF` | تفعيل/إلغاء وضع الحوار (يمنع الاستكمال الإحصائي) |

مثال جلسة تفاعلية:
```
> /beta 3.5
β = 3.50
> /mode poetic
الوضع = poetic
> يا ليت قومي يعلمون
  ↳ يا ليت قومي يعلمون ما فعلوا
> /report
==================================================
         التقرير الفيزيائي
==================================================
  الوضع:         poetic
  الإنتروبيا:    0.23
  β:             3.50
  DCCF اقتران:   0.41
  PPM حقل:       0.62
  AMFS مركزية:   0.55
==================================================
```

---

## 3. التوليد البرمجي (Python)

```python
import os
from src.physics.synchronize import synchronize
from src.physics.orchestrator import PhysicsOrchestrator, Generator

# تحميل النموذج
vocab, K_syn, K_sem, K_conc, texts = synchronize()
gen = Generator(vocab, K_sem, K_syn=K_syn, K_conc=K_conc, corpus_texts=texts)
orch = PhysicsOrchestrator(gen)

# توليد مع كشف تلقائي للوضع
result = orch.generate('السلام عليكم')
print(result)

# مع وضع محدد وتحكم فيزيائي
result = orch.generate('يا ليت قومي', mode='poetic', poetic_meter='kamil')
print(result)

# ضبط المعاملات الفيزيائية حياً
orch.adjust_beta(3.0)
orch.adjust_k_B(0.5)
result = orch.generate('العلم', mode='multiverse')

# تفعيل طبقة الهوي التراكمي
orch.set_cascade(True, lambda_cascade=1.8)
result = orch.generate('العلم', mode='quantum')

# تفعيل وضع الحوار — يمنع الاستكمال الإحصائي
orch.set_dialogue(True)
result = orch.generate('السلام عليكم', mode='dialogue')
# ↳ وعليكم السلام ورحمة الله
result = orch.generate('كيف حالك', mode='dialogue')

# تقرير فيزيائي
report = orch.get_report()
print(report)
```

---

## 4. الابتكارات الجديدة في V6

| الابتكار | التفعيل | شرح |
|---------|---------|------|
| **DCCF — Dynamic Contextual Coupling Field** | تلقائي | مصفوفة اقتران لحظي من سياق التوليد فقط — بديل self-attention الفيزيائي |
| **PPM — Prompt Phase Modulation** | تلقائي | حقل طوري يبتلع الـ prompt ويضمحل — محاكاة فيزيائية لـ In-Context Learning |
| **AMFS — Adaptive Mass & Frequency Shift** | تلقائي | تعديل الكتلة والتردد حسب السياق — contextual embeddings فيزيائياً |
| **PhysicsOrchestrator** | تلقائي | يكتشف الوضع تلقائياً (شعر ← رياضي ← كود ← عادي) ويدير كل المحركات |
| **PhaseReinforcement** | تلقائي | تعزيز طوري ذاتي — تقوى المسارات الناجحة وتضعف الضعيفة |
| **16 بحراً عربياً** | `--meter` | طويل، مديد، بسيط، وافر، كامل، هزج، رجز، رمل، سريع، منسرح، خفيف، مضارع، مقتضب، مجتث، متقارب، متدارك |
| **كشف البحر تلقائياً** | `detect_meter()` | يعرف البحر من كلمات النص |
| **CLI تفاعلية** | `python cli.py -i` | تحكم فيزيائي حي: /beta, /k_B, /mode, /report |
| **PotentialCascadeLayer** | `orch.set_cascade(True)` | طبقة هوي جهدي تراكمي حتمي — كل كلمة تهوي لأعمق بئر جهد. لا softmax ولا temperature |
| **DialogueEngine** | `orch.set_dialogue(True)` أو `--dialogue` | محرك حوار يمنع الاستكمال الإحصائي — يكشف القصد، يسترجع قالب الرد، يُلقّح ببادئة رد، يتوقف عند أول جملة |

---

## 5. أنماط التوليد

| النمط | الوصف | الأداء |
|-------|-------|--------|
| `auto` | كشف تلقائي — يختار الوضع حسب الـ prompt | — |
| `wave` | PGN pathfinding على الرسم البياني الطيفي | 0.015s |
| `standard` | بحث شعاعي كلاسيكي | 0.17s |
| `quantum` | تراكب كمومي — مسارات متوازية مع انهيار موجة | 1.32s |
| `multiverse` | أكوان متوازية — أغنى مخرجات | 2.83s |
| `poetic` | توليد مع 16 بحراً عربياً وقافية | 0.50–1.50s |
| `dialogue` | حوار قصدي — يكشف القصد، يسترجع الرد المناسب، يمنع الاستكمال الإحصائي | 0.15–0.30s |

---

## 6. ضبط المعاملات الفيزيائية

| المعامل | التأثير | النطاق | القيمة الافتراضية |
|---------|---------|--------|-------------------|
| β (beta) | حرارة التوليد — أعلى = أكثر تركيزاً | 0.1–10.0 | 2.0 |
| k_B | ثابت بولتزمان — أعلى = أكثر عشوائية | 0.1–10.0 | 1.0 |
| DCCF weight | قوة الاقتران الديناميكي | 0–5 | 2.0 |
| PPM weight | قوة الحقل الخارجي | 0–5 | 1.5 |
| AMFS weight | قوة تعديل الكتلة/التردد | 0–5 | 1.5 |
| Cascade | شدة طبقة الهوي التراكمي | 0–5 | 1.5 (وزن), 1.8 (λ) |

### 6.1 API — POST /api/chat

| معامل | النوع | الوصف |
|-------|-------|-------|
| `prompt` | string | النص المدخل |
| `mode` | string | وضع التوليد (auto, standard, wave, quantum, multiverse, poetic, code, dialogue) |
| `cascade` | bool | تفعيل طبقة الهوي التراكمي (true/false) |
| `cascade_strength` | float | قوة λ للطبقة (افتراضي 1.8) |
| `dialogue` | bool | تفعيل وضع الحوار — يمنع الاستكمال الإحصائي ويولّد رداً مستقلاً (true/false) |

---

## 7. الشعر العربي

```bash
# مع بحر محدد
python cli.py "يا ليت قومي يعلمون" --mode poetic --meter kamil

# مع كشف تلقائي للبحر
python cli.py "ألا ليت الشباب يعود يوماً" --mode poetic
```

البحور الـ 16 المدعومة:
طويل، مديد، بسيط، وافر، كامل، هزج، رجز، رمل، سريع، منسرح، خفيف، مضارع، مقتضب، مجتث، متقارب، متدارك

---

## 8. الاختبارات

```bash
pytest tests/ -v
# 108 تأكيد — 0 تراجعات
```
