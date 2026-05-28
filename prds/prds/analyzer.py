import numpy as np
from scipy.interpolate import interp1d

class PRDSAnalyzer:
    """
    المحلل اللغوي والتشخيصي (PRDS Diagnostic Analyzer)
    يقوم بتصنيف الجمل، مطابقة القوالب الطورية (Phase Templates)، وتحديد الجاذبية الطورية لملء الفراغات.
    """
    def __init__(self, engine):
        self.engine = engine
        self.lexicon = engine.lexicon
        # ذاكرة القوالب الطورية (Phase Templates Memory)
        self.phase_templates = {}

    def register_phase_template(self, name, r_history, sent_type):
        """تسجيل بصمة طورية كقالب مرجعي للمقارنة"""
        # توحيد طول المنحنى إلى 100 نقطة للمقارنة القياسية
        x_orig = np.linspace(0, 1, len(r_history))
        x_norm = np.linspace(0, 1, 100)
        f = interp1d(x_orig, r_history, kind='linear')
        r_norm = f(x_norm)
        
        self.phase_templates[name] = {
            "r_profile": r_norm,
            "type": sent_type
        }

    def _match_template(self, r_history, threshold=0.05):
        """البحث عن أقرب قالب طوري مطابق لمنحنى r(t) الحالي"""
        if not self.phase_templates or len(r_history) < 10:
            return None, None

        x_orig = np.linspace(0, 1, len(r_history))
        x_norm = np.linspace(0, 1, 100)
        f = interp1d(x_orig, r_history, kind='linear')
        r_norm = f(x_norm)

        best_match = None
        min_mse = float('inf')

        for name, template in self.phase_templates.items():
            mse = np.mean((r_norm - template["r_profile"]) ** 2)
            if mse < min_mse:
                min_mse = mse
                best_match = name

        if min_mse < threshold:
            return best_match, self.phase_templates[best_match]["type"]
        return None, None

    def classify_sentence(self, r_history, word_ids=None):
        """
        تصنيف الجملة (خبرية، استعارية، ساخرة) بناءً على مسار التماسك r(t) وطوبولوجيا قوى الاقتران K.
        يتضمن مطابقة القوالب الطورية المخزنة.
        """
        if len(r_history) < 10 or not word_ids or len(word_ids) < 2:
            return "غير محدد", "بيانات المحاكاة غير كافية"

        K = self.engine.coupling.K
        n = len(word_ids)
        w1, w2 = word_ids[0], word_ids[1]
        w_last = word_ids[-1]

        # 1. فحص مطابقة القوالب الطورية المخزنة مسبقاً (Phase Templates)
        matched_name, matched_type = self._match_template(r_history)
        template_info = f" (تمت مطابقة القالب الطوري: {matched_name})" if matched_name else ""

        # 2. التحقق من وجود تنافر طوري قوي مع الكلمة الأخيرة (كشف السخرية)
        has_repulsion = any(K[word_ids[i], w_last] < -1.0 for i in range(n - 1))
        max_r = np.max(r_history)
        final_r = r_history[-1]
        
        # معيار السخرية الديناميكي: هبوط حاد دون انتعاش بالإضافة إلى التنافر
        if has_repulsion or (max_r > 0.5 and (max_r - final_r) > 0.30):
            explanation = f"لوحظ ارتفاع مبدئي في التماسك يتبعه انهيار حاد وتنافر طوري قوي عند دخول الكلمة الأخيرة بسبب التعاكس الدلالي، مما يشخص كانتهاك ساخر.{template_info}"
            return "سخرية (Sarcasm)", explanation

        # 3. كشف الاستعارة: انخفاض في التماسك (حيرة طورية مبكرة) يتبعه انتعاش واستقرار
        min_dip = np.min(r_history[15:75])
        start_r = np.mean(r_history[:10])
        
        # معيار الاستعارة: غياب الاقتران المباشر أو وجود منحنى انخفاض ثم ارتفاع (r_min < 0.35 and r_final > 0.5)
        if (np.abs(K[w1, w2]) < 0.25 and n > 2) or (min_dip < 0.4 and final_r > 0.55 and final_r > min_dip + 0.1):
            explanation = f"لوحظ انخفاض في التماسك لغياب الاقتران المباشر بين الكلمتين الأوليين، يتبعه انتعاش ذاتي وإعادة تنظيم طوري بفضل الرنين غير المباشر (الدرجة الثانية) عبر الكلمة الوسيطة.{template_info}"
            return "استعارة (Metaphor)", explanation

        # 4. الجملة الخبرية: ترابط مباشر وتماسك مستقر
        explanation = f"المنحنى يظهر تماسكاً مرتفعاً ومستقراً، مما يعكس ترابطاً نحوياً ودلالياً مباشراً بين المذبذبات.{template_info}"
        return "خبرية (Declarative)", explanation

    def predict_next_word(self, sentence_words, top_k=5):
        """
        التنبؤ بالكلمة التالية (ملء الفراغ) باستخدام مبدأ الجاذبية الطورية (Phase Attraction).
        """
        word_ids = [self.lexicon.vocab[w] for w in sentence_words if w in self.lexicon.vocab]
        if not word_ids:
            return []

        # تشغيل محاكاة سريعة للجملة الحالية لمعرفة أطوار الاستقرار
        _, phases_history, _, _ = self.engine.simulate(word_ids, t_span=(0, 5), num_steps=100, sequential=False)
        final_phases = phases_history[-1, :, 0]  # البعد الدلالي فقط (d=0)
        mean_phase = np.angle(np.mean(np.exp(1j * final_phases)))

        vocab_size = self.lexicon.get_vocab_size()
        attractions = []

        K = self.engine.coupling.K
        alpha = self.engine.alpha

        # تحسين الكفاءة بسحب الأعمدة والصفوف للكلمات النشطة مسبقاً وتخزينها
        K_csr = K.tocsr() if hasattr(K, "tocsr") else K
        K_csc = K.tocsc() if hasattr(K, "tocsc") else K
        
        # استخراج مسبق لأعمدة الكلمات النشطة لزيادة السرعة
        cols = {}
        for wid in word_ids:
            cols[wid] = K_csc[:, wid]

        for cand_id in range(vocab_size):
            if cand_id in word_ids:
                continue
            
            cand_word = self.lexicon.id2word[cand_id]
            net_force = 0.0
            row_cand = K_csr[cand_id, :]
            
            for idx, wid in enumerate(word_ids):
                theta_i = final_phases[idx]
                direct = K_csr[cand_id, wid]
                if hasattr(direct, "toarray"):
                    direct = direct.toarray()[0, 0]
                
                # حساب الرنين غير المباشر (الدرجة الثانية) ديناميكياً للكلمات النشطة لتوفير الذاكرة
                col_wid = cols[wid]
                prod = row_cand * col_wid
                # إذا كانت النتيجة مصفوفة متفرقة 1x1، نستخلص القيمة
                if hasattr(prod, "toarray"):
                    indirect_val = prod.toarray()[0, 0]
                elif hasattr(prod, "data") and len(prod.data) > 0:
                    indirect_val = prod.data[0]
                else:
                    try:
                        indirect_val = prod[0, 0]
                    except:
                        indirect_val = float(prod)
                
                indirect = alpha * indirect_val
                phase_alignment = np.cos(mean_phase - theta_i)
                net_force += (direct + indirect) * phase_alignment

            attractions.append((cand_word, net_force))

        attractions.sort(key=lambda x: x[1], reverse=True)
        return attractions[:top_k]

    def analyze_sentence_groups(self, word_ids, K_eff, threshold=0.15):
        """
        استخراج المجموعات النحوية الضمنية (Clusters) بناءً على مصفوفة الاقتران الفعال.
        """
        n = len(word_ids)
        visited = np.zeros(n, dtype=bool)
        clusters = []

        for i in range(n):
            if not visited[i]:
                cluster = [i]
                visited[i] = True
                for j in range(n):
                    if not visited[j] and np.abs(K_eff[i, j]) > threshold:
                        cluster.append(j)
                        visited[j] = True
                
                cluster_words = [self.lexicon.id2word[word_ids[idx]] for idx in cluster]
                clusters.append(cluster_words)

        return clusters

    def calculate_phase_perplexity(self, r_history, word_ids):
        """
        مقياس التقييم الكمي 'الدهشة الطورية' (Phase Perplexity / Surprisal).
        يعكس مدى حيرة النموذج ومفاجأته أمام الجملة: كلما انخفض التماسك الديناميكي r(t)،
        زادت الدهشة الطورية.
        """
        if len(r_history) == 0 or not word_ids:
            return 1.0
        mean_r = np.mean(r_history)
        final_r = r_history[-1]
        effective_r = 0.7 * mean_r + 0.3 * final_r
        return float(1.0 / (effective_r + 1e-6))

