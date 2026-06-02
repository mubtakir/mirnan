# 05 — تدريب مرنان وبناء قاعدته المعرفية

**المستوى:** متوسط-متقدم  
**الوقت:** 20 دقيقة  
**المتطلب:** الدرس 04

---

## التدريب ≠ backpropagation

في النماذج التقليدية، "التدريب" يعني: تشغيل backpropagation على ملايين الأمثلة لضبط مليارات المعاملات.

في مرنان، "التدريب" يعني: **بناء مصفوفات التزامن (K matrices)** و **بناء القاعدة المعرفية (KB)**.

لا توجد دالة خسارة (loss function). لا يوجد محسّن (optimizer). هناك **مزامنة فيزيائية**.

## أنواع التدريب في مرنان

| النوع | الأمر | ماذا يفعل؟ | المدة |
|-------|-------|-----------|------|
| تدريب أساسي | `python train.py` | بناء K_sem, K_syn, أطياف سياقية | دقائق |
| تدريب تزايدي | `python assimilate.py --data new.txt` | تحديث K والمتجهات دون إعادة تدريب | ثواني |
| تعلم مستمر | تلقائي أثناء التوليد | Hebbian reinforcement | لحظي |
| بناء KB | `kb.load_curated_facts(...)` | تحميل حقائق من JSON | ~0.5 ثانية |

## ١. التدريب الأساسي: بناء مصفوفات K

```bash
python train.py
```

### ماذا يحدث؟

١. **قراءة النصوص** من `data/corpus.txt` و `data/dialogue_corpus.txt`

٢. **بناء K_sem (دلالية)** — من تشارك الكلمات في نافذة 10 كلمات:
```python
# لكل زوج كلمات يظهران معاً:
K_sem[w1][w2] = PMI(w1, w2) × phase_similarity(v1, v2) × co_occurrence_count
```

٣. **بناء K_syn (نحوية)** — من تشارك الكلمات في نافذة 4 كلمات (علاقات نحوية مباشرة):
```python
K_syn[w1][w2] = transition_probability × syntax_alignment
```

٤. **بناء K_dial (حوارية)** — من نصوص الحوار (نافذة 2)

٥. **بناء الأطياف السياقية** — توقيعات FFT للسياقات حول كل كلمة

٦. **بناء المصفوفة السببية** — علاقات السبب-النتيجة من النص

### ملاحظات مهمة

- مصفوفات K هي مصفوفات **متفرقة (sparse)** — معظم القيم صفر
- تستخدم PMI (Pointwise Mutual Information) لقياس قوة الارتباط
- التشابه الطوري `phase_similarity` يضبط الارتباط فيزيائياً
- K_syn و K_sem **لا تُستخدمان الآن في اختيار المرشحين** (تم تصفيرهما إلى 0.0 في config.yaml). الاختيار فيزيائي بحت بالجاذبية. لكنهما موجودان كمرجع.

## ٢. التدريب التزايدي

```bash
python assimilate.py --data my_new_texts.txt
```

يضيف نصوصاً جديدة **دون إعادة تدريب كامل**:

- يُحدّث مصفوفات K تزايدياً
- يُضبط المتجهات الطورية للكلمات الجديدة
- لا يمس الكلمات الموجودة

## ٣. التعلم المستمر (أثناء التوليد)

أثناء كل جلسة توليد، يتعلم مرنان بشكل مستمر:

```python
# PhaseReinforcement: تعزيز طوري
pv_new = pv_old + 0.05 × (target - pv_old) × reward

# PhaseEvolution: مزامنة هيبيانية
pv_shifted = pv + 0.03 × (context_pv - pv)

# AssociativeMemory: تخزين أنماط الحوار
memory.store(intent="QUESTION", topic_pv=topic, response=answer)
```

كلما تفاعل المستخدم مع مرنان، كلما "تعلم" أنماطه وتكيّف معها.

## ٤. بناء القاعدة المعرفية (KB)

القاعدة المعرفية **مستقلة عن التدريب**. يمكن بناؤها وتوسيعها في أي وقت.

### من أين تأتي الحقائق؟

١. **استخراج آلي** من النصوص (الجمل التي تحتوي "هو"، "في"، "يستطيع"...):
```python
kb.build_from_texts(corpus_texts, vocab, pv_fn, max_facts=500)
```

٢. **حقائق منسقة يدوياً** (ملف JSON):
```python
kb.load_curated_facts("data/facts_expanded.json", vocab, pv_fn)
```

### تنسيق ملف الحقائق

```json
{
  "facts": [
    {"subject": "باريس", "relation": "عاصمة", "object": "فرنسا"},
    {"subject": "ثلج", "relation": "يصبح_بالتسخين", "object": "ماء"},
    {"subject": "سكين", "relation": "مصنوع_من", "object": "معدن"}
  ]
}
```

### أنواع العلاقات المتاحة

`IS_A`, `LOCATED_IN`, `CAPITAL_OF`, `MADE_OF`, `PART_OF`, `USED_FOR`, `BECOMES_WHEN`, `PRODUCES`, `HAS_PROPERTY`, `CAPABLE_OF`, `SYNONYM`, `CURATED`

### كيف تستعلم القاعدة؟

```python
# استعلام اتجاهي (فاعل → مفعول)
kb.query_by_word("باريس")  # → [("فرنسا", 1.0)]

# استعلام ثنائي الاتجاه (فاعل أو مفعول)
kb.query_bidirectional("فرنسا")  # → [("باريس", 1.0), ("أوروبا", 1.0)]
```

## ٥. توسيع المفردات

إذا كانت كلمة تحتاجها غير موجودة في المعجم:

١. أضفها إلى `model/vocab_supplemental.json`:
```json
{"words": ["كلمة_جديدة", "أخرى"]}
```

٢. أو برمجياً:
```python
vocab.add("كلمة_جديدة")
```

## تجربة عملية

```bash
# ١. تدريب أساسي
python train.py

# ٢. أضف بعض الحقائق
python -c "
from src.physics.holographic_kb import HolographicKB
from src.physics.word_physics import compute_extended_phase_vector
from model import load_model
data = load_model()
kb = HolographicKB(data_dir='data')
kb.store_fact(
    compute_extended_phase_vector('القاهرة'),
    compute_extended_phase_vector('مصر'),
    'CAPITAL_OF',
    subj_word='القاهرة', obj_word='مصر'
)
kb.save()
"

# ٣. اسأل مرنان (نمط الاستدلال)
python cli.py "القاهرة في مصر. مصر في أفريقيا. أين القاهرة" --mode reason
```
