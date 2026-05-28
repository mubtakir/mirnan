import numpy as np
from scipy import sparse
from collections import defaultdict

class PhaseCoupling:
    """
    مصفوفة الاقتران الطورية (Phase Coupling Matrix K)
    تتعلم العلاقات النحوية والدلالية عبر قاعدة هيب المعدلة بالطور دون انتشار خلفي.
    """
    def __init__(self, lexicon, eta=0.05, max_weight=10.0):
        self.lexicon = lexicon
        self.eta = eta
        self.max_weight = max_weight
        self.vocab_size = lexicon.get_vocab_size()
        
        # مصفوفة الظهور المشترك والعلاقات الإحصائية C_ij (مخزنة كـ CSR افتراضياً للسرعة الفائقة)
        self.C = sparse.csr_matrix((self.vocab_size, self.vocab_size))
        # مصفوفة الاقتران الطورية K_ij
        self.K = sparse.csr_matrix((self.vocab_size, self.vocab_size))
        # مصفوفة الزخم الاتجاهي (Directed Transition T_ij) للحفاظ على النحو والترتيب
        self.T = sparse.csr_matrix((self.vocab_size, self.vocab_size))
        
        # مجمعات التحديثات للدفعات السريعة
        self.batch_updates_rows = []
        self.batch_updates_cols = []
        self.batch_updates_vals = []
        
    def build_co_occurrence_matrix(self, corpus_lines, window_size=5):
        """
        حساب مصفوفة العلاقات المشتركة C_ij بالاعتماد على:
        - القرب الموضعي (Positional proximity)
        - التضاد والترادف الدلالي الضمني عبر سياقات المقارنة
        """
        co_occur = defaultdict(float)
        T_dict = defaultdict(float)
        
        # كلمات مفتاحية تعبر عن التضاد أو السياق السلبي في المدونة
        contrast_words = {"بينما", "بئس", "قبيح", "قبيحة", "بشع", "أقبح", "عكس", "لكن", "مرفوضة"}
        positive_words = {"أجمل", "جميل", "جميلة", "سعادة", "صدق", "الصدق", "وفاء", "الوفاء", "حب", "الحب", "سلام", "السلام", "أمل", "الأمل", "الحياة", "الطبيعة"}
        negative_words = {"خيانة", "الخيانة", "غدر", "الغدر", "قبيح", "قبيحة", "بشع", "ألم", "حزن", "شقاء", "الشقاء", "ظلام", "الظلام", "بئس"}
        
        for line in corpus_lines:
            raw_words = self.lexicon.clean_text(line)
            words = [self.lexicon.get_base_form(w) for w in raw_words]
            words = [w for w in words if w in self.lexicon.vocab]
            n = len(words)
            
            # التحقق من وجود سياق تضاد في الجملة
            has_contrast = any(w in contrast_words for w in words)
            
            for i in range(n):
                w1_str = words[i]
                w1 = self.lexicon.vocab[w1_str]
                
                for j in range(n):
                    if i != j:
                        w2_str = words[j]
                        w2 = self.lexicon.vocab[w2_str]
                        dist = abs(i - j)
                        
                        if dist <= window_size:
                            # الاقتران المحلي (Local Window-based Coupling)
                            weight = 1.0 / dist
                            
                            # تعزيز التضاد إذا كانت الكلمتان من أقطاب دلالية متعاكسة
                            if (w1_str in positive_words and w2_str in negative_words) or \
                               (w1_str in negative_words and w2_str in positive_words):
                                weight = -2.0  # اقتران سلبي قوي يعكس التنافر الطوري
                            elif has_contrast and dist > 2:
                                weight = -0.5 / dist
                                
                            co_occur[(w1, w2)] += weight
                        else:
                            # الاقتران بعيد المدى (Global Long-Range Coupling)
                            # ربط جميع كلمات الفقرة بجاذبية خفيفة مستمرة لحفظ سياق النص الطويل
                            weight = 0.05 / n
                            co_occur[(w1, w2)] += weight
                            
                        # تحديث مصفوفة الزخم الاتجاهي (Directed Transition T)
                        if j == i + 1:
                            T_dict[(w1, w2)] += 5.0

        # تعيين تنافر طوري صريح (اقتران سلبي قوي) بين جميع الكلمات الإيجابية والسلبية في المعجم
        for p_word in positive_words:
            if p_word in self.lexicon.vocab:
                p_id = self.lexicon.vocab[p_word]
                for n_word in negative_words:
                    if n_word in self.lexicon.vocab:
                        n_id = self.lexicon.vocab[n_word]
                        co_occur[(p_id, n_id)] = -5.0  # قوة تنافر سلبية ساحقة
                        co_occur[(n_id, p_id)] = -5.0

        # ملء مصفوفة C مباشرة كـ CSR
        c_rows = []
        c_cols = []
        c_vals = []
        for (w1, w2), val in co_occur.items():
            c_rows.append(w1)
            c_cols.append(w2)
            c_vals.append(val)
        self.C = sparse.csr_matrix((c_vals, (c_rows, c_cols)), shape=(self.vocab_size, self.vocab_size))

        # ملء مصفوفة T مباشرة كـ CSR
        t_rows = []
        t_cols = []
        t_vals = []
        for (w1, w2), val in T_dict.items():
            t_rows.append(w1)
            t_cols.append(w2)
            t_vals.append(val)
        self.T = sparse.csr_matrix((t_vals, (t_rows, t_cols)), shape=(self.vocab_size, self.vocab_size))

        # تهيئة K مبدئياً بقيم C الموزونة
        self.K = self.C.copy()

    def update_hebbian(self, word_ids, phases, batch_mode=False):
        """
        تحديث مصفوفة الاقتران K باستخدام قاعدة هيب المعدلة بالطور:
        ΔK_ij = η × cos(θ_i − θ_j) × C_ij
        """
        n = len(word_ids)
        if n <= 1:
            return
            
        phases = np.array(phases)
        # دعم أبعاد متعددة: إذا كانت (N, D) نأخذ المتوسط عبر الأبعاد للحصول على (N,)
        if phases.ndim == 2:
            phases = phases[:, 0]  # استخدام البعد الدلالي الأول (البعد الرئيسي)
        diffs = phases[:, None] - phases[None, :]
        cos_diffs = np.cos(diffs)
        
        # استخراج المصفوفة الفرعية كثنائية الأبعاد numpy من مصفوفة CSR السريعة جداً
        C_sub = self.C[word_ids, :][:, word_ids]
        if hasattr(C_sub, "toarray"):
            C_sub = C_sub.toarray()
            
        delta_K = self.eta * cos_diffs * np.abs(C_sub)
        
        if batch_mode:
            # في وضع الدفعات، نقوم بتجميع التحديثات لتطبيقها لاحقاً دفعة واحدة
            for i in range(n):
                w1 = word_ids[i]
                for j in range(n):
                    if i != j:
                        w2 = word_ids[j]
                        self.batch_updates_rows.append(w1)
                        self.batch_updates_cols.append(w2)
                        self.batch_updates_vals.append(delta_K[i, j])
        else:
            # التحويل المؤقت إلى LIL لتحديث العناصر الفردية (في وضع التدريب الفردي عبر الإنترنت)
            is_originally_lil = isinstance(self.K, sparse.lil_matrix)
            K_lil = self.K if is_originally_lil else self.K.tolil()
            K_sub = K_lil[word_ids, :][:, word_ids]
            if hasattr(K_sub, "toarray"):
                K_sub = K_sub.toarray()
                
            K_sub_new = K_sub + delta_K
            np.clip(K_sub_new, -self.max_weight, self.max_weight, out=K_sub_new)
            
            for i in range(n):
                w1 = word_ids[i]
                for j in range(n):
                    if i != j:
                        w2 = word_ids[j]
                        K_lil[w1, w2] = K_sub_new[i, j]
            self.K = K_lil if is_originally_lil else K_lil.tocsr()

    def apply_batch_updates(self):
        """
        تطبيق التحديثات المجمعة دفعة واحدة باستخدام عمليات المصفوفات المتفرقة السريعة
        ثم قص القيم الزائدة لضمان استقرار النموذج.
        """
        if not self.batch_updates_rows:
            return
            
        # إنشاء مصفوفة تحديثات متفرقة بسرعة
        delta_K = sparse.coo_matrix(
            (self.batch_updates_vals, (self.batch_updates_rows, self.batch_updates_cols)),
            shape=self.K.shape
        )
        
        # جمع مصفوفات CSR مباشرة (عملية فائقة السرعة بالكامل بـ C++)
        self.K = (self.K + delta_K.tocsr())
        
        # قص القيم المتجاوزة للحد الأقصى مباشرة على مصفوفة CSR المدمجة
        self.K.data = np.clip(self.K.data, -self.max_weight, self.max_weight)
        
        # تفريغ المجمعات للدورة التالية
        self.batch_updates_rows = []
        self.batch_updates_cols = []
        self.batch_updates_vals = []

    def get_coupling_submatrix(self, word_ids):
        """استخراج مصفوفة الاقتران الفرعية لجملة معينة"""
        if len(word_ids) == 0:
            return np.zeros((0, 0))
        # CSR slicing سريع للغاية
        sub_K = self.K[word_ids, :][:, word_ids]
        if hasattr(sub_K, "toarray"):
            return sub_K.toarray()
        return sub_K

    def get_sparse_k(self):
        """الحصول على K كمصفوفة متفرقة للكفاءة الحسابية"""
        if hasattr(self.K, "tocsr"):
            return self.K.tocsr()
        return sparse.csr_matrix(self.K)

    def expand_vocab(self, new_vocab_size):
        """توسيع مصفوفات الاقتران K و C و T عند إضافة كلمات جديدة ديناميكياً"""
        if new_vocab_size > self.vocab_size:
            # تحويل مؤقت لـ LIL للـ resize
            C_lil = self.C.tolil()
            K_lil = self.K.tolil()
            T_lil = self.T.tolil()
            
            C_lil.resize((new_vocab_size, new_vocab_size))
            K_lil.resize((new_vocab_size, new_vocab_size))
            T_lil.resize((new_vocab_size, new_vocab_size))
            
            self.C = C_lil.tocsr()
            self.K = K_lil.tocsr()
            self.T = T_lil.tocsr()
            
            self.vocab_size = new_vocab_size
