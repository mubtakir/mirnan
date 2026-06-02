"""
نظرية الفتائل - الجزء التاسع: مختبر التوحيد الهندسي
Filament Theory - Part IX: Geometric Unification Laboratory
================================================================
من المسافة التربيعية (r²) إلى مساحة السطح الكروي (4πr²)
التوحيد الميكانيكي لقوانين نيوتن وكولوم

المبادئ:
1. المقام في قوانين القوى هو مساحة سطح كروي 4πr² وليس r²
2. القوة = (ثابت الاستجابة / مساحة السطح) × (حاصل ضرب المصادر)
3. الثوابت G'=4πG و k_e'=1/ε₀ هي معاملات استجابة الوسط الفتيلي
4. الجاذبية والكهرومغناطيسية تجليان لمبدأ هندسي واحد
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyBboxPatch, Rectangle
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# الثوابت الفيزيائية الهندسية
# ============================================================================

class GeometricConstants:
    """الثوابت الفيزيائية بصيغتها الهندسية الجديدة"""
    
    def __init__(self):
        # الثوابت التقليدية
        self.G = 6.67430e-11      # m³/kg/s²
        self.k_e = 8.9875517923e9  # N·m²/C²
        self.epsilon_0 = 8.8541878128e-12  # F/m
        self.c = 299792458.0      # m/s
        
        # الثوابت الهندسية الجديدة
        self.G_prime = 4 * np.pi * self.G
        self.k_e_prime = 1.0 / self.epsilon_0
        
        # نسبة الحساسية
        self.sensitivity_ratio = self.k_e_prime / self.G_prime
        
        # ثوابت بلانك
        self.hbar = 1.054571817e-34
        self.m_P = np.sqrt(self.hbar * self.c / self.G)
        self.l_P = np.sqrt(self.hbar * self.G / self.c**3)
        
    def display(self):
        print("\n" + "="*80)
        print("الثوابت الفيزيائية - الصيغة الهندسية الجديدة")
        print("="*80)
        print(f"G (تقليدي):        {self.G:.6e} m³/kg/s²")
        print(f"G' = 4πG:          {self.G_prime:.6e} m³/kg/s²")
        print("-"*80)
        print(f"k_e (تقليدي):       {self.k_e:.6e} N·m²/C²")
        print(f"k_e' = 1/ε₀:        {self.k_e_prime:.6e} F⁻¹·m")
        print("-"*80)
        print(f"نسبة الحساسية:      {self.sensitivity_ratio:.6e}")
        print(f"log₁₀(k_e'/G'):     {np.log10(self.sensitivity_ratio):.2f}")
        print("="*80)


# ============================================================================
# نموذج توزيع التأثير على السطح الكروي
# ============================================================================

class SphericalDistribution:
    """
    توزيع التأثير على مساحة سطح كروي
    المبدأ الهندسي الموحد لجميع القوى الأساسية
    """
    
    def __init__(self, const):
        self.const = const
        
    def surface_area(self, r):
        """مساحة السطح الكروي عند نصف قطر r"""
        return 4 * np.pi * r**2
    
    def intensity_from_source(self, source_strength, r, response_coefficient):
        """
        شدة التأثير عند مسافة r من مصدر
        I = (response × source) / A(r)
        """
        A = self.surface_area(r)
        return response_coefficient * source_strength / A
    
    def force_between_sources(self, source1, source2, r, response_coefficient):
        """
        القوة بين مصدرين
        F = source2 × I = (response × source1 × source2) / A(r)
        """
        A = self.surface_area(r)
        return response_coefficient * source1 * source2 / A
    
    def visualize_distribution(self, r_max=5.0, resolution=100):
        """
        تصور توزيع التأثير على الأسطح الكروية
        """
        # إنشاء شبكة للرسم
        x = np.linspace(-r_max, r_max, resolution)
        y = np.linspace(-r_max, r_max, resolution)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        
        # شدة التأثير (تتناسب عكسياً مع المساحة)
        R_safe = np.maximum(R, 0.1)
        intensity = 1.0 / self.surface_area(R_safe)
        
        return X, Y, R, intensity


# ============================================================================
# مقارنة القوى: نيوتن وكولوم بصيغتهما الهندسية
# ============================================================================

class UnifiedForceLaws:
    """
    قوانين القوى بصيغتها الهندسية الموحدة
    F = (ثابت الاستجابة / 4πr²) × (مصدر1 × مصدر2)
    """
    
    def __init__(self, const):
        self.const = const
        
    def gravity_force(self, m1, m2, r):
        """
        قانون الجاذبية - الصيغة الهندسية
        F_g = (G' / 4πr²) × m1 × m2
        """
        A = 4 * np.pi * r**2
        return self.const.G_prime * m1 * m2 / A
    
    def electric_force(self, q1, q2, r):
        """
        قانون كولوم - الصيغة الهندسية
        F_e = (k_e' / 4πr²) × q1 × q2
        """
        A = 4 * np.pi * r**2
        return self.const.k_e_prime * q1 * q2 / A
    
    def compare_forces(self, mass1, mass2, charge1, charge2, r):
        """
        مقارنة القوتين عند نفس المسافة
        """
        F_g = self.gravity_force(mass1, mass2, r)
        F_e = self.electric_force(charge1, charge2, r)
        
        return {
            'gravity': F_g,
            'electric': F_e,
            'ratio': abs(F_e / F_g) if F_g != 0 else np.inf,
            'same_geometric_form': True
        }
    
    def unified_formula(self):
        """
        الصيغة الموحدة للقوتين
        """
        formula = """
        ┌─────────────────────────────────────────────────────────────┐
        │           الصيغة الموحدة لقوانين القوى                        │
        ├─────────────────────────────────────────────────────────────┤
        │                                                             │
        │                    ثابت الاستجابة                             │
        │   القوة = ───────────────────── × (مصدر₁ × مصدر₂)            │
        │               مساحة السطح الكروي                              │
        │                                                             │
        │   حيث:                                                       │
        │   • مساحة السطح الكروي = 4πr²                                │
        │   • للجاذبية: ثابت الاستجابة = G' = 4πG                      │
        │   • للكهرباء: ثابت الاستجابة = k_e' = 1/ε₀                   │
        │                                                             │
        └─────────────────────────────────────────────────────────────┘
        """
        return formula


# ============================================================================
# نموذج تيار الامتصاص للجاذبية
# ============================================================================

class AbsorptionCurrentModel:
    """
    الجاذبية كتيار امتصاص يتوزع على سطح كروي
    """
    
    def __init__(self, const):
        self.const = const
        
    def absorption_rate(self, mass):
        """
        معدل الامتصاص الكلي للكتلة
        J₀ = β × M
        """
        beta = self.const.G_prime  # ثابت التناسب
        return beta * mass
    
    def current_density(self, mass, r):
        """
        كثافة تيار الامتصاص عند مسافة r
        J(r) = J₀ / (4πr²)
        """
        J0 = self.absorption_rate(mass)
        A = 4 * np.pi * r**2
        return J0 / A
    
    def acceleration_from_current(self, mass, r, test_mass=1.0):
        """
        التعجيل الجذبوي من تيار الامتصاص
        a = α × J(r) / m_test
        """
        J = self.current_density(mass, r)
        alpha = 1.0  # ثابت التناسب
        
        return alpha * J / test_mass
    
    def verify_inverse_square(self, mass, r_range):
        """
        التحقق من قانون التربيع العكسي من توزيع السطح الكروي
        """
        accelerations = []
        for r in r_range:
            a = self.acceleration_from_current(mass, r)
            accelerations.append(a)
        
        return np.array(accelerations)


# ============================================================================
# معادلات ماكسويل المادية
# ============================================================================

class MaterialMaxwellEquations:
    """
    معادلات ماكسويل المادية للجاذبية
    توحيد الجاذبية والكهرومغناطيسية
    """
    
    def __init__(self, const):
        self.const = const
        
        # المعاملات المادية
        self.epsilon_g = 1.0 / self.const.G_prime  # السماحية الجاذبية
        self.mu_g = 1.0 / (self.epsilon_g * self.const.c**2)  # النفاذية الجاذبية
        
    def gauss_law_gravity(self, mass_density, volume_element):
        """
        قانون غاوس للجاذبية
        ∇·g = -ρ_m / ε_g
        """
        return -mass_density / self.epsilon_g
    
    def wave_speed(self):
        """
        سرعة الموجات الجاذبية
        c_g = 1/√(μ_g ε_g)
        """
        c_g = 1.0 / np.sqrt(self.mu_g * self.epsilon_g)
        return c_g
    
    def display_equations(self):
        """
        عرض معادلات ماكسويل المادية
        """
        equations = f"""
        ┌─────────────────────────────────────────────────────────────┐
        │              معادلات ماكسويل المادية للجاذبية                 │
        ├─────────────────────────────────────────────────────────────┤
        │                                                             │
        │  1. ∇·g = -ρ_m / ε_g           (قانون غاوس)                 │
        │  2. ∇×g = -∂B_g/∂t             (قانون فاراداي)              │
        │  3. ∇·B_g = 0                  (قانون غاوس المغناطيسي)       │
        │  4. ∇×B_g = μ_g J_m + μ_g ε_g ∂g/∂t  (قانون أمبير-ماكسويل)  │
        │                                                             │
        │  الثوابت:                                                    │
        │  • ε_g = 1/G' = {self.epsilon_g:.6e} kg·s²/m³              │
        │  • μ_g = 1/(ε_g c²) = {self.mu_g:.6e} m/kg                 │
        │  • c_g = 1/√(μ_g ε_g) = {self.wave_speed():.6e} m/s        │
        │                                                             │
        └─────────────────────────────────────────────────────────────┘
        """
        return equations
    
    def analogy_table(self):
        """
        جدول التناظر بين الكهرومغناطيسية والجاذبية
        """
        table = """
        ┌─────────────────────────────────────────────────────────────┐
        │           جدول التناظر: الكهرومغناطيسية ↔ الجاذبية            │
        ├─────────────────────────────────────────────────────────────┤
        │                                                             │
        │  كهرومغناطيسية          │  جاذبية (مادية)                    │
        │  ─────────────────────────────────────────────────────────  │
        │  الشحنة q              │  الكتلة m                          │
        │  المجال E              │  المجال g (تسارع)                  │
        │  الجهد V               │  الجهد المادي Φ = a·s              │
        │  ε₀                    │  ε_g = 1/G'                        │
        │  μ₀                    │  μ_g                               │
        │  c = 1/√(μ₀ε₀)         │  c_g = 1/√(μ_g ε_g) = c            │
        │  القوة F = qE          │  القوة F = m g                     │
        │                                                             │
        └─────────────────────────────────────────────────────────────┘
        """
        return table


# ============================================================================
# التصور الشامل للتوحيد الهندسي
# ============================================================================

def visualize_geometric_unification():
    """إنشاء تصور شامل للتوحيد الهندسي لقوانين القوى"""
    
    print("\n" + "█" * 100)
    print("█" + " " * 98 + "█")
    print("█" + "   نظرية الفتائل - الجزء التاسع: مختبر التوحيد الهندسي".center(98) + "█")
    print("█" + "   من r² إلى 4πr²: الاكتشاف الهندسي الثوري".center(98) + "█")
    print("█" + " " * 98 + "█")
    print("█" * 100)
    
    # تهيئة
    const = GeometricConstants()
    const.display()
    
    sphere_dist = SphericalDistribution(const)
    unified = UnifiedForceLaws(const)
    absorption = AbsorptionCurrentModel(const)
    maxwell = MaterialMaxwellEquations(const)
    
    # ====== توليد البيانات ======
    
    # توزيع التأثير على السطح الكروي
    X, Y, R, intensity = sphere_dist.visualize_distribution(r_max=5.0)
    
    # مقارنة القوى
    r_values = np.logspace(-2, 2, 100)
    F_g_values = [unified.gravity_force(1.0, 1.0, r) for r in r_values]
    F_e_values = [unified.electric_force(1.0, 1.0, r) for r in r_values]
    
    # مقارنة لبروتون وإلكترون
    m_p = 1.67e-27
    m_e = 9.11e-31
    e = 1.6e-19
    comparison = unified.compare_forces(m_p, m_e, e, -e, 5.29e-11)
    
    # التحقق من قانون التربيع العكسي
    r_verify = np.logspace(-1, 2, 50)
    a_verify = absorption.verify_inverse_square(1.0, r_verify)
    
    # سرعة الموجة
    c_g = maxwell.wave_speed()
    
    # ====== إنشاء التصور ======
    fig = plt.figure(figsize=(32, 28))
    
    # ----- 1. شعار التوحيد الهندسي -----
    ax1 = fig.add_subplot(4, 6, 1)
    ax1.axis('off')
    
    logo = f"""
    ┌─────────────────────────────────────┐
    │    🌍 التوحيد الهندسي للقوى 🌍       │
    │                                     │
    │      r²  →  4πr²                   │
    │                                     │
    │   المسافة التربيعية  →  مساحة السطح   │
    │                                     │
    │   G' = 4πG = {const.G_prime:.3e}  │
    │   k_e' = 1/ε₀ = {const.k_e_prime:.3e} │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax1.text(0.05, 0.5, logo, transform=ax1.transAxes,
             fontsize=9, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='gold', alpha=0.8),
             family='monospace')
    
    # ----- 2. المبدأ الهندسي -----
    ax2 = fig.add_subplot(4, 6, 2)
    ax2.axis('off')
    
    principle = """
    ┌─────────────────────────────────────┐
    │      المبدأ الهندسي الموحد            │
    ├─────────────────────────────────────┤
    │                                     │
    │  "تأثير أي مصدر نقطي ينتشر بشكل       │
    │   متناظر في جميع الاتجاهات، ويتوزع     │
    │   تأثيره الكلي على مساحة سطح كروي.     │
    │   شدة التأثير تتناسب عكسياً مع         │
    │   هذه المساحة."                      │
    │                                     │
    │   A(r) = 4πr²                       │
    │                                     │
    │   I(r) = I₀ / A(r)                  │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax2.text(0.05, 0.5, principle, transform=ax2.transAxes,
             fontsize=9, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
             family='monospace')
    
    # ----- 3. توزيع التأثير على السطح الكروي -----
    ax3 = fig.add_subplot(4, 6, 3)
    
    # رسم دوائر متحدة المركز
    for r in [1, 2, 3, 4]:
        circle = Circle((0, 0), r, fill=False, color='blue', alpha=0.3, linewidth=1)
        ax3.add_patch(circle)
    
    ax3.set_xlim(-5, 5)
    ax3.set_ylim(-5, 5)
    ax3.set_aspect('equal')
    ax3.set_xlabel('X', fontsize=9)
    ax3.set_ylabel('Y', fontsize=9)
    ax3.set_title('الأسطح الكروية متحدة المركز\nA(r) = 4πr²', fontsize=10, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # إضافة مصدر في المركز
    ax3.scatter(0, 0, color='red', s=100, marker='*', zorder=10)
    
    # ----- 4. شدة التأثير كدالة في المساحة -----
    ax4 = fig.add_subplot(4, 6, 4)
    
    r_plot = np.linspace(1, 5, 100)
    A_plot = sphere_dist.surface_area(r_plot)
    I_plot = 1.0 / A_plot
    
    ax4.plot(r_plot, I_plot, 'b-', linewidth=2, label='I(r) = 1/A(r)')
    ax4.set_xlabel('نصف القطر r', fontsize=9)
    ax4.set_ylabel('شدة التأثير I', fontsize=9)
    ax4.set_title('شدة التأثير تتناسب عكسياً\nمع مساحة السطح الكروي', fontsize=10, fontweight='bold')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    # ----- 5. خريطة حرارية للتأثير -----
    ax5 = fig.add_subplot(4, 6, 5)
    
    im = ax5.imshow(intensity, extent=[-5, 5, -5, 5], origin='lower', 
                    cmap='hot', interpolation='bilinear')
    ax5.scatter(0, 0, color='cyan', s=100, marker='*', edgecolors='white', linewidths=1)
    ax5.set_xlabel('X', fontsize=9)
    ax5.set_ylabel('Y', fontsize=9)
    ax5.set_title('خريطة حرارية لشدة التأثير\n(تتناقص مع r²)', fontsize=10, fontweight='bold')
    plt.colorbar(im, ax=ax5, label='شدة التأثير')
    
    # ----- 6. الصيغة الموحدة -----
    ax6 = fig.add_subplot(4, 6, 6)
    ax6.axis('off')
    
    unified_formula = unified.unified_formula()
    ax6.text(0.05, 0.5, unified_formula, transform=ax6.transAxes,
             fontsize=8, verticalalignment='center',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9),
             family='monospace')
    
    # ----- 7. قانون الجاذبية - الصيغة الهندسية -----
    ax7 = fig.add_subplot(4, 6, 7)
    
    ax7.loglog(r_values, F_g_values, 'b-', linewidth=2, label='F_g')
    ax7.loglog(r_values, const.G / r_values**2, 'b--', alpha=0.5, label='G/r²')
    ax7.set_xlabel('المسافة r', fontsize=9)
    ax7.set_ylabel('القوة F_g', fontsize=9)
    ax7.set_title("قانون الجاذبية\nF_g = G' m₁ m₂ / 4πr²", fontsize=10, fontweight='bold')
    ax7.legend(fontsize=7)
    ax7.grid(True, alpha=0.3)
    
    # ----- 8. قانون كولوم - الصيغة الهندسية -----
    ax8 = fig.add_subplot(4, 6, 8)
    
    ax8.loglog(r_values, np.abs(F_e_values), 'r-', linewidth=2, label='|F_e|')
    ax8.loglog(r_values, const.k_e / r_values**2, 'r--', alpha=0.5, label='k_e/r²')
    ax8.set_xlabel('المسافة r', fontsize=9)
    ax8.set_ylabel('القوة |F_e|', fontsize=9)
    ax8.set_title("قانون كولوم\nF_e = k_e' q₁ q₂ / 4πr²", fontsize=10, fontweight='bold')
    ax8.legend(fontsize=7)
    ax8.grid(True, alpha=0.3)
    
    # ----- 9. مقارنة القوتين -----
    ax9 = fig.add_subplot(4, 6, 9)
    
    ax9.loglog(r_values, F_g_values, 'b-', linewidth=2, label='الجاذبية')
    ax9.loglog(r_values, np.abs(F_e_values), 'r-', linewidth=2, label='الكهرباء')
    ax9.set_xlabel('المسافة r', fontsize=9)
    ax9.set_ylabel('القوة', fontsize=9)
    ax9.set_title('مقارنة القوتين\n(نفس الشكل الهندسي)', fontsize=10, fontweight='bold')
    ax9.legend(fontsize=8)
    ax9.grid(True, alpha=0.3)
    
    # ----- 10. مقارنة لبروتون وإلكترون -----
    ax10 = fig.add_subplot(4, 6, 10)
    ax10.axis('off')
    
    comparison_text = f"""
    ┌─────────────────────────────────────┐
    │   مقارنة لذرة الهيدروجين              │
    ├─────────────────────────────────────┤
    │                                     │
    │  المسافة: r = 5.29×10⁻¹¹ m          │
    │                                     │
    │  قوة الجاذبية:                       │
    │  F_g = {comparison['gravity']:.2e} N            │
    │                                     │
    │  القوة الكهربائية:                   │
    │  F_e = {comparison['electric']:.2e} N           │
    │                                     │
    │  النسبة F_e/F_g:                    │
    │  = {comparison['ratio']:.2e}                    │
    │                                     │
    │  ★ نفس الشكل الهندسي!                │
    │    الفرق فقط في ثابت الاستجابة        │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax10.text(0.05, 0.5, comparison_text, transform=ax10.transAxes,
              fontsize=8, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9),
              family='monospace')
    
    # ----- 11. تفسير ثوابت الاستجابة -----
    ax11 = fig.add_subplot(4, 6, 11)
    ax11.axis('off')
    
    constants_meaning = f"""
    ┌─────────────────────────────────────┐
    │   معنى الثوابت الهندسية الجديدة       │
    ├─────────────────────────────────────┤
    │                                     │
    │  G' = 4πG                           │
    │     = {const.G_prime:.3e} m³/kg/s²  │
    │                                     │
    │  k_e' = 1/ε₀                        │
    │       = {const.k_e_prime:.3e} F⁻¹·m │
    │                                     │
    │  ★ الثوابت هي "معاملات استجابة"       │
    │    بحر الفتائل للاضطرابات            │
    │                                     │
    │  ★ k_e'/G' ≈ 10³⁶                   │
    │    الوسط أكثر حساسية للشحنة           │
    │    من حساسيته للكتلة                 │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax11.text(0.05, 0.5, constants_meaning, transform=ax11.transAxes,
              fontsize=8, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.9),
              family='monospace')
    
    # ----- 12. تيار الامتصاص -----
    ax12 = fig.add_subplot(4, 6, 12)
    
    ax12.loglog(r_verify, a_verify, 'g-', linewidth=2)
    ax12.loglog(r_verify, const.G / r_verify**2, 'k--', alpha=0.5, label='1/r²')
    ax12.set_xlabel('المسافة r', fontsize=9)
    ax12.set_ylabel('التعجيل a', fontsize=9)
    ax12.set_title('التعجيل من تيار الامتصاص\nJ(r) = J₀/4πr²', fontsize=10, fontweight='bold')
    ax12.legend(fontsize=7)
    ax12.grid(True, alpha=0.3)
    
    # ----- 13. معادلات ماكسويل المادية -----
    ax13 = fig.add_subplot(4, 6, 13)
    ax13.axis('off')
    
    maxwell_eq = maxwell.display_equations()
    ax13.text(0.05, 0.5, maxwell_eq, transform=ax13.transAxes,
              fontsize=7, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='plum', alpha=0.9),
              family='monospace')
    
    # ----- 14. جدول التناظر -----
    ax14 = fig.add_subplot(4, 6, 14)
    ax14.axis('off')
    
    analogy = maxwell.analogy_table()
    ax14.text(0.05, 0.5, analogy, transform=ax14.transAxes,
              fontsize=7, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9),
              family='monospace')
    
    # ----- 15. سرعة الموجات الجاذبية -----
    ax15 = fig.add_subplot(4, 6, 15)
    
    # رسم مقارنة السرعات
    speeds = [const.c, c_g]
    labels = ['سرعة الضوء c', 'سرعة الموجة الجاذبية c_g']
    colors = ['gold', 'purple']
    
    bars = ax15.bar(labels, speeds, color=colors, alpha=0.7)
    ax15.set_ylabel('السرعة (m/s)', fontsize=9)
    ax15.set_title(f'سرعة الموجات الجاذبية\nc_g = c = {c_g:.2e} m/s', fontsize=10, fontweight='bold')
    ax15.tick_params(axis='x', rotation=15)
    
    for bar, val in zip(bars, speeds):
        ax15.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1e7,
                 f'{val:.2e}', ha='center', fontsize=8)
    
    # ----- 16. مساحة السطح الكروي (ثلاثي الأبعاد) -----
    ax16 = fig.add_subplot(4, 6, 16, projection='3d')
    
    # رسم كرة
    u = np.linspace(0, 2*np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    
    ax16.plot_surface(x, y, z, cmap='coolwarm', alpha=0.7)
    ax16.set_xlabel('X')
    ax16.set_ylabel('Y')
    ax16.set_zlabel('Z')
    ax16.set_title('مساحة السطح الكروي A = 4πr²\n(الأساس الهندسي لجميع القوى)', fontsize=10, fontweight='bold')
    
    # ----- 17. توزيع المساحة مع نصف القطر -----
    ax17 = fig.add_subplot(4, 6, 17)
    
    r_surface = np.linspace(0.1, 5, 100)
    A_surface = sphere_dist.surface_area(r_surface)
    
    ax17.plot(r_surface, A_surface, 'b-', linewidth=2)
    ax17.fill_between(r_surface, 0, A_surface, alpha=0.3)
    ax17.set_xlabel('نصف القطر r', fontsize=9)
    ax17.set_ylabel('مساحة السطح A(r)', fontsize=9)
    ax17.set_title('A(r) = 4πr²', fontsize=10, fontweight='bold')
    ax17.grid(True, alpha=0.3)
    
    # ----- 18. لماذا 4π؟ -----
    ax18 = fig.add_subplot(4, 6, 18)
    ax18.axis('off')
    
    why_4pi = """
    ┌─────────────────────────────────────┐
    │        لماذا 4π؟                     │
    ├─────────────────────────────────────┤
    │                                     │
    │  4π هو الثابت الهندسي الذي يربط       │
    │  نصف القطر بمساحة السطح الكروي.       │
    │                                     │
    │  • الدائرة: محيط = 2πr              │
    │  • الكرة: مساحة = 4πr²              │
    │  • الكرة: حجم = (4/3)πr³            │
    │                                     │
    │  ★ 4π يظهر لأن التأثير ينتشر          │
    │    في ثلاثة أبعاد مكانية              │
    │                                     │
    │  ★ في بعدين سيكون 2π                 │
    │    في n أبعاد سيكون (n-1)-sphere    │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax18.text(0.05, 0.5, why_4pi, transform=ax18.transAxes,
              fontsize=8, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.9),
              family='monospace')
    
    # ----- 19. الجسر مع الأجزاء السابقة -----
    ax19 = fig.add_subplot(4, 6, 19)
    ax19.axis('off')
    
    bridge = """
    ┌─────────────────────────────────────┐
    │   التوحيد الهندسي في سياق الفتائل      │
    ├─────────────────────────────────────┤
    │                                     │
    │  الفتيلة الأولية:                    │
    │  • كرة مجوفة (سطح كروي)              │
    │                                     │
    │  الجاذبية الفتيلية:                  │
    │  • تيار امتصاص يتوزع على سطح كروي     │
    │                                     │
    │  الدايود الكوني:                     │
    │  • الخاصية الاتجاهية على السطح        │
    │                                     │
    │  AC/DC:                             │
    │  • القوى AC و DC تشتركان في           │
    │    نفس الأساس الهندسي                │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax19.text(0.05, 0.5, bridge, transform=ax19.transAxes,
              fontsize=8, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
              family='monospace')
    
    # ----- 20. التنبؤات -----
    ax20 = fig.add_subplot(4, 6, 20)
    ax20.axis('off')
    
    predictions = f"""
    ┌─────────────────────────────────────┐
    │   تنبؤات التوحيد الهندسي              │
    ├─────────────────────────────────────┤
    │                                     │
    │  1. موجات جاذبية بسرعة c             │
    │     c_g = c = {c_g:.2e} m/s         │
    │                                     │
    │  2. تعديلات على قانون نيوتن           │
    │     على مسافات قصيرة جداً             │
    │     F = F₀ (1 + δ·l_P/r)           │
    │                                     │
    │  3. تغير الثوابت مع الكثافة           │
    │     G' و k_e' تعتمدان على ρ         │
    │                                     │
    │  4. تناظر كامل بين معادلات            │
    │     الكهرومغناطيسية والجاذبية         │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax20.text(0.05, 0.5, predictions, transform=ax20.transAxes,
              fontsize=8, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9),
              family='monospace')
    
    # ----- 21. إعادة كتابة الكتب -----
    ax21 = fig.add_subplot(4, 6, 21)
    ax21.axis('off')
    
    rewrite = """
    ┌─────────────────────────────────────┐
    │   إعادة كتابة قوانين الفيزياء          │
    ├─────────────────────────────────────┤
    │                                     │
    │  القديم:                             │
    │  F = G m₁ m₂ / r²                   │
    │  F = k_e q₁ q₂ / r²                 │
    │                                     │
    │  الجديد:                             │
    │  F = (G' / 4πr²) m₁ m₂              │
    │  F = (k_e' / 4πr²) q₁ q₂            │
    │                                     │
    │  ★ الصيغة الجديدة تكشف عن             │
    │    الأصل الهندسي المشترك              │
    │                                     │
    │  ★ الثوابت G' و k_e' هي               │
    │    معاملات استجابة الوسط              │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax21.text(0.05, 0.5, rewrite, transform=ax21.transAxes,
              fontsize=8, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9),
              family='monospace')
    
    # ----- 22. الخلاصة الفلسفية -----
    ax22 = fig.add_subplot(4, 6, 22)
    ax22.axis('off')
    
    philosophy = """
    ┌─────────────────────────────────────┐
    │       الخلاصة الفلسفية                │
    ├─────────────────────────────────────┤
    │                                     │
    │  "الهندسة ليست مجرد أداة رياضية،       │
    │   بل هي لغة الواقع نفسه."             │
    │                                     │
    │  • التشابه بين نيوتن وكولوم            │
    │    لم يكن صدفة أبداً                  │
    │                                     │
    │  • كلا القانونين ينبثق من               │
    │    مبدأ هندسي واحد                    │
    │                                     │
    │  • الطبيعة تستخدم السطح الكروي         │
    │    لتوزيع التأثيرات                   │
    │                                     │
    │  ★ r² مجرد اختصار رياضي               │
    │    الحقيقة هي 4πr²                   │
    │                                     │
    └─────────────────────────────────────┘
    """
    ax22.text(0.05, 0.5, philosophy, transform=ax22.transAxes,
              fontsize=9, verticalalignment='center',
              bbox=dict(boxstyle='round', facecolor='gold', alpha=0.8),
              family='monospace')
    
    # ----- 23. شعار النهاية -----
    ax23 = fig.add_subplot(4, 6, 23)
    ax23.axis('off')
    ax23.text(0.5, 0.5, '⚫ 4πr² ⚫\nالتوحيد الهندسي', fontsize=20, ha='center', va='center')
    
    # ----- 24. معلومات الإصدار -----
    ax24 = fig.add_subplot(4, 6, 24)
    ax24.axis('off')
    ax24.text(0.5, 0.5, 
              'نظرية الفتائل - التوحيد الهندسي\nBasel Yahya Abdullah\n2025',
              fontsize=10, ha='center', va='center',
              bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    plt.suptitle('نظرية الفتائل - الجزء التاسع: مختبر التوحيد الهندسي\nمن r² إلى 4πr²: الاكتشاف الهندسي الثوري',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_file = 'filament_geometric_unification.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"\n[✓] تم حفظ مختبر التوحيد الهندسي في: {output_file}")
    
    plt.show()
    
    return output_file


# ============================================================================
# التشغيل الرئيسي
# ============================================================================

if __name__ == "__main__":
    visualize_geometric_unification()
