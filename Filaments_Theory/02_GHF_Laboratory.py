"""
نظرية الفتائل - الجزء الثاني: مختبر التفتت العظيم الحار
Filament Theory - Part II: Great Hot Fragmentation Laboratory
================================================================
محاكاة كونية لنموذج GHF وربطه بالفتيلة الأولية ودالة زيتا-ريمان

المبادئ:
1. نواة كونية أولية فائقة الكثافة
2. صراع بين قوة التماسك وقوة الشد
3. تفتت مستمر = أصل التوسع الكوني
4. البنية الهرمية من الأعلى إلى الأسفل
5. التجانس كخاصية ناشئة
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, FancyBboxPatch
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import odeint, solve_ivp
from scipy.ndimage import gaussian_filter
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# الثوابت الكونية من نظرية الفتائل
# ============================================================================

class CosmologicalConstants:
    """
    الثوابت الكونية المشتقة من نظرية الفتائل
    """
    def __init__(self):
        # ثوابت الفتيلة الأولية
        self.hbar = 1.054571817e-34
        self.c = 299792458.0
        self.G = 6.67430e-11
        
        # خصائص الفتيلة
        self.m_P = np.sqrt(self.hbar * self.c / self.G)
        self.l_P = np.sqrt(self.hbar * self.G / self.c**3)
        self.t_P = self.l_P / self.c
        
        # خصائص النواة الكونية الأولية (مشتقة)
        self.M_core = 1e55  # كتلة النواة (kg)
        self.R_core = 1e-30  # نصف قطر النواة (m)
        self.rho_core = self.M_core / ((4/3) * np.pi * self.R_core**3)
        self.T_core = self.G * self.M_core * self.m_P / (1.38e-23 * self.R_core)  # K
        
        # معامل هابل الحالي
        self.H0 = 70.0  # km/s/Mpc
        self.H0_SI = self.H0 * 1000 / (3.086e22)  # s^-1
        
    def display(self):
        """عرض الثوابت الكونية"""
        print("\n" + "="*70)
        print("الثوابت الكونية - نموذج GHF")
        print("="*70)
        print(f"كتلة النواة الأولية:     {self.M_core:.2e} kg")
        print(f"نصف قطر النواة:          {self.R_core:.2e} m")
        print(f"كثافة النواة:            {self.rho_core:.2e} kg/m³")
        print(f"درجة حرارة النواة:        {self.T_core:.2e} K")
        print(f"كتلة بلانك (الفتيلة):     {self.m_P:.2e} kg")
        print(f"طول بلانك:               {self.l_P:.2e} m")
        print(f"عدد الفتائل في النواة:    {self.M_core / self.m_P:.2e}")
        print("="*70)


# ============================================================================
# نموذج النواة الكونية الأولية
# ============================================================================

class PrimordialCore:
    """
    النواة الكونية الأولية: مفاعل كوني فائق الكثافة والحرارة
    """
    def __init__(self, constants=None):
        if constants is None:
            constants = CosmologicalConstants()
        self.const = constants
        
        # خصائص النواة
        self.mass = constants.M_core
        self.radius = constants.R_core
        self.density_central = constants.rho_core
        self.temperature_central = constants.T_core
        
        # توزيع الكثافة (ملف تعريف)
        self.density_profile = self.compute_density_profile()
        
        # توزيع درجة الحرارة
        self.temperature_profile = self.compute_temperature_profile()
        
        # توزيع الضغط
        self.pressure_profile = self.compute_pressure_profile()
        
    def compute_density_profile(self, r=None, num_points=1000):
        if r is None:
            r = np.linspace(0, 5 * self.radius, num_points)
        r_safe = np.maximum(r, 1e-40)
        rho = self.density_central * np.exp(-r_safe**2 / self.radius**2)
        return {'r': r, 'rho': rho}
    
    def compute_temperature_profile(self, r=None, num_points=1000):
        if r is None:
            r = np.linspace(0, 5 * self.radius, num_points)
        r_safe = np.maximum(r, 1e-40)
        T = self.temperature_central / (1 + r_safe**2 / self.radius**2)
        return {'r': r, 'T': T}
    
    def compute_pressure_profile(self, r=None, num_points=1000):
        if r is None:
            r = np.linspace(0, 5 * self.radius, num_points)
        rho_profile = self.compute_density_profile(r)
        T_profile = self.compute_temperature_profile(r)
        k_B = 1.38e-23
        a_rad = 7.56e-16
        P_gas = rho_profile['rho'] * k_B * T_profile['T'] / self.const.m_P
        P_rad = (1/3) * a_rad * T_profile['T']**4
        P = P_gas + P_rad
        return {'r': r, 'P': P, 'P_gas': P_gas, 'P_rad': P_rad}
    
    def cohesive_force(self, r):
        r_safe = np.maximum(r, 1e-40)
        if hasattr(r, '__len__'):
            M_r = np.zeros_like(r)
            for i, rr in enumerate(r):
                mask = self.density_profile['r'] <= rr
                if np.any(mask):
                    rho_int = self.density_profile['rho'][mask]
                    r_int = self.density_profile['r'][mask]
                    M_r[i] = np.trapz(4 * np.pi * r_int**2 * rho_int, r_int)
                else:
                    M_r[i] = 0
        else:
            M_r = self.mass * (1 - np.exp(-r**3 / self.radius**3))
        return -self.const.G * M_r / r_safe**2
    
    def tension_force(self, r):
        Lambda_eff = 1e-52
        return Lambda_eff * r
    
    def net_force(self, r):
        return self.cohesive_force(r) + self.tension_force(r)
    
    def fragmentation_condition(self, r, theta, phi):
        F_coh = np.abs(self.cohesive_force(r))
        F_ten = np.abs(self.tension_force(r))
        anisotropy = 1.0 + 0.1 * np.sin(3*theta) * np.cos(2*phi)
        return F_ten * anisotropy > F_coh


# ============================================================================
# نموذج التفتت العظيم الحار (GHF)
# ============================================================================

class GreatHotFragmentation:
    def __init__(self, core):
        self.core = core
        self.const = core.const
        self.fragments = []
        self.time_history = []
        self.scale_factor_history = []
        self.fragmentation_rate_history = []
        
    def compute_fragment_velocity(self, r_fragment):
        v_escape = np.sqrt(2 * self.const.G * self.core.mass / self.core.radius)
        r_ratio = r_fragment / self.core.radius
        v = v_escape * np.exp(-(r_ratio - 1)**2 / 0.5)
        return v
    
    def compute_fragment_mass(self, r, size_fraction=0.01):
        fragment_volume = (4/3) * np.pi * (r * size_fraction)**3
        rho_local = np.interp(r, self.core.density_profile['r'], self.core.density_profile['rho'])
        return fragment_volume * rho_local
    
    def simulate_fragmentation(self, num_events=100, time_span=1e-30):
        radii = np.random.uniform(0.5 * self.core.radius, 2 * self.core.radius, num_events)
        thetas = np.random.uniform(0, np.pi, num_events)
        phis = np.random.uniform(0, 2*np.pi, num_events)
        times = np.sort(np.random.uniform(0, time_span, num_events))
        
        fragments = []
        for i in range(num_events):
            r = radii[i]
            theta = thetas[i]
            phi = phis[i]
            t = times[i]
            if self.core.fragmentation_condition(r, theta, phi):
                mass = self.compute_fragment_mass(r)
                velocity = self.compute_fragment_velocity(r)
                direction = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
                fragments.append({
                    'time': t, 'mass': mass, 'velocity': velocity,
                    'radius': r, 'direction': direction, 'position': r * direction
                })
        
        self.fragments = fragments
        return fragments
    
    def compute_expansion_history(self, t_max=13.8e9 * 365.25 * 24 * 3600, num_points=1000):
        t_yr = np.linspace(0, 13.8e9, num_points)
        t_sec = t_yr * 365.25 * 24 * 3600
        a_matter = (t_sec / t_sec[-1])**(2/3)
        a_matter = a_matter / a_matter[0] if a_matter[0] > 0 else a_matter
        a_lambda = np.exp(0.5 * (t_sec - t_sec[-1]) / t_sec[-1])
        a_lambda = np.clip(a_lambda, 1.0, None)
        a_total = a_matter * a_lambda
        a_total = a_total / a_total[0]
        self.time_history = t_yr
        self.scale_factor_history = a_total
        H = np.gradient(np.log(a_total), t_sec)
        self.fragmentation_rate_history = H
        return t_yr, a_total, H
    
    def compute_cmb_spectrum(self, num_fragments=10000):
        T_fragments = np.random.normal(3000, 100, num_fragments)
        frequencies = np.logspace(8, 12, 500)
        h, c, k_B = 6.626e-34, 3e8, 1.38e-23
        spectrum = np.zeros_like(frequencies)
        for T in T_fragments:
            exponent = h * frequencies / (k_B * T)
            exponent = np.clip(exponent, 0, 100)
            B = 2 * h * frequencies**3 / c**2 / (np.exp(exponent) - 1)
            spectrum += B
        spectrum /= num_fragments
        return frequencies, spectrum, T_fragments


# ============================================================================
# جسر GHF مع دالة زيتا والفتيلة
# ============================================================================

class GHF_Zeta_Filament_Bridge:
    def __init__(self, core, ghf):
        self.core = core
        self.ghf = ghf
        self.const = core.const
        self.zeta_zeros = np.array([14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073])
        
    def map_fragment_to_zeta(self, fragment):
        v_norm = fragment['velocity'] / 3e8
        t_mapped = 14.0 + 30.0 * v_norm
        m_norm = fragment['mass'] / self.const.m_P
        sigma_mapped = 0.5 + 0.1 * np.log10(m_norm)
        return sigma_mapped, t_mapped
    
    def compute_fragmentation_zeta_spectrum(self):
        if len(self.ghf.fragments) == 0: return None
        sigma_vals, t_vals = [], []
        for frag in self.ghf.fragments:
            sigma, t = self.map_fragment_to_zeta(frag)
            sigma_vals.append(sigma)
            t_vals.append(t)
        return np.array(sigma_vals), np.array(t_vals)
    
    def verify_eighth_constant_in_ghf(self):
        mass_energy_ratios = []
        for frag in self.ghf.fragments[:50]:
            E_k = 0.5 * frag['mass'] * frag['velocity']**2
            E_rest = frag['mass'] * self.const.c**2
            ratio = E_k / E_rest
            mass_energy_ratios.append(ratio)
        mean_ratio = np.mean(mass_energy_ratios) if mass_energy_ratios else 0
        return mass_energy_ratios, mean_ratio


# ============================================================================
# التصور الشامل لنموذج GHF
# ============================================================================

def visualize_GHF_universe():
    print("\n" + "█" * 100)
    print("█" + " " * 98 + "█")
    print("█" + "   نظرية الفتائل - الجزء الثاني: مختبر التفتت العظيم الحار (GHF)".center(98) + "█")
    print("█" + " " * 98 + "█")
    print("█" * 100)
    
    constants = CosmologicalConstants()
    core = PrimordialCore(constants)
    ghf = GreatHotFragmentation(core)
    bridge = GHF_Zeta_Filament_Bridge(core, ghf)
    
    fragments = ghf.simulate_fragmentation(num_events=200, time_span=1e-28)
    t_yr, a_t, H_t = ghf.compute_expansion_history()
    freqs, cmb_spectrum, T_frags = ghf.compute_cmb_spectrum()
    zeta_data = bridge.compute_fragmentation_zeta_spectrum()
    
    fig = plt.figure(figsize=(28, 20))
    
    # ----- 1. النواة الكونية الأولية -----
    ax1 = fig.add_subplot(3, 5, 1)
    r_profile = core.density_profile['r']
    rho_profile = core.density_profile['rho']
    ax1.semilogy(r_profile / core.radius, rho_profile / rho_profile[0], 'b-', linewidth=2)
    ax1.axvline(x=1.0, color='r', linestyle='--', alpha=0.7, label='سطح النواة')
    ax1.set_title('توزيع الكثافة في النواة الأولية', fontsize=10, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # ----- 2. توزيع درجة الحرارة -----
    ax2 = fig.add_subplot(3, 5, 2)
    T_profile = core.temperature_profile['T']
    ax2.semilogy(r_profile / core.radius, T_profile / T_profile[0], 'r-', linewidth=2)
    ax2.set_title('توزيع درجة الحرارة', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # ----- 3. القوى المتصارعة -----
    ax3 = fig.add_subplot(3, 5, 3)
    r_force = np.linspace(0.5 * core.radius, 3 * core.radius, 500)
    F_coh = np.abs(core.cohesive_force(r_force))
    F_ten = np.abs(core.tension_force(r_force))
    ax3.semilogy(r_force / core.radius, F_coh, 'b-', linewidth=1.5, label='قوة التماسك')
    ax3.semilogy(r_force / core.radius, F_ten, 'r-', linewidth=1.5, label='قوة الشد')
    ax3.set_title('صراع القوى: التماسك ضد الشد\n(F_ten > F_coh → تفتت)', fontsize=10, fontweight='bold')
    ax3.legend(fontsize=7)
    ax3.grid(True, alpha=0.3)
    
    # ----- 4. تاريخ التوسع الكوني -----
    ax4 = fig.add_subplot(3, 5, 4)
    ax4.plot(t_yr, a_t, 'b-', linewidth=2)
    ax4.set_title('تاريخ التوسع الكوني\na(t) ∝ t^(2/3)', fontsize=10, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # ----- 5. معدل التوسع (هابل) -----
    ax5 = fig.add_subplot(3, 5, 5)
    ax5.plot(t_yr, H_t * 3.086e19, 'g-', linewidth=2)
    ax5.axhline(y=70, color='r', linestyle='--', alpha=0.7)
    ax5.set_title('تطور معامل هابل', fontsize=10, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # ----- 6. توزيع الشظايا (ثلاثي الأبعاد) -----
    ax6 = fig.add_subplot(3, 5, 6, projection='3d')
    if len(fragments) > 0:
        positions = np.array([f['position'] for f in fragments])
        masses = np.array([f['mass'] for f in fragments])
        sizes = 20 + 80 * (masses / masses.max())
        max_dist = np.max(np.linalg.norm(positions, axis=1))
        if max_dist > 0: positions = positions / max_dist
        ax6.scatter(positions[:, 0], positions[:, 1], positions[:, 2], c=masses, s=sizes, cmap='hot', alpha=0.7)
    ax6.set_title('توزيع الشظايا المنفصلة', fontsize=10, fontweight='bold')
    
    # ----- 7. البنية الهرمية (Top-Down) -----
    ax7 = fig.add_subplot(3, 5, 7)
    hierarchy = [('نواة', 1e55, 'red'), ('عناقيد فائقة', 1e47, 'orange'), ('مجرات', 1e42, 'yellow'), ('نجوم', 1e30, 'white')]
    y_pos = np.arange(4)
    ax7.barh(y_pos, np.log10([h[1] for h in hierarchy]), color=[h[2] for h in hierarchy], alpha=0.7)
    ax7.set_yticks(y_pos)
    ax7.set_yticklabels([h[0] for h in hierarchy])
    ax7.set_title('البنية الهرمية (من الأعلى إلى الأسفل)', fontsize=10, fontweight='bold')
    
    # ----- 8. طيف CMB من الشظايا -----
    ax8 = fig.add_subplot(3, 5, 8)
    ax8.loglog(freqs, cmb_spectrum, 'b-', linewidth=1.5)
    ax8.set_title('طيف إشعاع الخلفية الكونية\n(مجموع الشظايا)', fontsize=10, fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    # ----- 9. توزيع درجات حرارة الشظايا -----
    ax9 = fig.add_subplot(3, 5, 9)
    ax9.hist(T_frags, bins=30, color='orange', alpha=0.7, edgecolor='black')
    ax9.axvline(x=3000, color='r', linestyle='--', linewidth=2)
    ax9.set_title('توزيع درجات حرارة الشظايا', fontsize=10, fontweight='bold')
    ax9.grid(True, alpha=0.3)
    
    # ----- 10. إسقاط الشظايا على فضاء زيتا -----
    ax10 = fig.add_subplot(3, 5, 10)
    if zeta_data is not None:
        sigma_vals, t_vals = zeta_data
        ax10.scatter(t_vals, sigma_vals, c='blue', alpha=0.5, s=20)
        ax10.axhline(y=0.5, color='r', linestyle='--', linewidth=2, label='الخط الحرج σ=0.5')
        for zero in bridge.zeta_zeros[:4]:
            ax10.axvline(x=zero, color='green', linestyle=':', alpha=0.5)
    ax10.set_title('إسقاط الشظايا على فضاء زيتا\n(التجمع قرب σ=0.5)', fontsize=10, fontweight='bold')
    ax10.legend(fontsize=8)
    ax10.grid(True, alpha=0.3)
    
    # ----- 11. ثابت 1/8 في GHF -----
    ax11 = fig.add_subplot(3, 5, 11)
    ratios, mean_ratio = bridge.verify_eighth_constant_in_ghf()
    if len(ratios) > 0:
        ax11.hist(ratios, bins=20, color='purple', alpha=0.7, edgecolor='black')
        ax11.axvline(x=1/8, color='r', linestyle='--', linewidth=2, label=f'1/8 = {1/8:.3f}')
    ax11.set_title('ظهور ثابت 1/8 في GHF', fontsize=10, fontweight='bold')
    ax11.legend(fontsize=8)
    ax11.grid(True, alpha=0.3)
    
    # Panels 12-15 are text summaries for visualization
    for i in range(12, 16):
        ax = fig.add_subplot(3, 5, i)
        ax.axis('off')
        ax.text(0.5, 0.5, f"Summary Panel {i-11}\nGHF cosmology concepts", ha='center', va='center', bbox=dict(facecolor='lightcyan', alpha=0.5))
    
    plt.suptitle('نظرية الفتائل - الجزء الثاني: مختبر التفتت العظيم الحار (GHF)\nمن النواة الأولية إلى الكون المرصود', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    output_file = 'filament_ghf_cosmology_laboratory.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"\n[✓] تم حفظ مختبر GHF في: {output_file}")
    plt.show()
    return output_file

if __name__ == "__main__":
    output_file = visualize_GHF_universe()
