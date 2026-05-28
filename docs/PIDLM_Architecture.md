# معمارية mirnan V6 — Physics Orchestrator

## 1. نظرة عامة

محرك mirnan V6 يولد النص العربي والإنجليزي عبر 28 ابتكاراً فيزيائياً-موجياً-رمزياً:

1. **DCCF** — حقل اقتران ديناميكي لحظي (بديل self-attention)
2. **PPM** — حقل طوري خارجي يضمحل (In-Context Learning فيزيائي)
3. **AMFS** — تعديل الكتلة والتردد حسب السياق
4. **PhysicsOrchestrator** — موحّد مركزي يدير كل المحركات
5. **PhaseReinforcement** — تعزيز طوري ذاتي (تعلّم بدون backprop)
6. **16 بحراً عربياً** — كامل البحور الـ 16 مع كشف تلقائي
7. **PotentialCascadeLayer** — هوي جهدي تراكمي حتمي: كل كلمة تهوي لأعمق بئر جهد في الحقل التراكمي
8. **DialogueEngine** — محرك حوار يمنع الاستكمال الإحصائي: يكشف القصد، يسترجع الرد، يُلقّح المولد ببادئة
9. **Spectral Wave Engine** — FFT, K_spectral, sidebands, adaptive filter
10. **PhysicsGenerativeNetwork (PGN)** — pathfinding على رسم بياني للرنين الطيفي
11. **RAM** — ذاكرة جواذب طورية
12. **Quantum Superposition** — تراكب كمومي وانهيار موجة
13. **Vectorized Gravity** — جاذبية دلالية فائقة السرعة
14. **Pragmatic Binding** — فضاء قصدي 6D وطاقة ربط
15. **Phase Attention** — انتباه طوري ديناميكي
16. **WeightResonanceEngine (عربي 14 وزناً)**
17. **English Morphology + Grammar + Weight**
18. **Physics Report**
19. **EntropyGate**
20. **SyntaxField 6D** (عربي + إنجليزي)
21. **Symbolic Bridge + MorphoPhasic**
22. **Bilingual Support**
23. **Interactive Physics Dashboard**
24. **CLI تفاعلية** — تحكم فيزيائي حي

## 2. المكونات

| المكون | الملف | أبرز الدوال |
|--------|-------|-------------|
| الثوابت | `constants.py` | PHASE_DIM=22, ROOT_DIMS=8, EXTRA_DIMS=6, SYNTAX_DIMS=6, SEMANTIC_DIMS=16, PRAGMATIC_DIMS=6, TOTAL_DIM=64 |
| الحروف | `letter_db.py` | 30 حرفاً عربياً + 26 إنجليزياً + /ŋ/ + operator + ω₀ |
| فيزياء الكلمة | `word_physics.py` | compute_word_phase_vector, compute_extended_phase_vector, dress, compute_word_mass, compute_word_energy |
| الموجات الطيفية | `spectral_wave_engine.py` | compute_word_wave(), wave_at(), wave_spectrum(), SpectralCouplingMatrix, adaptive_context_filter(), PhysicsGenerativeNetwork (find_path()), PhysicsTranslator (search()) |
| DCCF | `dccf.py` | **جديد V6** — build_coupling(), get_context_boost() — اقتران طوري لحظي باضمحلال المسافة |
| PPM | `ppm.py` | **جديد V6** — absorb(), score(), step(), reset() — حقل خارجي يضمحل |
| AMFS | `amfs.py` | **جديد V6** — adapt_word() — تعديل كتلة/تردد حسب السياق |
| التنسيق | `orchestrator.py` | **جديد V6** — PhysicsOrchestrator.generate(), _detect_mode(), get_report(), adjust_beta(), adjust_k_B() |
| التعزيز | `phase_reinforcement.py` | **جديد V6** — reinforce(), apply(), weaken(), reinforce_sentence() |
| الهوي التراكمي | `potential_cascade.py` | **جديد V6** — PotentialCascadeLayer.compute_score() — جهد تراكمي حتمي مع Phase Lock Gate, Syntax Wall, Pauli Repulsion |
| الحوار | `dialogue_engine.py` | **جديد V6** — DialogueEngine.compute_dialogue_score(), detect_need_for_dialogue(), _dialogue_generate() — كشف القصد، استرجاع الرد، إلقاح ببادئة، إيقاف عند أول جملة |
| الشعر | `poetic_gravity.py` | **مُحدّث V6** — 16 بحراً عربياً + detect_meter() + sentence_resonance() |
| الإنجليزي | `english_morpheme.py` | EnglishMorphology (analyze, get_pos, get_stem, compute_morph_phase), EnglishGrammarEngine, EnglishWeightResonance |
| الوزن العربي | `weight_resonance.py` | WeightResonanceEngine: resonance(), transition_score() — 14 وزناً |
| الجاذبية | `gravity.py` | gravitational_force(G·m₁m₂/r²) |
| المذبذبات | `oscillator.py` | simulate() → RK4 |
| النحو | `syntax_field.py` | compute_syntax_vector() — عربي (verb/noun/prep/part/conj/kana) + إنجليزي |
| الذاكرة | `ram_core.py` | AttractorMemory: observe(), resonate(), retrieve_context() |
| الانتروبيا | `entropy_gate.py` | EntropyGate: compute_S(), evaluate() |
| الجسر الرمزي | `symbolic_bridge.py` | 6 rules: نفي، عطف، جر، تفضيل، استفهام، شرط |
| الصرف العربي | `morpho_phasic.py` | MorphoPhasicEngine: analyze(), compute_morph_phase(), score(), transition_score() |
| القصد | `pragmatic_field.py` | PragmaticBindingEngine: detect_intent_frame(), compute_binding_energy() |
| المزامنة | `synchronize.py` | synchronize() → (vocab, K_syn, K_sem, K_conc, corpus_texts), save_k_mmap(), load_k_mmap() |
| التوليد | `generator.py` | Generator: generate() مع 6 أنماط, _score() مع 23+ معياراً, get_physics_report() |
| CLI | `cli.py` | **جديد V6** — واجهة أوامر تفاعلية: --mode, --beta, --k_B, --meter, --report, -i |
| API | `src/api/main.py` | FastAPI: POST /api/chat — mode, prompt, max_words |

## 3. ملفات جديدة في V6

| الملف | الوظيفة |
|------|---------|
| `src/physics/dccf.py` | Dynamic Contextual Coupling Field — بديل self-attention فيزيائي |
| `src/physics/ppm.py` | Prompt Phase Modulation — In-Context Learning فيزيائي |
| `src/physics/amfs.py` | Adaptive Mass & Frequency Shift — contextual embeddings فيزيائية |
| `src/physics/orchestrator.py` | PhysicsOrchestrator + PhysicsState — موحّد مركزي |
| `src/physics/phase_reinforcement.py` | PhaseReinforcement — تعزيز طوري ذاتي |
| `src/physics/potential_cascade.py` | PotentialCascadeLayer — هوي جهدي تراكمي حتمي |
| `src/physics/dialogue_engine.py` | DialogueEngine — محرك حوار يمنع الاستكمال الإحصائي |

## 4. مقارنة الإصدارات

| الخاصية | V5.3 | V5.4 | V6 |
|---------|------|------|----|
| أبعاد الفضاء | 56 + FFT | 56 + FFT | **64 + FFT** |
| معايير التسجيل | 20+ | 20+ | **24+ (+DCCF, PPM, AMFS, Cascade)** |
| أنماط التوليد | 5 | 5 | 6 (+ auto في Orchestrator) |
| الشعر العربي | 3 أبحُر | 3 أبحُر | **16 بحراً + كشف تلقائي** |
| التعلم | لا | لا | **تعزيز طوري (PhaseReinforcement)** |
| التنسيق | Generator | Generator | **PhysicsOrchestrator + CLI** |
| In-Context Learning | لا | لا | **PPM (حقل خارجي يضمحل)** |
| بديل Attention | Phase Attention | Phase Attention | **DCCF (اقتران ديناميكي لحظي)** |
| التوليد الحتمي | لا | لا | **PotentialCascadeLayer (هوي جهدي تراكمي)** |
| الملفات | 34 | 38 | **48** |
| الحوار | لا | لا | **DialogueEngine (كشف القصد + رد مستقل)** |
| الاختبارات | 89 | 108 | **108 (0 تراجع)** |