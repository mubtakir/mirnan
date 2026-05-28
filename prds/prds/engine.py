import numpy as np
from prds.lexicon import PHYSICAL_CONSTANTS

def gravitational_force(word_i, word_j, distance: int) -> np.ndarray:
    """
    F_ij = G * m_i * m_j / r²
    تعيد متجه قوة في الفضاء الطوري تؤثر على word_i من word_j
    
    distance: المسافة (عدد الكلمات بينهما + 1)
    """
    G = PHYSICAL_CONSTANTS["G"]
    r_sq = float(max(distance, 1) ** 2)
    force_magnitude = G * word_i.mass * word_j.mass / r_sq
    
    # اتجاه القوة: من الطور الحالي باتجاه طور word_j
    delta_phase = word_j.phase_vector - word_i.phase_vector
    norm = np.linalg.norm(delta_phase)
    direction = delta_phase / (norm + 1e-10)
    
    return force_magnitude * direction

class KuramotoEngine:
    """
    المحرك الديناميكي (Kuramoto Core Engine)
    يحاكي نظام المذبذبات المقترنة لحل معادلة كوراموتو المعدلة باستخدام تكامل Runge-Kutta 4 (RK4).
    """
    def __init__(self, lexicon, coupling, alpha=0.5):
        self.lexicon = lexicon
        self.coupling = coupling
        self.alpha = alpha
        self.dim = self.lexicon.dim if hasattr(self.lexicon, 'dim') else 1
        self.scope_stack = []
        self.step_gate_threshold = 0.85
        self.gravity_scale = PHYSICAL_CONSTANTS.get("gravity_scale", 1.0)
        # مصفوفة الرنين من الدرجة الثانية (K^2)
        self.K2 = None
        self.last_K_eff_history = None

    def push_scope(self, local_K):
        """دفع مصفوفة اقتران محلية إلى مكدس النطاقات البرمجية"""
        # تحويل المصفوفة المتفرقة إلى كثيفة لدعم np.pad و np.ix_
        if hasattr(local_K, 'toarray'):
            local_K = local_K.toarray()
        target_size = self.coupling.K.shape[0]
        if local_K.shape[0] < target_size:
            pad_size = target_size - local_K.shape[0]
            local_K = np.pad(local_K, ((0, pad_size), (0, pad_size)), mode='constant', constant_values=0.0)
        self.scope_stack.append(local_K)

    def pop_scope(self):
        """إزالة مصفوفة الاقتران المحلية والعودة للنطاق الأوسع"""
        if self.scope_stack:
            return self.scope_stack.pop()
        return None

    def _precompute_second_order(self):
        """تعطيل الحساب المسبق لـ K2 لتوفير الذاكرة وسرعة المعالجة للمدونات الضخمة"""
        self.K2 = None

    def update_coupling_ref(self):
        """تعطيل الحساب المسبق لـ K2 لتوفير الذاكرة وسرعة المعالجة للمدونات الضخمة"""
        pass

    def _calc_derivatives(self, phases, active_mask, omega, K_sub, K2_active, pinned_mask, word_ids=None, temperature=0.0, gravity_scale=None):
        """
        حساب المشتقات dθ_i/dt باستخدام معادلة كوراموتو المعدلة للفضاء المتجهي (HD-ROV).
        """
        # phases shape: (N, D)
        diffs = phases[None, :, :] - phases[:, None, :] # shape: (N, N, D)
        sin_diffs = np.sin(diffs)
        
        is_all_active = np.all(active_mask)
        if not is_all_active:
            sin_diffs_masked = sin_diffs * active_mask[None, :, None]
        else:
            sin_diffs_masked = sin_diffs
        
        direct_sync_all = np.sum(K_sub[:, :, None] * sin_diffs_masked, axis=1)
        if K2_active is not None and K2_active.size > 0:
            indirect_sync_all = self.alpha * np.sum(K2_active[:, :, None] * sin_diffs_masked, axis=1)
        else:
            indirect_sync_all = 0.0
            
        # ---- Gravitational coupling ----
        grav_contribution = np.zeros_like(phases)
        n = len(phases)
        if word_ids is not None and len(word_ids) == n:
            wps = []
            for wid in word_ids:
                w_str = self.lexicon.id2word.get(wid, "<UNK>")
                wp = self.lexicon.word_registry.compute_or_retrieve(w_str)
                wps.append(wp)
            for i in range(n):
                if not active_mask[i]:
                    continue
                for j in range(n):
                    if i == j or not active_mask[j]:
                        continue
                    dist = abs(i - j)
                    f_ij = gravitational_force(wps[i], wps[j], dist)
                    # Hebbian force using absolute force component to keep gravity attractive
                    # Apply a scaling factor from PHYSICAL_CONSTANTS to prevent gravity from overwhelming Hebbian coupling
                    if gravity_scale is None:
                        gravity_scale = self.gravity_scale
                    grav_contribution[i] += gravity_scale * np.abs(f_ij) * np.sin(phases[j] - phases[i])
        
        dtheta = omega + direct_sync_all + indirect_sync_all + grav_contribution
        
        # ---- Thermal noise ----
        kB = PHYSICAL_CONSTANTS["kB"]
        std = np.sqrt(2.0 * kB * max(temperature, 0.0))
        if std > 0:
            noise = np.random.normal(0, std, size=phases.shape)
            dtheta += noise
        
        dtheta[pinned_mask, :] = omega[pinned_mask, :]
        
        if not is_all_active:
            dtheta[~active_mask, :] = 0.0
            
        return dtheta

    def simulate(self, word_ids, t_span=(0, 10), num_steps=150, sequential=True, word_entry_interval=1.2, initial_phases=None, fast_mode=False, irab_biases=None, tau=8.0, temperature=0.0, gravity_scale=None):
        """
        تشغيل محاكاة كوراموتو على كلمات الجملة باستخدام تكامل RK4.
        يدعم الدخول المتتابع للكلمات وتتبع K_eff عبر الزمن، بالإضافة إلى الأطوار الابتدائية المخصصة (initial_phases).

        irab_biases: قائمة إزاحات الترددات الإعرابية (rad/s) لكل كلمة.
                     None = بلا تشكيل (كل الإزاحات = 0).
                     الفاعل المرفوع (+0.30) يصبح المذبذب القائد في المزامنة.
        tau: ثابت تلاشي الانتباه/الذاكرة قصيرة المدى بالكلمات (None لتعطيله).
        """
        n = len(word_ids)
        if n == 0:
            return [], [], np.zeros((0,0))

        dt = (t_span[1] - t_span[0]) / num_steps
        times = np.linspace(t_span[0], t_span[1], num_steps)
        
        # استخراج الترددات الذاتية والمصفوفات الفرعية
        omega = np.array([self.lexicon.get_omega(wid) for wid in word_ids]) # shape: (N, D)
        if len(omega.shape) == 1:
            omega = omega[:, None]

        # ← تطبيق إزاحة الإعراب النحوي (I'rab Phase Bias)
        if irab_biases is not None:
            irab_arr = np.array(irab_biases[:len(omega)], dtype=float)
            omega[:, 0] = omega[:, 0] + irab_arr
        if self.scope_stack:
            active_K = self.scope_stack[-1]
            if hasattr(active_K, 'toarray'):
                active_K = active_K.toarray()
            grid = np.ix_(word_ids, word_ids)
            K_sub = active_K[grid]
        else:
            K_sub = self.coupling.get_coupling_submatrix(word_ids)
        
        # ← تطبيق تلاشي الاقتران بناءً على المسافة الموضعية (Positional Attention Decay)
        if tau is not None and n > 1:
            indices = np.arange(n)
            dist_matrix = np.abs(indices[:, None] - indices[None, :])
            decay_matrix = np.exp(-dist_matrix / tau)
            K_sub = K_sub * decay_matrix


        pinned_mask = np.array([wid in self.lexicon.pinned_words for wid in word_ids], dtype=bool)

        # مصفوفات التتبع
        if not fast_mode:
            phases_history = np.zeros((num_steps, n, self.dim))
            r_history = np.zeros(num_steps)
            self.last_K_eff_history = np.zeros((num_steps, n, n))
        else:
            phases_history = None
            r_history = None
            self.last_K_eff_history = None
        
        active_mask = np.zeros(n, dtype=bool)
        if not sequential:
            active_mask[:] = True
        else:
            active_mask[0] = True  # الكلمة الأولى فعالة من البداية

        current_phases = np.zeros((n, self.dim))
        if initial_phases is not None:
            if len(initial_phases.shape) == 1:
                current_phases[:, 0] = initial_phases
            else:
                current_phases[:] = initial_phases
        else:
            current_phases += np.random.normal(0, 0.05, (n, self.dim))

        # حساب K2_active الأولي (ثابت إذا لم يكن متتابعاً)
        K2_active = np.dot(K_sub[:, active_mask], K_sub[active_mask, :])

        for step, t in enumerate(times):
            if sequential:
                mask_changed = False
                for i in range(n):
                    if t >= i * word_entry_interval and not active_mask[i]:
                        # التحقق من بوابة التماسك (Coherence Gating) للكلمات المرحلية
                        if i > 0 and step > 0:
                            w_str = self.lexicon.id2word.get(word_ids[i], "")
                            if w_str.startswith("<الخطوة_") or w_str in ["<التحقق>", "<النتيجة>"]:
                                if not fast_mode and r_history[step-1] < self.step_gate_threshold:
                                    # كبح الدخول وتأخير فتح البوابة حتى يرتفع التماسك
                                    continue
                        active_mask[i] = True
                        mask_changed = True
                        if initial_phases is None and np.any(active_mask[:i]):
                            active_phases = current_phases[:i][active_mask[:i]]
                            # أخذ متوسط الطور لكل بُعد على حدة
                            mean_phase = np.angle(np.mean(np.exp(1j * active_phases), axis=0))
                            current_phases[i, :] = mean_phase + np.random.normal(0, 0.1, self.dim)
                
                if mask_changed:
                    K2_active = np.dot(K_sub[:, active_mask], K_sub[active_mask, :])

            # تكامل Runge-Kutta 4 (RK4) لحساب الأطوار الجديدة بدقة عالية
            # تكامل Runge-Kutta 4 (RK4) لحساب الأطوار الجديدة بدقة عالية
            k1 = self._calc_derivatives(current_phases, active_mask, omega, K_sub, K2_active, pinned_mask, word_ids=word_ids, temperature=temperature, gravity_scale=gravity_scale)
            k2 = self._calc_derivatives(current_phases + 0.5 * dt * k1, active_mask, omega, K_sub, K2_active, pinned_mask, word_ids=word_ids, temperature=temperature, gravity_scale=gravity_scale)
            k3 = self._calc_derivatives(current_phases + 0.5 * dt * k2, active_mask, omega, K_sub, K2_active, pinned_mask, word_ids=word_ids, temperature=temperature, gravity_scale=gravity_scale)
            k4 = self._calc_derivatives(current_phases + dt * k3, active_mask, omega, K_sub, K2_active, pinned_mask, word_ids=word_ids, temperature=temperature, gravity_scale=gravity_scale)
            
            current_phases = current_phases + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
            current_phases = (current_phases + np.pi) % (2 * np.pi) - np.pi
            
            if not fast_mode:
                phases_history[step, :, :] = current_phases
                
                # حساب معامل التماسك r(t) كمتوسط للتماسك عبر جميع الأبعاد
                active_count = np.sum(active_mask)
                if active_count > 0:
                    z = np.mean(np.exp(1j * current_phases[active_mask]), axis=0) # (D,)
                    r_history[step] = np.mean(np.abs(z))
                else:
                    r_history[step] = 0.0

                # تتبع K_eff عبر الزمن بنسخة مجهّزة بالكامل بـ NumPy (يعتمد على البعد الأول للتبسيط)
                diffs = current_phases[:, 0, None] - current_phases[None, :, 0]
                step_K_eff = (K_sub + self.alpha * K2_active) * np.cos(diffs)
                np.fill_diagonal(step_K_eff, 0.0)
                mask_2d = active_mask[:, None] & active_mask[None, :]
                step_K_eff[~mask_2d] = 0.0
                self.last_K_eff_history[step, :, :] = step_K_eff

        if fast_mode:
            return times, current_phases, None, None

        # مصفوفة الاقتران الفعال النهائية
        K_eff = self.last_K_eff_history[-1, :, :]
        return times, phases_history, r_history, K_eff
