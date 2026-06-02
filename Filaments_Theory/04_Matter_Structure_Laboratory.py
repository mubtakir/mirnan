"""
نظرية الفتائل - الجزء الرابع: مختبر بنية المادة
Filament Theory - Part IV: Matter Structure Laboratory
================================================================
محاكاة تراكم الفتائل الأولية لتكوين الجسيمات المركبة

المبادئ:
1. التراكم غير المتراكز → أصل العزم المغزلي
2. قانون تصاغر نصف القطر: r_p = l_P / n
3. البروتون والإلكترون = تجليات الماهيات المتضادة
4. الشحنة = اختلال في المنسوب الفتيلي
5. قانون الاستقرار الكثافي
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# الثوابت الفتيلية لبنية المادة
# ============================================================================

class MatterStructureConstants:
    """ثوابت بنية المادة في نظرية الفتائل"""
    def __init__(self):
        self.hbar = 1.054571817e-34
        self.c = 299792458.0
        self.G = 6.67430e-11
        self.m_P = np.sqrt(self.hbar * self.c / self.G)
        self.l_P = np.sqrt(self.hbar * self.G / self.c**3)
        self.m_p = 1.67262192e-27
        self.m_e = 9.1093837e-31
        self.m_n = 1.67492749e-27
        self.r_p = 0.84e-15
        self.N_A = 6.02214076e23
        self.n_filaments_proton = self.m_p / self.m_P
        self.C_radius = self.r_p * self.n_filaments_proton
        
    def display(self):
        print("\n" + "="*70)
        print("ثوابت بنية المادة - نظرية الفتائل")
        print("="*70)
        print(f"كتلة الفتيلة:            {self.m_P:.4e} kg")
        print(f"طول الفتيلة:             {self.l_P:.4e} m")
        print(f"كتلة البروتون:           {self.m_p:.4e} kg")
        print(f"نصف قطر البروتون:        {self.r_p:.4e} m")
        print(f"عدد الفتائل في البروتون: {self.n_filaments_proton:.4e}")
        print(f"ثابت تصاغر نصف القطر:    {self.C_radius:.4e} m")
        print("="*70)

# ============================================================================
# نموذج التراكم غير المتراكز وأصل العزم المغزلي
# ============================================================================

class NonConcentricAccumulation:
    def __init__(self, n_filaments=100):
        self.n_filaments = n_filaments
        self.positions = self.generate_positions()
        self.velocities = self.calculate_velocities()
        self.angular_momentum = self.calculate_angular_momentum()
        self.spin = self.calculate_spin()
        
    def generate_positions(self):
        positions = [np.array([0.0, 0.0, 0.0])]
        layer_centers = [0.3 * i * np.random.randn(3) for i in range(1, 5)]
        for center in layer_centers:
            n_in_layer = self.n_filaments // len(layer_centers)
            for _ in range(n_in_layer):
                positions.append(center + 0.1 * np.random.randn(3))
        return np.array(positions)
    
    def calculate_velocities(self):
        velocities = []
        for pos in self.positions:
            r = np.linalg.norm(pos)
            if r > 1e-10:
                direction = np.cross(pos, np.array([0, 0, 1]))
                direction /= np.linalg.norm(direction)
                velocities.append(0.5 * r * direction)
            else:
                velocities.append(np.zeros(3))
        return np.array(velocities)
    
    def calculate_angular_momentum(self):
        L = np.zeros(3)
        for pos, vel in zip(self.positions, self.velocities):
            L += np.cross(pos, vel)
        return L
    
    def calculate_spin(self):
        L_mag = np.linalg.norm(self.angular_momentum)
        return 0.5 * (self.angular_momentum / L_mag) if L_mag > 0 else np.array([0.0,0.0,0.5])

# ============================================================================
# قانون تصاغر نصف القطر
# ============================================================================

class RadiusShrinkageLaw:
    def __init__(self, constants):
        self.const = constants
        
    def radius_from_filaments(self, n_filaments):
        return self.const.C_radius / n_filaments
    
    def verify_law(self):
        particles = {
            'proton': {'n': self.const.n_filaments_proton, 'r_exp': 0.84e-15},
            'deuteron': {'n': 2 * self.const.n_filaments_proton, 'r_exp': 2.1e-15},
            'helium-4': {'n': 4 * self.const.n_filaments_proton, 'r_exp': 1.7e-15},
        }
        results = []
        for name, data in particles.items():
            r_theory = self.radius_from_filaments(data['n'])
            results.append({'name': name, 'r_theory': r_theory, 'r_exp': data['r_exp']})
        return results
    
    def avogadro_connection(self):
        r_from_NA = self.const.l_P / self.const.N_A
        return {'r_from_NA': r_from_NA, 'r_exp': self.const.r_p, 'ratio': r_from_NA / self.const.r_p, 'N_A': self.const.N_A, 'l_P': self.const.l_P}

# ============================================================================
# تجليات الماهيات والمنسوب الفتيلي والاستقرار
# ============================================================================

class ProtonElectronDuality:
    def __init__(self, constants):
        self.const = constants
        
    def contractive_essence(self, n_filaments):
        radius = self.const.C_radius / n_filaments
        return {'mass': n_filaments * self.const.m_P, 'radius': radius}
    
    def expansive_essence(self, n_filaments=1):
        return {'mass': n_filaments * self.const.m_P, 'cloud_extent': self.const.C_radius}
    
    def tension_force(self, distance):
        return (8.99e9 * 1.6e-19**2 / distance**2) + (1e-3 * self.const.G * self.const.m_p * self.const.m_e / distance**2)

class FilamentLevelTheory:
    def __init__(self, constants):
        self.const = constants
        self.e = 1.602176634e-19
        self.alpha = self.e / (self.const.m_P / self.const.l_P**3)
        
    def charge_from_density(self, rho_local, rho_eq):
        return self.alpha * (rho_local - rho_eq)
    
    def charge_quantization(self):
        charges = np.arange(-3, 4) * self.e
        return charges, [f"Quantized {q/self.e}e" for q in charges]

class DensityStabilityLaw:
    def __init__(self, constants):
        self.const = constants
        self.rho_nucleus = 2.3e17
        self.rho_free_space = 1e-27
        
    def stability_condition(self, rho_internal, rho_env, tolerance=0.1):
        return abs(rho_internal / rho_env - 1.0) < tolerance, rho_internal / rho_env
    
    def neutron_stability(self):
        rho_neutron = self.rho_nucleus / 1.5
        stable_in, _ = self.stability_condition(rho_neutron, self.rho_nucleus)
        stable_out, _ = self.stability_condition(rho_neutron, self.rho_free_space)
        return {'in_nucleus': {'stable': stable_in}, 'in_free_space': {'stable': stable_out}, 'decay_energy_MeV': 0.782, 'lifetime_free': 879.4}
    
    def proton_stability(self):
        return {'stable_in_nucleus': True, 'stable_in_free_space': True, 'decay_energy_required_GeV': self.const.m_P * self.const.c**2 / 1.6e-10}
        
    def density_profile(self, r, rho_center, R_char):
        return rho_center * np.exp(-r / R_char)

# ============================================================================
# التصور الشامل לבنية المادة
# ============================================================================

def visualize_matter_structure():
    const = MatterStructureConstants()
    accum = NonConcentricAccumulation(n_filaments=200)
    radius_law = RadiusShrinkageLaw(const)
    duality = ProtonElectronDuality(const)
    level_theory = FilamentLevelTheory(const)
    stability = DensityStabilityLaw(const)
    
    fig = plt.figure(figsize=(28, 24))
    
    # 1. Non-concentric Accumulation (Spin)
    ax1 = fig.add_subplot(4, 5, 1, projection='3d')
    ax1.scatter(accum.positions[:, 0], accum.positions[:, 1], accum.positions[:, 2], c='blue', s=10, alpha=0.6)
    L_norm = accum.angular_momentum / np.linalg.norm(accum.angular_momentum) * 2
    ax1.quiver(0, 0, 0, L_norm[0], L_norm[1], L_norm[2], color='red', linewidth=3, label='العزم المغزلي')
    ax1.set_title('التراكم غير المتراكز\n(أصل العزم المغزلي)', fontweight='bold')
    ax1.legend()
    
    # 2. Radius Shrinkage Law
    ax2 = fig.add_subplot(4, 5, 2)
    n_vals = np.logspace(np.log10(const.n_filaments_proton/10), np.log10(const.n_filaments_proton*10), 100)
    ax2.loglog(n_vals, radius_law.radius_from_filaments(n_vals), 'b-', label='r = C/n')
    ax2.scatter([const.n_filaments_proton], [const.r_p], color='red', s=100, label='بروتون')
    ax2.set_title('قانون تصاغر نصف القطر\nr_p = C / n', fontweight='bold')
    ax2.legend()
    
    # 3. Proton & Electron
    ax3 = fig.add_subplot(4, 5, 3)
    ax3.add_patch(Circle((0.3, 0.5), 0.15, color='red', alpha=0.7))
    ax3.add_patch(Circle((0.7, 0.5), 0.25, color='blue', alpha=0.3))
    ax3.text(0.3, 0.2, "انطوائي\n(بروتون)", ha='center')
    ax3.text(0.7, 0.2, "اتساعي\n(إلكترون)", ha='center')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    ax3.set_title('تجليات الماهيات المتضادة', fontweight='bold')

    # Add remaining text placeholders for structure
    for i in list(range(4, 21)):
        ax = fig.add_subplot(4, 5, i)
        ax.axis('off')
        ax.text(0.5, 0.5, f"Panel {i}\n(Theory visual/text)", ha='center', va='center', bbox=dict(facecolor='lightcyan', alpha=0.5))

    plt.suptitle('نظرية الفتائل - الجزء الرابع: مختبر بنية المادة\nمن الفتيلة الأولية إلى الجسيمات المركبة', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    output_file = 'filament_matter_structure_laboratory.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"\n[✓] تم حفظ مختبر بنية المادة في: {output_file}")
    plt.show()
    return output_file

if __name__ == "__main__":
    visualize_matter_structure()
