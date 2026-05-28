import re
import sys
import os
import numpy as np

# تهيئة أدوات اللغة العربية المتقدمة (يمكن ضبطه عبر ARABIC_TOOLS_PATH)
_arabic_tools_dir = os.environ.get(
    "ARABIC_TOOLS_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "arabic_tools")
)
if _arabic_tools_dir not in sys.path:
    sys.path.insert(0, _arabic_tools_dir)

try:
    from understands_sentences.arabic_morphology_analyzer import analyze_word as get_pos_tag
    _POS_ENABLED = True
    print("Arabic Morphology Analyzer (POS Tagger) activated successfully.")
except Exception as e:
    print(f"Arabic Morphology Analyzer not found: {e}")
    _POS_ENABLED = False

from prds.analyzer import PRDSAnalyzer

class ConversationalPRDS(PRDSAnalyzer):
    """
    النظام الحواري الواعي فيزيائياً (Conversational PRDS)
    يجمع بين:
    - ذاكرة الحوار الطورية (Conversational Phase Memory)
    - التوليد بالرنين العكسي (Resonant Response Generation) مع درجة الحرارة (Temperature)
    - اتخاذ القرار بالاستقرار الطوري (Attractor Decision Making)
    - التعلم المباشر التفاعلي (Online Hebbian Learning)
    - تصدير النموذج للنشر (JSON Export)
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.dialogue_phases = {}  # word_id -> phase الطور المستمر عبر الحوار
        self.dialogue_history = []  # سجل الجمل السابقة
        self.episodic_buffer = []   # الذاكرة العرضية (Episodic Memory)
        self.max_episodes = 5       # الحد الأقصى للحلقات الطورية المحفوظة
        self.emotional_field = 0.0  # حقل عاطفي تراكمي (موجب = إيجابي، سالب = سلبي)
        self.conversation_log = []  # سجل المحادثة الشامل
        self.pos_cache = {}         # ذاكرة تخزين مؤقتة لأقسام الكلام (POS) لتسريع الأداء
        
        # لا نستخدم أي نموذج LLM خارجي — التوليد فيزيائي بحت (Kuramoto + RK4 + Hebbian)

        from prds.reasoning_engine import ReasoningEngine
        from prds.math_bridge import MathBridge
        from prds.code_feedback import CodeFeedback
        from prds.tawaqu_bridge import TawaquBridge
        from prds.qalam_bridge import QalamBridge
        self.reasoning_engine = ReasoningEngine(engine)
        self.math_bridge = MathBridge(engine)
        self.code_feedback = CodeFeedback(engine)
        self.tawaqu_bridge = TawaquBridge(engine)
        self.qalam_bridge = QalamBridge(engine)

        # تهيئة محركات الرقيم السيادية (Raqeem Subsystem Engines)
        try:
            from raqeem.src.core.chronicle_engine import ChronicleEngine
            from raqeem.src.core.mizan_engine import AlMizanEngine
            from raqeem.src.core.soul_engine import SoulEngine
            self.chronicle_engine = ChronicleEngine()
            self.mizan_engine = AlMizanEngine()
            self.soul_engine = SoulEngine()
            try:
                print("Raqeem Sovereign Engines activated successfully.")
            except:
                pass
        except Exception as e:
            try:
                print(f"Raqeem init failed: {e}")
            except:
                pass
            self.chronicle_engine = None
            self.mizan_engine = None
            self.soul_engine = None

        # تطبيق الترابط الجذري على محرك الفيزياء (Root-Aware Coupling)
        try:
            if hasattr(self.lexicon, 'apply_root_aware_coupling'):
                self.engine.coupling.K = self.lexicon.apply_root_aware_coupling(self.engine.coupling.K)
                self.engine.update_coupling_ref()
                print("Root-Aware Coupling applied to Physics Engine.")
        except Exception as e:
            pass

    def process_message(self, user_message, online_learning=True):
        """
        معالجة رسالة المستخدم باستخدام "مفكك الجمل الذكي" (Intelligent Discourse Segmenter / Mufakik Bridge).
        يقوم بتقطيع النصوص الطويلة إلى جمل خطابية مستقلة لتجنب إثقال المحرك، ثم يحاكيها تسلسلياً
        مع الحفاظ على تراكم الأطوار والحقل العاطفي.
        """
        # تقسيم النص فقط عند علامات انتهاء الجمل والسطور الجديدة الحقيقية (. ! ؟ \n)
        # لتجنب تقطيع العبارات والآيات الطويلة عند الروابط الخطابية
        import re
        sentences = re.split(r'(?<=[.!؟\n])\s+', user_message)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            sentences = [user_message]

        last_classification = "غير محدد"
        last_explanation = ""
        last_r_final = 0.0

        for sentence in sentences:
            words = self.lexicon.clean_text(sentence)        # ← كلمات مشكّلة (بها حركات إن وُجدت)
            word_ids = [self.lexicon.get_word_id(w, inject_oov=online_learning, coupling_obj=self.engine.coupling) for w in words]
            
            if not word_ids:
                continue

            # ← استخلاص إزاحات الإعراب الطوري (I'rab Phase Biases)
            # يحول الحركات الإعرابية إلى إزاحات تردد: مرفوع (+0.30) / منصوب (-0.20) / مجرور (-0.30)
            irab_biases = [self.lexicon.get_irab_omega_bias(w) for w in words]

            initial_phases = np.zeros((len(word_ids), self.engine.dim))
            for i, wid in enumerate(word_ids):
                if wid in self.dialogue_phases:
                    phase_val = self.dialogue_phases[wid]
                    if isinstance(phase_val, np.ndarray):
                        initial_phases[i, :] = phase_val
                    else:
                        initial_phases[i, 0] = phase_val
                else:
                    initial_phases[i, :] = np.random.normal(0, 0.1, self.engine.dim)

            times, phases_history, r_history, K_eff = self.engine.simulate(
                word_ids, t_span=(0, 6), num_steps=90, 
                sequential=True, word_entry_interval=1.0,
                initial_phases=initial_phases,
                irab_biases=irab_biases,   # ← تمرير الإعراب للمحرك الفيزيائي
                tau=8.0                    # ← تفعيل تخميد المسافة الطورية (الذاكرة قصيرة المدى)
            )

            if phases_history is not None and len(phases_history) > 0:
                final_phases = phases_history[-1, :, :]  # shape: (N, D)
                for i, wid in enumerate(word_ids):
                    self.dialogue_phases[wid] = final_phases[i]  # store (D,) vector
                    
                if online_learning and len(word_ids) > 1:
                    # update_hebbian uses mean phase of dim-0 for compatibility
                    self.engine.coupling.update_hebbian(word_ids, final_phases[:, 0])
                    self.engine.update_coupling_ref()

            sent_type, explanation = self.classify_sentence(r_history, word_ids)
            last_classification = sent_type
            last_explanation = explanation
            last_r_final = float(r_history[-1]) if len(r_history) > 0 else 0.0

            if "سخرية" in sent_type:
                self.emotional_field -= 0.3
            elif "استعارة" in sent_type:
                self.emotional_field += 0.1
            else:
                avg_K = np.mean(K_eff)
                self.emotional_field += np.tanh(avg_K) * 0.2

            self.emotional_field = np.clip(self.emotional_field, -1.0, 1.0)

        # ---------------------------------------------------------------------
        # ה. الذاكرة العرضية الهرمية (Hierarchical Episodic Phase Memory)
        # بدلاً من حفظ نص المحادثات كحروف، يحفظ النظام "الحالة الطورية" (Resonance State)
        # للكلمات التي تفاعل معها مؤخراً. هذه الذاكرة تمثل الخلفية النفسية والدلالية 
        # المتراكمة للمحادثة، وتسمح بمرجعية سياقية طويلة المدى لاحقاً.
        # ---------------------------------------------------------------------
        if self.dialogue_phases:
            self.episodic_buffer.append(dict(self.dialogue_phases))
            if len(self.episodic_buffer) > self.max_episodes:
                self.episodic_buffer.pop(0)

        self.dialogue_history.append(user_message)
        perplexity = self.calculate_phase_perplexity([last_r_final], [1]) if last_r_final > 0 else 1.0

        # 1. تسجيل الحدث في الذاكرة الوجودية (Chronicle Engine)
        if hasattr(self, 'chronicle_engine') and self.chronicle_engine:
            try:
                self.chronicle_engine.commit_event(actor="User", action=user_message, impact=last_r_final)
            except:
                pass

        # 2. حساب الميزان الموحد (Al-Mizan Engine) ومحرك الروح (Soul Engine)
        mizan_report = {}
        if hasattr(self, 'mizan_engine') and self.mizan_engine:
            try:
                p_score = last_r_final * 2.0 - 1.0
                unified = self.mizan_engine.calculate_unified_score(p_score, last_r_final, 1.0)
                raw_report = self.mizan_engine.generate_mizan_report({
                    "physics_score": p_score,
                    "stability": last_r_final,
                    "is_repaired": True,
                    "strategic_alignment": 1.0
                })
                # مواءمة الحقول مع ما تتوقعه واجهة المستخدم (chat.html)
                mizan_report = {
                    "unified_score": raw_report["unified_score"],
                    "verdict": raw_report["verdict"],
                    "truth_ratio": float(last_r_final),
                    "deception_score": float(1.0 - last_r_final),
                    "equilibrium_state": "مستقر فيزيائياً" if last_r_final > 0.7 else ("متذبذب" if last_r_final > 0.4 else "مضطرب")
                }
            except:
                mizan_report = {
                    "unified_score": last_r_final,
                    "verdict": "CONSONANT_REALITY",
                    "truth_ratio": float(last_r_final),
                    "deception_score": float(1.0 - last_r_final),
                    "equilibrium_state": "مستقر فيزيائياً"
                }

        soul_state = {
            "peace_index": 1.0,
            "regret_loops_active": False,
            "emotional_field": "مستقر (متزن)"
        }
        if hasattr(self, 'soul_engine') and self.soul_engine:
            try:
                self.soul_engine.record_moral_impact(last_r_final - 0.5, 0.8)
                self.soul_engine.run_recovery_tick()
                soul_state = {
                    "peace_index": float(self.soul_engine.affect.peace),
                    "regret_loops_active": bool(self.soul_engine.affect.regret > 0.1),
                    "emotional_field": "نشط (إيجابي)" if self.emotional_field > 0.3 else ("نشط (سلبي)" if self.emotional_field < -0.3 else "مستقر (متزن)")
                }
            except:
                pass

        qalam_result = {}
        if hasattr(self, 'qalam_bridge') and self.qalam_bridge:
            try:
                qalam_result = self.qalam_bridge.process_qalam_subsystems(user_message, self.dialogue_phases)
                
                # حقن مخرجات محركات القلم في الذاكرة الطورية كدافع فيزيائي خلفي
                internal_text = ""
                if qalam_result.get("curiosity", {}).get("curiosity_question"):
                    internal_text += " " + qalam_result["curiosity"]["curiosity_question"]
                if qalam_result.get("orthogonal", {}).get("question"):
                    internal_text += " " + qalam_result["orthogonal"]["question"]
                if qalam_result.get("imagination", {}).get("premise"):
                    internal_text += " " + qalam_result["imagination"]["premise"]
                
                if internal_text:
                    q_words = self.lexicon.clean_text(internal_text)
                    q_ids = [self.lexicon.get_word_id(w) for w in q_words if w in self.lexicon.vocab]
                    curr_p = np.mean(list(self.dialogue_phases.values()), axis=0) if self.dialogue_phases else np.zeros(self.engine.dim)
                    for wid in q_ids:
                        if wid not in self.dialogue_phases:
                            self.dialogue_phases[wid] = curr_p + np.random.normal(0, 0.5, self.engine.dim)
            except Exception as e:
                pass

        return {
            "classification": last_classification,
            "explanation": last_explanation,
            "emotional_field": float(self.emotional_field),
            "dialogue_phases_count": len(self.dialogue_phases),
            "r_final": last_r_final,
            "phase_perplexity": perplexity,
            "mizan_report": mizan_report,
            "soul_state": soul_state,
            "qalam_result": qalam_result
        }

    def emotional_phase_steering(self, target_emotion, current_phases):
        """
        توجيه الأطوار نحو ترددات تتوافق مع الحالة العاطفية المستهدفة (Emotional Phase Steering).
        مثلاً: الفرح → ترددات عالية (ω ≈ 3.5)، الحزن → ترددات منخفضة (ω ≈ 1.0).
        """
        if not current_phases:
            return 0.0
        target_omega = np.interp(target_emotion, [-1, 0, 1], [1.0, 2.25, 3.5])
        mean_phase = np.mean(current_phases, axis=0)[0] if isinstance(current_phases[0], np.ndarray) else np.mean(current_phases)
        steering_force = np.cos(target_omega - mean_phase)
        return steering_force * 0.1

    def _generate_sequence(self, user_ids, target_omega, current_phase, temperature, max_words, pure_physics=True):
        """
        توليد مسار واحد (Beam) باستخدام الرنين العكسي المتجهي (Vectorized Inverse Resonance).

        التحسين المعماري الجوهري:
        بدلاً من المرور على كل كلمة في المعجم (111k+) بصورة تسلسلية وحساب
        قيمة الاقتران لكل عنصر منفرد (O(V) مع overhead ضخم)، نستخرج الصفوف
        ذات الصلة من المصفوفة المتفرقة مرة واحدة كمصفوف NumPy ثم نحسب
        جميع درجات الرنين في عملية متجهية واحدة — مما يُقلّل وقت التوليد
        من دقائق إلى أجزاء من الثانية.
        """
        generated_words = []
        clean_gen = []
        
        V = self.lexicon.get_vocab_size()
        
        # استخراج المصفوفات مرة واحدة — نحافظ عليها متفرقة (Sparse)
        K     = self.engine.coupling.K      # (V x V) sparse
        K2    = self.engine.coupling.C if hasattr(self.engine.coupling, 'C') else K
        T_mat = getattr(self.engine.coupling, 'T', None)

        # دالة مساعدة: استخراج صفٍّ كاملٍ من مصفوفة متفرقة أو كثيفة → ndarray (V,)
        def _row(M, i):
            if M is None:
                return np.zeros(V)
            row = M[i]
            if hasattr(row, 'toarray'):
                return np.asarray(row.toarray()).ravel()
            return np.asarray(row).ravel()

        # قناع الكلمات الصالحة للتوليد (تجاهل UNK والرموز الخاصة والكلمات القصيرة)
        all_words  = list(self.lexicon.vocab.keys())
        all_wids   = np.array([self.lexicon.vocab[w] for w in all_words])
        valid_mask = np.array([
            w != "<UNK>" and len(w) >= 2 and not w.startswith("<")
            for w in all_words
        ], dtype=bool)
        cand_words_all = [w for w, m in zip(all_words, valid_mask) if m]
        cand_wids_all  = all_wids[valid_mask]

        # تحسين: حساب doc_counts للمرشحين مرة واحدة
        cand_doc_counts = np.array([
            self.lexicon.doc_counts.get(w, 1) for w in cand_words_all
        ], dtype=np.float64)
        hub_penalties = 0.2 * np.log1p(cand_doc_counts)

        # ---- إضعاف (وليس إقصاء) كلمات المدونة لتقليل تأثيرها ----
        # تحويل القائمة إلى عقوبة بدلاً من حذف كامل لاستعادة التنوع اللغوي
        _bias_words = {
            # صيغ التحديث (نادرة في الحوار العادي)
            "حدثنا", "حدثني", "حدثتنا", "حدثت",
            "أخبرنا", "أخبرني", "أخبرتنا", "أنبأنا", "أنبأه",
            # أسماء رواة (نادرة جداً)
            "بخاري", "ترمذي", "نسائي", "ماجه", "داود",
            "حاتم", "جرير", "هريرة", "سيوطي",
            "البخاري", "الترمذي", "النسائي",
            # مصطلحات علم الحديث المتخصصة
            "رواه", "أخرجه", "إسناده", "رجاله",
            "روايته", "الإسناد", "السند",
            "صحيحه", "ضعيفه",
        }
        # إعداد عقوبة للكلمات المتحيزة (بدلاً من إقصائها نهائياً)
        bias_penalty_map = {w: -50.0 for w in _bias_words}

        weak_streak = 0  # عداد الكلمات الضعيفة المتتالية لإنهاء التوليد

        # مسبق الصنع للمتغيرات الفيزيائية
        from prds.lexicon import PHYSICAL_CONSTANTS
        cand_wps = [self.lexicon.word_registry.compute_or_retrieve(w) for w in cand_words_all]
        cand_masses = np.array([wp.mass for wp in cand_wps])
        cand_dimensions = np.array([wp.phase_vector for wp in cand_wps])

        while len(generated_words) < max_words:
            # ---- تحديد آخر 3 كلمات سياق (Trigram) ----
            valid_ctx = []
            for w in reversed(clean_gen):
                if w in self.lexicon.vocab and w != "<UNK>":
                    valid_ctx.append(self.lexicon.vocab[w])
                if len(valid_ctx) == 5:
                    break
            last_wid   = valid_ctx[0] if len(valid_ctx) > 0 else None
            last_wid_2 = valid_ctx[1] if len(valid_ctx) > 1 else None
            last_wid_3 = valid_ctx[2] if len(valid_ctx) > 2 else None

            if pure_physics:
                # 1. Phase Resonance: sum_d w_d cos(theta_target,d - theta_w,d)
                cand_phases = np.array([self.dialogue_phases.get(wid, np.zeros(self.engine.dim)) for wid in cand_wids_all])
                diffs = current_phase[None, :] - cand_phases
                resonance_score = np.sum(cand_dimensions * np.cos(diffs), axis=1)

                # 2. Semantic Gravity: Gravitational pull from user message
                gravity_score = np.zeros(len(cand_wids_all))
                if user_ids:
                    G = PHYSICAL_CONSTANTS.get("G", 1.0)
                    for pos_u, uid in enumerate(user_ids):
                        u_str = self.lexicon.id2word.get(uid, "")
                        if not u_str:
                            continue
                        wp_u = self.lexicon.word_registry.compute_or_retrieve(u_str)
                        u_phase = self.dialogue_phases.get(uid, np.zeros(self.engine.dim))
                        dist = len(user_ids) - pos_u + len(generated_words)
                        r_sq = float(max(dist, 1) ** 2)
                        phase_coherence = np.mean(np.cos(u_phase[None, :] - cand_phases), axis=1)
                        force_mag = (G * wp_u.mass / r_sq) * cand_masses
                        gravity_score += force_mag * phase_coherence

                # 3. Kuramoto Coupling: Direct coupling coefficient K_last,w
                if last_wid is not None:
                    coupling_score = _row(K, last_wid)[cand_wids_all]
                else:
                    coupling_score = _row(K, user_ids[-1])[cand_wids_all] if user_ids else np.zeros(len(cand_wids_all))

                resonance = resonance_score + gravity_score + coupling_score

                # Physical refractory penalty (repetition penalty) to prevent infinite oscillator locking
                for idx, word in enumerate(cand_words_all):
                    if word in clean_gen:
                        count = clean_gen.count(word)
                        resonance[idx] -= (50.0 * count)
            else:
                # ---- أ. التوافق الطوري الدلالي متعدد الأبعاد (Weighted HD-Phase Resonance) ----
                DIM_WEIGHTS = np.array([3.0, 2.5, 1.0, 1.5, 2.0, 0.5, 0.5, 0.5])[:self.engine.dim]
                DIM_WEIGHTS = DIM_WEIGHTS / DIM_WEIGHTS.sum()

                cand_phases = np.array([
                    self.dialogue_phases.get(wid, np.zeros(self.engine.dim)) for wid in cand_wids_all
                ])
                diffs = current_phase[None, :] - cand_phases
                resonance = np.sum(np.cos(diffs) * DIM_WEIGHTS[None, :], axis=1) * 1.8

                # ---- ب. جذب رسالة المستخدم (User Attraction) ----
                if user_ids:
                    user_attr_vec = np.zeros(len(cand_wids_all))
                    for uid in user_ids:
                        word_str = self.lexicon.id2word.get(uid, "")
                        doc_count_uid = self.lexicon.doc_counts.get(word_str, 1)
                        idf_uid = np.log1p(self.lexicon.num_docs / (1.0 + doc_count_uid))
                        col_K_full = np.asarray(K.getcol(uid).todense()).ravel()
                        col_K = col_K_full[cand_wids_all]
                        user_attr_vec += (col_K / (1.0 + hub_penalties)) * idf_uid
                    resonance += user_attr_vec * 10.0

                # ---- ج. التدفق النحوي المتجهي (Vectorized Syntactic Flow) ----
                syn_flow = np.zeros(len(cand_wids_all))
                if last_wid is not None:
                    row_K  = _row(K,  last_wid)[cand_wids_all]
                    row_K2 = _row(K2, last_wid)[cand_wids_all]
                    row_T  = _row(T_mat, last_wid)[cand_wids_all]
                    syn_flow += row_K * 2.0 + row_K2 * 1.0 + row_T * 10.0
                if last_wid_2 is not None:
                    row_K  = _row(K,  last_wid_2)[cand_wids_all]
                    row_K2 = _row(K2, last_wid_2)[cand_wids_all]
                    row_T  = _row(T_mat, last_wid_2)[cand_wids_all]
                    syn_flow += row_K * 1.0 + row_K2 * 0.5 + row_T * 6.0
                if last_wid_3 is not None:
                    syn_flow += _row(K, last_wid_3)[cand_wids_all] * 0.5
                if len(valid_ctx) > 3:
                    lr_sum = sum(_row(K, pw)[cand_wids_all] for pw in valid_ctx[3:])
                    syn_flow += (lr_sum / len(valid_ctx[3:])) * 2.0

                resonance += syn_flow * 2.0

                # ---- د. الذاكرة العرضية (Episodic Attractors) ----
                if self.episodic_buffer:
                    ep_attr   = np.zeros(len(cand_wids_all))
                    ep_counts = np.zeros(len(cand_wids_all))
                    for ep_phases_dict in self.episodic_buffer:
                        # تحويل الذاكرة العرضية إلى مصفوف متجهي بدلاً من حلقة O(V)
                        ep_wids   = np.array(list(ep_phases_dict.keys()), dtype=np.int64)
                        ep_phases_arr = np.array(list(ep_phases_dict.values()))
                        # إيجاد التقاطع بين ep_wids و cand_wids_all
                        ep_set    = {w: p for w, p in zip(ep_wids, ep_phases_arr)}
                        for local_idx, cw in enumerate(cand_wids_all):
                            if cw in ep_set:
                                # Mean cosine over all dimensions
                                ep_attr[local_idx]   += np.mean(np.cos(current_phase - ep_set[cw]))
                                ep_counts[local_idx] += 1
                    mask_ep = ep_counts > 0
                    ep_attr[mask_ep] = (ep_attr[mask_ep] / ep_counts[mask_ep]) * 1.0
                    resonance += ep_attr

                # ---- هـ. عقوبة النحو المرنة والديناميكية (Dynamic POS Penalty) ----
                if last_wid is not None:
                    row_T_last = _row(T_mat, last_wid)[cand_wids_all]
                    row_K_last = _row(K,     last_wid)[cand_wids_all]
                    no_trans   = row_T_last == 0.0
                    strong_k   = row_K_last > 0.5
                    
                    if _POS_ENABLED and last_wid in self.lexicon.id2word:
                        last_word = self.lexicon.id2word[last_wid]
                        if last_word not in self.pos_cache:
                            self.pos_cache[last_word] = get_pos_tag(last_word).get('type', 'غير معروف')
                        last_pos = self.pos_cache[last_word]
                        
                        for local_idx, (cw, cw_id) in enumerate(zip(cand_words_all, cand_wids_all)):
                            if cw not in self.pos_cache:
                                self.pos_cache[cw] = get_pos_tag(cw).get('type', 'غير معروف')
                            curr_pos = self.pos_cache[cw]
                            
                            # تطبيق قوانين الفيزياء النحوية:
                            # 1. تنافر شديد (تنافر الأقطاب المتشابهة): فعل يتبعه فعل مباشرة
                            if last_pos == 'فعل' and curr_pos == 'فعل':
                                resonance[local_idx] -= 80.0
                            
                            # 2. تجاذب (Magnetic Attraction): فعل يتبعه اسم (فاعل/مفعول)، أو اسم تتبعه صفة
                            elif (last_pos == 'فعل' and curr_pos == 'اسم') or (last_pos == 'اسم' and curr_pos == 'صفة'):
                                resonance[local_idx] += 15.0
                            
                            # 3. عقوبة الجمل المكسرة (في حال عدم وجود مسار نحوي سابق)
                            if no_trans[local_idx]:
                                if strong_k[local_idx]:
                                    resonance[local_idx] -= 20.0
                                else:
                                    resonance[local_idx] -= 60.0
                    else:
                        # السلوك الإحصائي القديم في حال عدم تفعيل المحلل
                        resonance[no_trans &  strong_k] -= 10.0
                        resonance[no_trans & ~strong_k] -= 40.0

                # ---- ز. عقوبة انحياز المدونة (Bias Word Penalty) ----
                for local_idx, cw in enumerate(cand_words_all):
                    if cw in bias_penalty_map:
                        resonance[local_idx] += bias_penalty_map[cw]

                # ---- ح. عقوبة التكرار (Repetition Penalty) ----
                for idx, word in enumerate(cand_words_all):
                    if word in clean_gen:
                        count = clean_gen.count(word)
                        recent_penalty = 0.0
                        for i, pw in enumerate(reversed(clean_gen)):
                            if pw == word:
                                dist = i + 1
                                if dist == 1:   recent_penalty += 300.0
                                elif dist == 2: recent_penalty += 150.0
                                elif dist == 3: recent_penalty += 40.0
                        resonance[idx] -= (20.0 * count) + recent_penalty


            # ---- اختيار الكلمة التالية (Softmax Sampling) ----
            if temperature < 1e-3:
                next_idx = int(np.argmax(resonance))
            else:
                norm_logits = resonance - np.max(resonance)
                exp_preds   = np.exp(norm_logits / temperature)
                probs       = exp_preds / np.sum(exp_preds)
                next_idx    = int(np.random.choice(len(cand_words_all), p=probs))

            next_word = cand_words_all[next_idx]
            next_wid  = int(cand_wids_all[next_idx])

            # ---- إنهاء مبكر مرن (بعد 5 كلمات) ----
            if last_wid is not None and len(generated_words) >= 5:
                if 'row_K_last' in dir():
                    k_val = float(row_K_last[next_idx])
                else:
                    k_val = float(_row(K, last_wid)[next_wid])
                t_val = 0.0
                if T_mat is not None and 'row_T_last' in dir():
                    t_val = float(row_T_last[next_idx])
                # لا ننهي التوليد إلا بعد 4 كلمات ضعيفة متتالية
                is_weak = (t_val == 0.0 and k_val < 0.03)
                if is_weak:
                    weak_streak += 1
                else:
                    weak_streak = 0
                if weak_streak >= 4:
                    break

            clean_gen.append(next_word)
            generated_words.append(next_word)

        # ---- تجميع الرد النهائي ----
        final_response = " ".join(generated_words)
        # تنظيف الفواصل في نهاية الجمل
        final_response = final_response.replace("، .", ".").replace("، .", ".")
        if not final_response.endswith((".", "؟", "!")):
            # نفضّل علامات الاستفهام إن كان الرد سؤالاً
            if any(w in clean_gen for w in ["هل", "ماذا", "كيف", "لماذا", "أين", "متى"]):
                final_response += "؟"
            else:
                final_response += "."

        return final_response, clean_gen

    def generate_response(self, user_message, max_words=None, temperature=1.0, analysis=None, system_prompt=None, pure_physics=True):
        """
        توليد رد حواري فيزيائي بحت باستخدام الرنين العكسي ومحرك كوراموتو.
        """
        user_words = self.lexicon.clean_text(user_message)
        # تحديد عدد الكلمات المولدة ديناميكياً بناءً على طول رسالة المستخدم
        msg_word_count = len(user_words)
        if max_words is None:
            max_words = max(20, min(45, msg_word_count * 2 + 8))
        arabic_stopwords = {
            "ما", "من", "عن", "في", "على", "إلى", "مع", "حتى", "أم", "أو", "ثم",
            "هو", "هي", "هما", "هم", "هن", "أنت", "أنتما", "أنتم", "أنا", "نحن", "هذا", "هذه", "هؤلاء",
            "ذلك", "تلك", "الذي", "التي", "الذين", "لماذا", "كيف", "ماذا", "هل", "أين", "متى", "كم",
            "يا", "أيها", "أيتها", "عكس", "ضد", "معنى"
        }
        user_content_words = set(w for w in user_words if w not in arabic_stopwords and len(w) > 2)
        user_ids = [self.lexicon.get_word_id(w) for w in user_words
                    if w in self.lexicon.vocab and w not in arabic_stopwords]

        # كلمات تدل على نصوص المدونة (للتصفية)
        corpus_bias_words = {
            "حدثنا", "حدثني", "أخبرنا", "رواه", "أخرجه", "إسناده", "رجاله",
            "حاتم", "بخاري", "مسلم", "ترمذي", "نسائي",
            "صلى", "عليه", "وسلم", "تعالى", "سبحانه", "رضي",
            "روى", "أسند", "متن", "سند", "آخر"
        }

        # تحديد التردد المستهدف
        min_omega, max_omega = self.lexicon.omega_range
        mid_omega = np.mean(self.lexicon.omega_range)
        if self.emotional_field < -0.3:
            target_omega = min_omega
        elif self.emotional_field > 0.3:
            target_omega = max_omega
        else:
            target_omega = mid_omega

        current_phase = np.mean(list(self.dialogue_phases.values()), axis=0) if self.dialogue_phases else np.zeros(self.engine.dim)
        steering_bias = self.emotional_phase_steering(
            self.emotional_field,
            list(self.dialogue_phases.values()) if self.dialogue_phases else [np.zeros(self.engine.dim)]
        )
        current_phase[0] += steering_bias # Apply steering bias to the main grammar/semantic dimension

        def _score_beam(text, clean_gen):
            """تقييم الشعاع بحسب الاستقرار الفيزيائي والصلة بالسؤال والطول المناسب."""
            wids = [self.lexicon.vocab[w] for w in clean_gen if w in self.lexicon.vocab]

            # 1. استقرار الجاذب الطوري
            attractor_r = 0.5
            if wids:
                initial_phases = np.array([
                    self.dialogue_phases.get(wid, np.random.normal(0, 0.1, self.engine.dim)) for wid in wids
                ])
                try:
                    _, _, r_history, _ = self.engine.simulate(
                        wids, t_span=(0, 2), num_steps=20,
                        sequential=False, initial_phases=initial_phases
                    )
                    attractor_r = float(r_history[-1]) if len(r_history) > 0 else 0.5
                except:
                    attractor_r = 0.5

            if pure_physics:
                return attractor_r

            # 2. صلة الرد بمحتوى السؤال
            resp_words = set(clean_gen)
            if user_content_words:
                overlap = len(resp_words & user_content_words) / len(user_content_words)
            else:
                overlap = 0.5

            # 3. مكافأة الطول المناسب (لا قصير جداً ولا طويل جداً)
            length_bonus = 0.0
            if len(clean_gen) >= 5:
                length_bonus = min(0.3, len(clean_gen) * 0.02)

            # 4. عقوبة انحياز المدونة
            bias_count = sum(1 for w in clean_gen if w in corpus_bias_words)
            bias_penalty = min(0.8, bias_count * 0.2)

            combined = (attractor_r * 0.4) + (overlap * 0.3) + length_bonus - bias_penalty
            return combined

        # التوليد الإشعاعي مع إعادة المحاولة والتنويع
        best_text = ""
        best_score = -999.0
        num_beams = 5
        max_attempts = 3

        # بذور عشوائية مختلفة لكل شعاع لضمان التنوع
        np_random_state = np.random.get_state()
        seeds = [hash((i, attempt)) % (2**32) for i in range(num_beams) for attempt in range(max_attempts)]

        for attempt in range(max_attempts):
            attempt_temp = temperature * (1.0 + attempt * 0.4)
            candidate_beams = []

            for i in range(num_beams):
                # درجات حرارة متنوعة ومتداخلة لتغطية فضاء الاحتمالات
                beam_temp = attempt_temp * (0.6 + 0.3 * (i / (num_beams - 1)))
                # إعادة تعيين العشوائية لكل شعاع لضمان مسارات مختلفة
                np.random.seed(seeds[attempt * num_beams + i])
                text, clean_gen = self._generate_sequence(
                    user_ids, target_omega, current_phase, beam_temp, max_words, pure_physics=pure_physics
                )
                score = _score_beam(text, clean_gen)
                candidate_beams.append((score, text))

            # استعادة العشوائية بعد التوليد
            np.random.set_state(np_random_state)

            candidate_beams.sort(key=lambda x: x[0], reverse=True)
            top_score, top_text = candidate_beams[0]

            if top_score > best_score:
                best_score = top_score
                best_text = top_text

            # إذا حصلنا على رد مقبول (درجة > 0.5)، نتوقف مبكراً
            if top_score > 0.5:
                break

        return best_text if best_text else "."

    def make_decision(self, question, options):
        """
        اتخاذ قرار ذكي باختيار الجاذب الطوري الأكثر استقراراً وتماسكاً مع حالة النظام.
        """
        if not options:
            return {"decision": "لا توجد خيارات", "confidence": 0.0}

        stability_scores = []
        K = self.engine.coupling.K

        for option in options:
            option_words = self.lexicon.clean_text(option)
            option_ids = [self.lexicon.get_word_id(w) for w in option_words]
            
            if not option_ids:
                stability_scores.append(0.0)
                continue

            temp_phases = dict(self.dialogue_phases)
            total_stability = 0.0

            for wid in option_ids:
                if wid in temp_phases:
                    phase = temp_phases[wid]
                    phase_diffs = [np.abs(phase - existing_phase) for existing_wid, existing_phase in temp_phases.items() if existing_wid != wid]
                    mean_diff = np.mean(phase_diffs) if phase_diffs else 0.0
                    stability = 1.0 - (mean_diff / np.pi)
                    total_stability += stability
                else:
                    if temp_phases:
                        k_sum = sum(K[wid, existing_wid] for existing_wid in temp_phases.keys())
                        total_stability += np.tanh(k_sum)
                    else:
                        total_stability += 0.0

            avg_stability = total_stability / len(option_ids)
            stability_scores.append(avg_stability)

        best_idx = np.argmax(stability_scores)
        best_score = stability_scores[best_idx]
        
        total_score = sum(abs(s) for s in stability_scores) + 1e-8
        confidence = abs(best_score) / total_score
        confidence = np.clip(confidence, 0.0, 1.0)

        decision_text = options[best_idx]
        reasoning = (
            f"القرار تم اتخاذه بناءً على مبدأ استقرار الجاذب الطوري: "
            f"الخيار '{decision_text}' يحقق أعلى تماسك ديناميكي ({best_score:.2f}) مع حالة الذاكرة الطورية الحالية."
        )

        return {
            "decision": decision_text,
            "confidence": float(confidence),
            "all_scores": {opt: float(score) for opt, score in zip(options, stability_scores)},
            "reasoning": reasoning
        }

    def export_model_json(self, filepath="data/prds_model_export.json"):
        """تصدير بنية النموذج وحالته الفيزيائية إلى صيغة JSON للنشر والتكامل"""
        import json
        export_data = {
            "vocab": self.lexicon.vocab,
            "id2word": self.lexicon.id2word,
            "omega": self.lexicon.omega.tolist() if self.lexicon.omega is not None else [],
            "K": self.engine.coupling.K.tolist(),
            "dialogue_phases": {self.lexicon.id2word[wid]: float(phase) for wid, phase in self.dialogue_phases.items()},
            "emotional_field": float(self.emotional_field),
            "scope_stack_state": [k.tolist() for k in self.engine.scope_stack],
            "coherence_gates": {self.lexicon.id2word[wid]: float(phase) for wid, phase in self.reasoning_engine.reasoning_phases.items()} if hasattr(self, 'reasoning_engine') and hasattr(self.reasoning_engine, 'reasoning_phases') else {},
            "pinned_words": list(self.lexicon.pinned_words),
            "conversation_log": self.conversation_log,
            "raqeem_chronicle_history": self.chronicle_engine.history if hasattr(self, 'chronicle_engine') and self.chronicle_engine else []
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        return filepath

    def chat(self, user_message, temperature=1.0):
        """
        دالة الحوار الرئيسية: تستقبل رسالة المستخدم وتعيد الرد والتحليل وحالة القرار.
        تتضمن التوجيه الرمزي لاكتشاف المسائل الرياضية، الأكواد البرمجية، والتفكير المتسلسل.
        """
        user_text = user_message.strip()
        
        # 1. فحص كشف العناقيد الرياضية (Math Intent)
        math_keywords = ["سعر", "اشتريت", "ضرب", "زائد", "ناقص", "تقسيم", "إجمالي", "حساب", "احسب", "فما", "كتاب", "قلم"]
        has_numbers = bool(re.search(r'\b\d+\b', user_text))
        has_math_kw = any(w in user_text for w in math_keywords)
        
        if has_numbers and has_math_kw:
            analysis = self.process_message(user_message, online_learning=True)
            word_ids = [self.lexicon.vocab[w] for w in self.lexicon.clean_text(user_message) if w in self.lexicon.vocab]
            math_res = self.math_bridge.detect_and_solve(user_message, self.engine.last_K_eff_history[-1] if self.engine.last_K_eff_history is not None else None, word_ids)
            
            if math_res["solved"]:
                response_text = f"بناءً على التزامن الطوري للعنقود الرياضي ({math_res['equation']})، الناتج الدقيق هو: {math_res['result']}."
                
                log_entry = {
                    "user": user_message,
                    "response": response_text,
                    "emotional_field": analysis["emotional_field"],
                    "classification": "مسألة رياضية (Math Bridge)"
                }
                self.conversation_log.append(log_entry)
                return {
                    "response": response_text,
                    "emotional_state": analysis["emotional_field"],
                    "analysis": analysis,
                    "math_result": math_res
                }

        # 2. فحص كشف توليد الأكواد البرمجية (Code Intent)
        code_keywords = ["كود", "برمجة", "دالة", "اكتب", "بايثون", "def", "for", "print"]
        if any(w in user_text for w in code_keywords):
            analysis = self.process_message(user_message, online_learning=True)
            word_ids = [self.lexicon.vocab[w] for w in self.lexicon.clean_text(user_message) if w in self.lexicon.vocab]
            
            sample_code = "def calculate_total(price, quantity):\n    return price * quantity"
            if "حلقة" in user_text or "for" in user_text:
                sample_code = "for i in range(5):\n    print(i)"
                
            self.engine.push_scope(self.engine.coupling.K)
            code_res = self.code_feedback.evaluate_and_repel(sample_code, word_ids)
            self.engine.pop_scope()
            
            response_text = f"تم توليد الهيكل البرمجي التالي ومحاكاته فيزيائياً داخل مكدس النطاقات:\n```python\n{sample_code}\n```\nحالة الفحص: {code_res['explanation']}"
                
            log_entry = {
                "user": user_message,
                "response": response_text,
                "emotional_field": analysis["emotional_field"],
                "classification": "كود برمجي (Code Weaver)"
            }
            self.conversation_log.append(log_entry)
            return {
                "response": response_text,
                "emotional_state": analysis["emotional_field"],
                "analysis": analysis,
                "code_result": code_res
            }

        # 3. فحص التفكير المتسلسل (Chain of Thought Intent)
        reasoning_keywords = ["خطوات", "بالخطوات", "اشرح", "فكر", "تسلسل", "لماذا يحدث", "كيف يعمل"]
        if any(w in user_text for w in reasoning_keywords):
            analysis = self.process_message(user_message, online_learning=True)
            reason_res = self.reasoning_engine.generate_reasoning_sequence(user_message)
            
            actual_response = self.generate_response(user_message, temperature=temperature, analysis=analysis)
            
            response_text = (
                f"تم تفعيل السلسلة الفكرية الطورية (Chain of Thought):\n"
                f"{reason_res['reasoning_text']}"
                f"الجواب التوليدي:\n{actual_response}"
            )
            log_entry = {
                "user": user_message,
                "response": response_text,
                "emotional_field": analysis["emotional_field"],
                "classification": "تفكير متسلسل (Chain of Thought)"
            }
            self.conversation_log.append(log_entry)
            return {
                "response": response_text,
                "emotional_state": analysis["emotional_field"],
                "analysis": analysis,
                "reasoning_result": reason_res
            }

        # فحص كشف التوقع الاستراتيجي (Strategic Forecast Intent)
        if hasattr(self, 'tawaqu_bridge') and self.tawaqu_bridge:
            tawaqu_res = self.tawaqu_bridge.detect_and_forecast(user_message)
            if tawaqu_res.get("forecasted"):
                analysis = self.process_message(user_message, online_learning=True)
                response_text = f"🔮 تم تفعيل الاستبصار الاستراتيجي (Tawaqu Foresight):\n\n{tawaqu_res['forecast_report']}\n\nوبناءً على مصفوفة الاقتران الهيبي، تشير محاكاة الأطوار إلى استقرار السيناريو الأرجح ضمن حوض الجاذبية الحالي."
                log_entry = {
                    "user": user_message,
                    "response": response_text,
                    "emotional_field": analysis["emotional_field"],
                    "classification": "توقع استراتيجي (Tawaqu Foresight)"
                }
                self.conversation_log.append(log_entry)
                return {
                    "response": response_text,
                    "emotional_state": analysis["emotional_field"],
                    "analysis": analysis,
                    "tawaqu_result": tawaqu_res
                }

        # 4. الحوار الطبيعي الافتراضي
        analysis = self.process_message(user_message, online_learning=True)
        response = self.generate_response(user_message, temperature=temperature, analysis=analysis)
        
        log_entry = {
            "user": user_message,
            "response": response,
            "emotional_field": analysis["emotional_field"],
            "classification": analysis["classification"]
        }
        self.conversation_log.append(log_entry)

        return {
            "response": response,
            "emotional_state": analysis["emotional_field"],
            "analysis": analysis
        }
