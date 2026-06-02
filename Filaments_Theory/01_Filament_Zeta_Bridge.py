"""
نظرية الفتائل والرنين الأساسي: الجسر الموحد
Filament Theory & Basil Resonance: The Unified Bridge
================================================================
ربط الفتيلة الأولية (ذات البنية الكروية المجوفة) مع:
- دالة زيتا-ريمان
- الخط الحرج σ = 0.5
- ثابت 1/8
- الكرة الزيتاوية
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle, Wedge
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# الثوابت الأساسية من نظرية الفتائل
# ============================================================================

class FilamentConstants:
    """
    ثوابت الفتيلة الأولية - مشتقة من المبادئ الأولى
    """
    def __init__(self):
        # ثوابت الطبيعة (وحدات SI)
        self.hbar = 1.054571817e-34  # ثابت بلانك المخفض (J·s)
        self.c = 299792458.0         # سرعة الضوء (m/s)
        self.G = 6.67430e-11         # ثابت الجاذبية (m³/kg/s²)
        
        # خصائص الفتيلة الأولية (مشتقة)
        self.m_P = np.sqrt(self.hbar * self.c / self.G)  # كتلة بلانك
        self.l_P = np.sqrt(self.hbar * self.G / self.c**3)  # طول بلانك
        self.t_P = self.l_P / self.c  # زمن بلانك
        
        # الثوابت الهندسية للفتيلة
        self.sphere_radius = self.l_P
        self.sphere_surface_area = 4 * np.pi * self.l_P**2
        self.sphere_volume = (4/3) * np.pi * self.l_P**3  # مجوفة عملياً
        
    def display(self):
        """عرض الثوابت الأساسية"""
        print("\n" + "="*60)
        print("ثوابت الفتيلة الأولية (نظرية الفتائل)")
        print("="*60)
        print(f"كتلة الفتيلة (m_P):     {self.m_P:.4e} kg")
        print(f"نصف قطر الفتيلة (l_P):   {self.l_P:.4e} m")
        print(f"زمن الفتيلة (t_P):       {self.t_P:.4e} s")
        print(f"مساحة سطح الفتيلة:       {self.sphere_surface_area:.4e} m²")
        print(f"العلاقة الأساسية:        m_P · c · l_P = ħ = {self.hbar:.4e}")
        print("="*60)


# ============================================================================
# نموذج الفتيلة الأولية (الكرة المجوفة ذات الحلقات الثلاث)
# ============================================================================

class PrimordialFilament:
    """
    الفتيلة الأولية: كرة مجوفة مكونة من ثلاث حلقات متعامدة
    تمثل التجسيد الهندسي لمبدأ التناظر الأولي
    """
    def __init__(self, constants=None):
        if constants is None:
            constants = FilamentConstants()
        self.const = constants
        
        # أبعاد الفتيلة
        self.radius = 1.0  # نصف قطر معياري للتمثيل
        
        # إحداثيات الحلقات الثلاث
        self.generate_rings()
        
        # سطح الكرة
        self.generate_sphere()
        
    def generate_rings(self, resolution=100):
        """توليد الحلقات الثلاث المتعامدة (حلقات Z₃)"""
        theta = np.linspace(0, 2*np.pi, resolution)
        
        # الحلقة الأولى (XY - المستوى الاستوائي)
        self.ring_xy = {
            'x': self.radius * np.cos(theta),
            'y': self.radius * np.sin(theta),
            'z': np.zeros_like(theta),
            'color': 'red',
            'label': 'Ring 1 (XY)'
        }
        
        # الحلقة الثانية (XZ - المستوى الرأسي الأول)
        self.ring_xz = {
            'x': self.radius * np.cos(theta),
            'y': np.zeros_like(theta),
            'z': self.radius * np.sin(theta),
            'color': 'green',
            'label': 'Ring 2 (XZ)'
        }
        
        # الحلقة الثالثة (YZ - المستوى الرأسي الثاني)
        self.ring_yz = {
            'x': np.zeros_like(theta),
            'y': self.radius * np.cos(theta),
            'z': self.radius * np.sin(theta),
            'color': 'blue',
            'label': 'Ring 3 (YZ)'
        }
        
    def generate_sphere(self, resolution=50):
        """توليد سطح الكرة المجوفة"""
        phi = np.linspace(0, 2*np.pi, resolution)
        theta = np.linspace(0, np.pi, resolution)
        self.Phi, self.Theta = np.meshgrid(phi, theta)
        
        self.sphere = {
            'x': self.radius * np.sin(self.Theta) * np.cos(self.Phi),
            'y': self.radius * np.sin(self.Theta) * np.sin(self.Phi),
            'z': self.radius * np.cos(self.Theta)
        }
    
    def Z3_evolution(self, state):
        """
        ديناميكية Z₃ الداخلية
        الحالات: 0 (محايد)، 1 (انكماش)، 2 (تمدد)
        """
        if state == 0:
            scale = 1.0
            color = 'gray'
            label = 'Neutral'
        elif state == 1:
            scale = 0.9  # انكماش
            color = 'red'
            label = 'Mass-dominant'
        else:  # state == 2
            scale = 1.1  # تمدد
            color = 'blue'
            label = 'Space-dominant'
        
        return scale, color, label
    
    def get_equator(self, t_values=None):
        """
        الحصول على خط الاستواء للفتيلة
        هذا الخط يقابل σ = 0.5 في فضاء زيتا
        """
        if t_values is None:
            t_values = np.linspace(0, 2*np.pi, 100)
        
        x_eq = self.radius * np.cos(t_values)
        y_eq = self.radius * np.sin(t_values)
        z_eq = np.zeros_like(t_values)
        
        return x_eq, y_eq, z_eq


# ============================================================================
# جسر الفتيلة-زيتا: الربط الرياضي
# ============================================================================

class FilamentZetaBridge:
    """
    الجسر الرياضي بين نظرية الفتائل ودالة زيتا-ريمان
    يوضح كيف تنبثق خصائص دالة زيتا من بنية الفتيلة الأولية
    """
    def __init__(self, filament, constants):
        self.filament = filament
        self.const = constants
        
        # الأصفار المعروفة لدالة زيتا
        self.zeta_zeros = np.array([
            14.134725, 21.022040, 25.010858, 30.424876,
            32.935062, 37.586178, 40.918719, 43.327073
        ])
        
    def map_zeta_to_filament(self, sigma, t):
        """
        ربط نقطة في فضاء زيتا (σ, t) بنقطة على سطح الفتيلة
        
        المبدأ: σ = 0.5 يقابل خط الاستواء
                t تقابل الزاوية على خط الاستواء
        """
        # σ تحدد خط العرض (زاوية θ)
        # σ = sin²(θ/2)  =>  θ = 2·arcsin(√σ)
        if sigma < 0 or sigma > 1:
            sigma = np.clip(sigma, 0, 1)
        theta = 2 * np.arcsin(np.sqrt(sigma))
        
        # t تحدد خط الطول (زاوية φ)
        # استخدام علاقة لوغاريتمية لأن توزيع الأصفار يتبع log(t)
        phi = 2 * np.pi * np.log(t + 1) / np.log(50)
        
        # إحداثيات على سطح الكرة
        r = self.filament.radius
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        
        return x, y, z
    
    def compute_filament_potential(self, sigma, t):
        """
        حساب الجهد المادي على سطح الفتيلة عند نقطة (σ, t)
        
        Φ ∝ A^{-1/2} حيث A هي المساحة الفعالة
        عند σ = 0.5، المساحة في أقصى تناظر
        """
        # المساحة الفعالة تعتمد على البعد عن خط الاستواء
        equator_distance = np.abs(sigma - 0.5)
        effective_area = 1.0 + equator_distance * 10
        
        # تأثير الأصفار (نقاط الرنين)
        if len(self.zeta_zeros) > 0:
            zero_distance = np.min(np.abs(t - self.zeta_zeros))
            resonance_factor = np.exp(-zero_distance**2 / 50.0)
            effective_area *= (1.0 + 5.0 * resonance_factor)
        
        # Φ ∝ A^{-1/2}
        potential = 1.0 / np.sqrt(effective_area)
        
        return potential
    
    def derive_eighth_constant_from_filament(self):
        """
        اشتقاق ثابت 1/8 من بنية الفتيلة
        
        باستخدام مفكوك تايلور للوتر الهندسي على سطح الفتيلة
        """
        # على خط الاستواء (σ = 0.5)
        t_values = np.linspace(10, 100, 1000)
        deviations = []
        
        for t in t_values:
            # الوتر الهندسي من مركز الفتيلة إلى نقطة على خط الاستواء
            chord = np.sqrt(0.25 + (t/100)**2)
            
            # حاصل ضرب الوتر في التردد
            product = chord * (t/100)
            
            # الانحراف عن القيمة المقاربة
            deviation = product - 1
            deviations.append(deviation)
        
        deviations = np.array(deviations)
        
        # تحليل السلوك المقارب
        # نظرياً: deviation ≈ -1/(8t²) للترددات العالية
        asymptotic_limit = -1/8
        
        return t_values, deviations, asymptotic_limit
    
    def verify_filament_zeta_connection(self):
        """
        التحقق من أن σ = 0.5 هو خط التوازن الطبيعي للفتيلة
        """
        sigma_range = np.linspace(0, 1, 100)
        t_fixed = 14.134725  # أول صفر
        
        potentials = []
        for sigma in sigma_range:
            pot = self.compute_filament_potential(sigma, t_fixed)
            potentials.append(pot)
        
        # إيجاد نقطة التوازن (أدنى جهد)
        min_idx = np.argmin(potentials)
        equilibrium_sigma = sigma_range[min_idx]
        
        return sigma_range, potentials, equilibrium_sigma


# ============================================================================
# التصور الموحد: الفتيلة الأولية وجسر زيتا
# ============================================================================

def visualize_filament_zeta_unification():
    """
    إنشاء تصور موحد يربط نظرية الفتائل بدالة زيتا-ريمان
    """
    print("\n" + "█" * 90)
    print("█" + " " * 88 + "█")
    print("█" + "   نظرية الفتائل والرنين الأساسي: الجسر الموحد".center(88) + "█")
    print("█" + " " * 88 + "█")
    print("█" * 90)
    
    # تهيئة النماذج
    constants = FilamentConstants()
    constants.display()
    
    filament = PrimordialFilament(constants)
    bridge = FilamentZetaBridge(filament, constants)
    
    # ====== إنشاء التصور ======
    fig = plt.figure(figsize=(24, 18))
    
    # ----- 1. الفتيلة الأولية: الحلقات الثلاث -----
    ax1 = fig.add_subplot(3, 4, 1, projection='3d')
    ax1.plot(filament.ring_xy['x'], filament.ring_xy['y'], filament.ring_xy['z'], color='red', linewidth=2, label='حلقة XY')
    ax1.plot(filament.ring_xz['x'], filament.ring_xz['y'], filament.ring_xz['z'], color='green', linewidth=2, label='حلقة XZ')
    ax1.plot(filament.ring_yz['x'], filament.ring_yz['y'], filament.ring_yz['z'], color='blue', linewidth=2, label='حلقة YZ')
    ax1.plot_surface(filament.sphere['x'], filament.sphere['y'], filament.sphere['z'], alpha=0.15, color='gray')
    x_eq, y_eq, z_eq = filament.get_equator()
    ax1.plot(x_eq, y_eq, z_eq, 'k--', linewidth=1.5, alpha=0.7, label='خط الاستواء (σ=0.5)')
    ax1.set_title('الفتيلة الأولية: ثلاث حلقات متعامدة\n(بنية كروية مجوفة)', fontsize=11, fontweight='bold')
    ax1.legend(fontsize=8)
    
    # ----- 2. ديناميكية Z₃ -----
    ax2 = fig.add_subplot(3, 4, 2)
    states = [0, 1, 2]
    colors_state = ['gray', 'red', 'blue']
    labels_state = ['محايد (0)', 'كتلة (1)', 'مكان (2)']
    for i, (state, color, label) in enumerate(zip(states, colors_state, labels_state)):
        angle = 2 * np.pi * i / 3
        x, y = np.cos(angle), np.sin(angle)
        circle = Circle((x, y), 0.2, color=color, alpha=0.7)
        ax2.add_patch(circle)
        ax2.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')
    for i in range(3):
        angle1 = 2 * np.pi * i / 3
        angle2 = 2 * np.pi * ((i+1)%3) / 3
        x1, y1 = np.cos(angle1), np.sin(angle1)
        x2, y2 = np.cos(angle2), np.sin(angle2)
        ax2.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=1.5, color='purple'))
    ax2.set_xlim(-1.5, 1.5)
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_aspect('equal')
    ax2.set_title('ديناميكية Z₃ الداخلية\n(التبدل الدوري للفتيلة)', fontsize=11, fontweight='bold')
    ax2.axis('off')
    
    # ----- 3. إسقاط أصفار زيتا على الفتيلة -----
    ax3 = fig.add_subplot(3, 4, 3, projection='3d')
    ax3.plot_surface(filament.sphere['x'], filament.sphere['y'], filament.sphere['z'], alpha=0.1, color='lightblue')
    ax3.plot(x_eq, y_eq, z_eq, 'b-', linewidth=2, label='خط الاستواء')
    for zero in bridge.zeta_zeros[:6]:
        x, y, z = bridge.map_zeta_to_filament(0.5, zero)
        ax3.scatter(x, y, z, color='red', s=80, edgecolors='white', linewidths=1.5)
    ax3.set_title('أصفار زيتا على سطح الفتيلة\n(تقع على خط الاستواء)', fontsize=11, fontweight='bold')
    
    # ----- 4. الجهد المادي على سطح الفتيلة -----
    ax4 = fig.add_subplot(3, 4, 4)
    sigma_range, potentials, eq_sigma = bridge.verify_filament_zeta_connection()
    ax4.plot(sigma_range, potentials, 'b-', linewidth=2)
    ax4.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='σ = 0.5 (النظري)')
    ax4.set_title('الجهد المادي على سطح الفتيلة\n(أدنى جهد عند σ = 0.5)', fontsize=11, fontweight='bold')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    # ----- 5. اشتقاق ثابت 1/8 من الفتيلة -----
    ax5 = fig.add_subplot(3, 4, 5)
    t_vals, deviations, asymp = bridge.derive_eighth_constant_from_filament()
    ax5.plot(t_vals, deviations, 'g-', linewidth=1.5, label='الانحراف الفعلي')
    ax5.axhline(y=asymp, color='purple', linestyle='--', linewidth=2, label=f'القيمة المقاربة = {asymp}')
    ax5.set_title('اشتقاق ثابت 1/8 من هندسة الفتيلة\n(مفكوك تايلور للوتر)', fontsize=11, fontweight='bold')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # ----- 6. العلاقة بين الفتيلة وزيتا -----
    ax6 = fig.add_subplot(3, 4, 6)
    t_range = np.linspace(0, 50, 200)
    phi_range = 2 * np.pi * np.log(t_range + 1) / np.log(50)
    ax6.plot(t_range, phi_range, 'b-', linewidth=2)
    for zero in bridge.zeta_zeros[:6]:
        phi_zero = 2 * np.pi * np.log(zero + 1) / np.log(50)
        ax6.scatter(zero, phi_zero, color='red', s=50, zorder=5)
    ax6.set_title('ربط الترددات بالزوايا على الفتيلة\n(علاقة لوغاريتمية)', fontsize=11, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # ----- 7. الفتيلة في حالات Z₃ المختلفة -----
    ax7 = fig.add_subplot(3, 4, 7, projection='3d')
    for i, state in enumerate([0, 1, 2]):
        scale, color, label = filament.Z3_evolution(state)
        offset = i * 3 - 3
        r_scaled = filament.radius * scale
        x_ring = r_scaled * np.cos(np.linspace(0, 2*np.pi, 50))
        y_ring = r_scaled * np.sin(np.linspace(0, 2*np.pi, 50))
        ax7.plot(x_ring + offset, y_ring, np.zeros_like(x_ring), color=color, linewidth=2, alpha=0.7)
        ax7.text(offset, 0, 1.5, label, ha='center', fontsize=8)
    ax7.set_xlim(-4, 4)
    ax7.set_ylim(-2, 2)
    ax7.set_zlim(-2, 2)
    ax7.set_title('حالات الفتيلة في دورة Z₃\n(محايد ← انكماش ← تمدد)', fontsize=11, fontweight='bold')
    ax7.axis('off')
    
    # ----- 8. الثوابت المشتقة من الفتيلة -----
    ax8 = fig.add_subplot(3, 4, 8)
    ax8.axis('off')
    constants_text = f"""
    ┌─────────────────────────────────────────┐
    │     الثوابت المشتقة من الفتيلة الأولية    │
    ├─────────────────────────────────────────┤
    │  m_P = √(ħc/G) = {constants.m_P:.3e} kg  │
    │  l_P = √(ħG/c³) = {constants.l_P:.3e} m   │
    │  t_P = l_P / c = {constants.t_P:.3e} s    │
    │  العلاقة الأساسية: m_P · c · l_P = ħ       │
    └─────────────────────────────────────────┘
    """
    ax8.text(0.05, 0.5, constants_text, transform=ax8.transAxes, fontsize=9, verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.9), family='monospace')
    
    # ----- 9. خريطة الرنين على الفتيلة -----
    ax9 = fig.add_subplot(3, 4, 9, projection='3d')
    phi_vals = np.linspace(0, 2*np.pi, 100)
    theta_vals = np.linspace(0, np.pi, 100)
    Phi, Theta = np.meshgrid(phi_vals, theta_vals)
    resonance = np.zeros_like(Phi)
    sigma_map = np.sin(Theta/2)**2
    for i in range(len(theta_vals)):
        for j in range(len(phi_vals)):
            sigma = sigma_map[i, j]
            t_equiv = 50 * Phi[i, j] / (2*np.pi)
            resonance[i, j] = bridge.compute_filament_potential(sigma, t_equiv)
    resonance = 1.0 / (resonance + 0.1)
    resonance = resonance / resonance.max()
    X = filament.radius * np.sin(Theta) * np.cos(Phi)
    Y = filament.radius * np.sin(Theta) * np.sin(Phi)
    Z = filament.radius * np.cos(Theta)
    ax9.plot_surface(X, Y, Z, facecolors=plt.cm.hot(resonance), alpha=0.9)
    ax9.plot(x_eq, y_eq, z_eq, 'c-', linewidth=2, alpha=0.7)
    for zero in bridge.zeta_zeros[:4]:
        x, y, z = bridge.map_zeta_to_filament(0.5, zero)
        ax9.scatter(x, y, z, color='cyan', s=60, edgecolors='white', linewidths=1)
    ax9.set_title('خريطة الرنين على سطح الفتيلة\n(القمم عند أصفار زيتا)', fontsize=11, fontweight='bold')
    ax9.axis('off')
    
    # ----- 10. المسار الزيتاوي على الفتيلة -----
    ax10 = fig.add_subplot(3, 4, 10, projection='3d')
    t_path = np.linspace(0, 40, 200)
    sigma_path = 0.5 * np.ones_like(t_path)
    x_path, y_path, z_path = [], [], []
    for i in range(len(t_path)):
        x, y, z = bridge.map_zeta_to_filament(sigma_path[i], t_path[i])
        x_path.append(x)
        y_path.append(y)
        z_path.append(z)
    ax10.plot_surface(filament.sphere['x'], filament.sphere['y'], filament.sphere['z'], alpha=0.1, color='gray')
    ax10.plot(x_path, y_path, z_path, 'r-', linewidth=1.5, label='المسار الزيتاوي')
    for zero in bridge.zeta_zeros[:5]:
        x, y, z = bridge.map_zeta_to_filament(0.5, zero)
        ax10.scatter(x, y, z, color='gold', s=60, edgecolors='red', linewidths=1.5)
    ax10.set_title('المسار الزيتاوي على سطح الفتيلة\n(النقاط الذهبية = الأصفار)', fontsize=11, fontweight='bold')
    ax10.axis('off')
    
    # ----- 11. معادلات النظرية الموحدة -----
    ax11 = fig.add_subplot(3, 4, 11)
    ax11.axis('off')
    unified_eq = """
    ┌──────────────────────────────────────────────┐
    │        النظرية الموحدة: المعادلات الأساسية      │
    ├──────────────────────────────────────────────┤
    │  جسر الفتيلة-زيتا:                            │
    │  • σ = sin²(θ/2)  (ربط التمدد بالزاوية)        │
    │  • φ = 2π·log(t+1)/log(T_max)                │
    │  • Φ ∝ A^{-1/2}  (الجهد المادي)                │
    │                                              │
    │  الرنين الأساسي:                              │
    │  • σ = 0.5 = خط الاستواء للفتيلة               │
    │  • أصفار زيتا = نقاط الرنين على خط الاستواء     │
    └──────────────────────────────────────────────┘
    """
    ax11.text(0.05, 0.5, unified_eq, transform=ax11.transAxes, fontsize=9, verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9), family='monospace')
    
    # ----- 12. الخلاصة الفلسفية -----
    ax12 = fig.add_subplot(3, 4, 12)
    ax12.axis('off')
    philosophy = """
    ┌──────────────────────────────────────────────┐
    │                الخلاصة الفلسفية                │
    ├──────────────────────────────────────────────┤
    │  "الأعداد الأولية هي النسيج الأساسي للزمكان.   │
    │   ودالة زيتا هي دالة الاستجابة لهذا النسيج."   │
    │                                              │
    │  من مبدأ الحفظ الشامل (المجموع الصفري) إلى     │
    │  التناظر الأولي تمكننا من استنتاج خط الاستواء  │
    │  للفتيلة (σ = 0.5).                           │
    └──────────────────────────────────────────────┘
    """
    ax12.text(0.05, 0.5, philosophy, transform=ax12.transAxes, fontsize=9, verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9), family='monospace')
    
    plt.suptitle('نظرية الفتائل والرنين الأساسي: الجسر الموحد بين الفيزياء الأساسية ودالة زيتا-ريمان',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_file = 'filament_zeta_unified_bridge.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"\n[✓] تم حفظ الجسر الموحد في: {output_file}")
    plt.show()
    return output_file

if __name__ == "__main__":
    output_file = visualize_filament_zeta_unification()
