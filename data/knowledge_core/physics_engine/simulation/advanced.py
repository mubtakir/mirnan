# RAW TRANSPILED FROM physical_advanced.bayan - DO NOT EDIT
# قدرات فيزيائية متقدمة | Advanced Physics Capabilities
# ========================================================
# PhysiCAL Framework - Phase 26: Advanced Capabilities
# ديناميكا الموائع الأساسية وتحليل العناصر المحدودة

import math

# استيراد النواة الفيزيائية
try:
    from physical_core import PhysicalQuantity, Dimension, Vector3, Meter, Kg, Second
    from physical_core import PhysicalConstants, LorentzFactor
except ImportError:
    # تعريفات احتياطية
    class Vector3:
        def __init__(self, x=0, y=0, z=0):
            self.x, self.y, self.z = x, y, z

        def magnitude(self):
            return math.sqrt(self.x**2 + self.y**2 + self.z**2)

        def __add__(self, o):
            return Vector3(self.x + o.x, self.y + o.y, self.z + o.z)

        def __mul__(self, s):
            return Vector3(self.x * s, self.y * s, self.z * s)




# === ديناميكا الموائع (SPH أساسي) ===

class FluidParticle:
    """
    جسيم مائع - لمحاكاة SPH
    Smoothed Particle Hydrodynamics
    """
    
    def __init__(self, position, velocity=None, mass=1.0, density=1000.0):
        self.position = position  # Vector3
        self.velocity = velocity or Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        self.mass = mass
        self.density = density
        self.pressure = 0.0
        self.neighbors = []

    
    def update(self, dt):
        """تحديث الموقع والسرعة"""
        # v = v + a * dt
        self.velocity = self.velocity + self.acceleration * dt
        # x = x + v * dt
        self.position = self.position + self.velocity * dt



class SPHFluidSimulation:
    """
    محاكاة موائع SPH أساسية
    """
    
    # الثوابت الفيزيائية
    GAS_CONSTANT = 2000.0  # ثابت الغاز
    REST_DENSITY = 1000.0  # كثافة الراحة (kg/m³)
    VISCOSITY = 0.1        # اللزوجة
    GRAVITY = Vector3(0, -9.81, 0)
    
    def __init__(self, smoothing_radius=0.1):
        self.particles = []
        self.h = smoothing_radius  # نصف قطر التنعيم
        self.time = 0.0

    
    def add_particle(self, position, velocity=None):
        """إضافة جسيم"""
        p = FluidParticle(position, velocity)
        self.particles.append(p)
        return p

    
    def create_fluid_block(self, origin, dimensions, spacing):
        """إنشاء كتلة مائع"""
        particles = []
        x, y, z = origin.x, origin.y, origin.z
        dx, dy, dz = dimensions
        
        cx, cy, cz = x, y, z
        while cx < x + dx:
            cy = y
            while cy < y + dy:
                cz = z
                while cz < z + dz:
                    p = self.add_particle(Vector3(cx, cy, cz))
                    particles.append(p)
                    cz += spacing

                cy += spacing

            cx += spacing

        
        return particles

    
    # === دوال النواة (Kernel Functions) ===
    
    def W_poly6(self, r):
        """نواة Poly6 للكثافة"""
        if r >= self.h: { return 0 }
        coefficient = 315.0 / (64.0 * math.pi * self.h**9)
        return coefficient * (self.h**2 - r**2)**3

    
    def W_spiky_gradient(self, r, direction):
        """تدرج نواة Spiky للضغط"""
        if r >= self.h or r < 1e-6: { return Vector3(0, 0, 0) }
        coefficient = -45.0 / (math.pi * self.h**6)
        scale = coefficient * (self.h - r)**2 / r
        return direction * scale

    
    def W_viscosity_laplacian(self, r):
        """لابلاسيان نواة اللزوجة"""
        if r >= self.h: { return 0 }
        coefficient = 45.0 / (math.pi * self.h**6)
        return coefficient * (self.h - r)

    
    # === حسابات الديناميكا ===
    
    def compute_density_pressure(self):
        """حساب الكثافة والضغط لكل جسيم"""
        for pi in self.particles:
            pi.density = 0.0
            
            for pj in self.particles:
                dx = pi.position.x - pj.position.x
                dy = pi.position.y - pj.position.y
                dz = pi.position.z - pj.position.z
                r = math.sqrt(dx**2 + dy**2 + dz**2)
                
                pi.density += pj.mass * self.W_poly6(r)

            
            # معادلة حالة الغاز
            pi.pressure = self.GAS_CONSTANT * (pi.density - self.REST_DENSITY)


    
    def compute_forces(self):
        """حساب القوى (الضغط، اللزوجة، الجاذبية)"""
        for pi in self.particles:
            pressure_force = Vector3(0, 0, 0)
            viscosity_force = Vector3(0, 0, 0)
            
            for pj in self.particles:
                if pi == pj: { continue }
                
                dx = pi.position.x - pj.position.x
                dy = pi.position.y - pj.position.y
                dz = pi.position.z - pj.position.z
                r = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if r < self.h and r > 1e-6:
                    # اتجاه الوحدة
                    direction = Vector3(dx/r, dy/r, dz/r)
                    
                    # قوة الضغط
                    pressure_term = (pi.pressure + pj.pressure) / (2.0 * pj.density)
                    grad = self.W_spiky_gradient(r, direction)
                    pressure_force = pressure_force + grad * (-pj.mass * pressure_term)
                    
                    # قوة اللزوجة
                    vel_diff = Vector3(
                        pj.velocity.x - pi.velocity.x,
                        pj.velocity.y - pi.velocity.y,
                        pj.velocity.z - pi.velocity.z
                    )
                    visc_term = pj.mass * self.W_viscosity_laplacian(r) / pj.density
                    viscosity_force = viscosity_force + vel_diff * (self.VISCOSITY * visc_term)


            
            # التسارع الكلي
            if pi.density > 0:
                pi.acceleration = Vector3(
                    (pressure_force.x + viscosity_force.x) / pi.density + self.GRAVITY.x,
                    (pressure_force.y + viscosity_force.y) / pi.density + self.GRAVITY.y,
                    (pressure_force.z + viscosity_force.z) / pi.density + self.GRAVITY.z
                )



    
    def step(self, dt=0.001):
        """خطوة محاكاة واحدة"""
        self.compute_density_pressure()
        self.compute_forces()
        
        for p in self.particles:
            p.update(dt)

        
        self.time += dt

    
    def get_state(self):
        """الحصول على حالة المحاكاة"""
        return {
            "time": self.time,
            "particle_count": len(self.particles),
            "particles": [
                {
                    "position": [p.position.x, p.position.y, p.position.z],
                    "velocity": [p.velocity.x, p.velocity.y, p.velocity.z],
                    "density": p.density,
                    "pressure": p.pressure
                }
                for p in self.particles
            ]
        }



# === تحليل العناصر المحدودة (FEA أساسي) ===

class Node:
    """عقدة في شبكة العناصر المحدودة"""
    def __init__(self, id, x, y, z=0):
        self.id = id
        self.x, self.y, self.z = x, y, z
        self.displacement = Vector3(0, 0, 0)
        self.force = Vector3(0, 0, 0)
        self.fixed = [False, False, False]  # قيود x, y, z

    
    def fix(self, x=True, y=True, z=True):
        """تثبيت العقدة"""
        self.fixed = [x, y, z]

    
    def apply_force(self, fx, fy, fz=0):
        """تطبيق قوة"""
        self.force = Vector3(fx, fy, fz)



class TrussElement:
    """عنصر جمالون (1D)"""
    def __init__(self, id, node1, node2, E, A):
        """
        E: معامل المرونة (Pa)
        A: مساحة المقطع (m²)
        """
        self.id = id
        self.node1 = node1
        self.node2 = node2
        self.E = E  # معامل يونغ
        self.A = A  # المساحة
        
        # حساب الطول والاتجاه
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        dz = node2.z - node1.z
        self.L = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # جيوب التمام الاتجاهية
        self.cx = dx / self.L
        self.cy = dy / self.L
        self.cz = dz / self.L

    
    def stiffness_matrix_local(self):
        """مصفوفة الصلابة المحلية"""
        k = self.E * self.A / self.L
        return [
            [k, -k],
            [-k, k]
        ]

    
    def stiffness_matrix_global(self):
        """مصفوفة الصلابة العامة (6x6)"""
        k = self.E * self.A / self.L
        c, s = self.cx, self.cy
        
        # تحويل للإحداثيات العامة (2D مبسط)
        return [
            [k*c*c, k*c*s, -k*c*c, -k*c*s],
            [k*c*s, k*s*s, -k*c*s, -k*s*s],
            [-k*c*c, -k*c*s, k*c*c, k*c*s],
            [-k*c*s, -k*s*s, k*c*s, k*s*s]
        ]

    
    def get_stress(self):
        """حساب الإجهاد في العنصر"""
        # إزاحة محورية
        du = (
            (self.node2.displacement.x - self.node1.displacement.x) * self.cx +
            (self.node2.displacement.y - self.node1.displacement.y) * self.cy
        )
        
        # الانفعال
        strain = du / self.L
        
        # الإجهاد (σ = E * ε)
        stress = self.E * strain
        
        return stress



class FEASolver:
    """
    محلل العناصر المحدودة
    يدعم الجمالونات ثنائية الأبعاد
    """
    
    def __init__(self):
        self.nodes = {}
        self.elements = []

    
    def add_node(self, id, x, y, z=0):
        """إضافة عقدة"""
        node = Node(id, x, y, z)
        self.nodes[id] = node
        return node

    
    def add_truss(self, id, node1_id, node2_id, E, A):
        """إضافة عنصر جمالون"""
        element = TrussElement(
            id,
            self.nodes[node1_id],
            self.nodes[node2_id],
            E, A
        )
        self.elements.append(element)
        return element

    
    def solve(self):
        """
        حل المسألة
        يستخدم طريقة الصلابة المباشرة
        """
        n_nodes = len(self.nodes)
        n_dof = n_nodes * 2  # درجتي حرية لكل عقدة (x, y)
        
        # مصفوفة الصلابة الكلية
        K = [[0.0] * n_dof for _ in range(n_dof)]
        
        # تجميع المصفوفة
        for elem in self.elements:
            ke = elem.stiffness_matrix_global()
            
            # مؤشرات العقد
            i1 = (elem.node1.id - 1) * 2
            i2 = (elem.node2.id - 1) * 2
            indices = [i1, i1+1, i2, i2+1]
            
            for i, gi in enumerate(indices):
                for j, gj in enumerate(indices):
                    K[gi][gj] += ke[i][j]



        
        # متجه القوى
        F = [0.0] * n_dof
        for node in self.nodes.values():
            i = (node.id - 1) * 2
            F[i] = node.force.x
            F[i+1] = node.force.y

        
        # تطبيق شروط الحدود (elimination method)
        for node in self.nodes.values():
            i = (node.id - 1) * 2
            if node.fixed[0]:
                for j in range(n_dof): { K[i][j] = 0; K[j][i] = 0 }
                K[i][i] = 1
                F[i] = 0

            if node.fixed[1]:
                for j in range(n_dof): { K[i+1][j] = 0; K[j][i+1] = 0 }
                K[i+1][i+1] = 1
                F[i+1] = 0


        
        # حل النظام الخطي (Gauss elimination بسيط)
        U = self._solve_linear_system(K, F)
        
        # تحديث الإزاحات
        for node in self.nodes.values():
            i = (node.id - 1) * 2
            node.displacement = Vector3(U[i], U[i+1], 0)

        
        return U

    
    def _solve_linear_system(self, A, b):
        """حل نظام خطي بطريقة Gauss"""
        n = len(b)
        
        # نسخ
        A = [row[:] for row in A]
        b = b[:]
        
        # Elimination
        for i in range(n):
            # Pivot
            max_row = i
            for k in range(i+1, n):
                if abs(A[k][i]) > abs(A[max_row][i]):
                    max_row = k


            A[i], A[max_row] = A[max_row], A[i]
            b[i], b[max_row] = b[max_row], b[i]
            
            if abs(A[i][i]) < 1e-10: { continue }
            
            for k in range(i+1, n):
                factor = A[k][i] / A[i][i]
                for j in range(i, n):
                    A[k][j] -= factor * A[i][j]

                b[k] -= factor * b[i]


        
        # Back substitution
        x = [0.0] * n
        for i in range(n-1, -1, -1):
            if abs(A[i][i]) > 1e-10:
                x[i] = b[i]
                for j in range(i+1, n):
                    x[i] -= A[i][j] * x[j]

                x[i] /= A[i][i]


        
        return x

    
    def get_results(self):
        """الحصول على النتائج"""
        results = {
            "nodes": [],
            "elements": []
        }
        
        for node in self.nodes.values():
            results["nodes"].append({
                "id": node.id,
                "displacement": [node.displacement.x, node.displacement.y],
                "force": [node.force.x, node.force.y]
            })

        
        for elem in self.elements:
            results["elements"].append({
                "id": elem.id,
                "stress": elem.get_stress(),
                "length": elem.L
            })

        
        return results



# === واجهة عربية ===

def محاكاة_موائع(نصف_قطر=0.1):
    """إنشاء محاكاة موائع"""
    return SPHFluidSimulation(نصف_قطر)


def تحليل_إنشائي():
    """إنشاء محلل إنشائي"""
    return FEASolver()


# === اختبار ===

if __name__ == "__main__":
    print("=" * 50)
    print("اختبار ديناميكا الموائع SPH")
    print("=" * 50)
    
    sim = محاكاة_موائع(0.1)
    # إضافة جسيمات
    for i in range(5):
        sim.add_particle(Vector3(i * 0.05, 1.0, 0))

    
    # تشغيل 10 خطوات
    for _ in range(10):
        sim.step(0.001)

    
    state = sim.get_state()
    print(f"الوقت: {state['time']:.4f}s")
    print(f"عدد الجسيمات: {state['particle_count']}")
    
    print("\n" + "=" * 50)
    print("اختبار تحليل العناصر المحدودة")
    print("=" * 50)
    
    fea = تحليل_إنشائي()
    
    # جمالون بسيط
    fea.add_node(1, 0, 0)
    fea.add_node(2, 1, 0)
    fea.add_node(3, 0.5, 0.866)
    
    E = 200e9  # فولاذ (Pa)
    A = 0.001  # 10 cm² (m²)
    
    fea.add_truss(1, 1, 2, E, A)
    fea.add_truss(2, 2, 3, E, A)
    fea.add_truss(3, 3, 1, E, A)
    
    # تثبيت العقدة 1
    fea.nodes[1].fix()
    # تثبيت أفقياً العقدة 2
    fea.nodes[2].fix(x=False, y=True)
    # تطبيق قوة على العقدة 3
    fea.nodes[3].apply_force(0, -10000)  # 10 kN للأسفل
    
    # الحل
    fea.solve()
    
    results = fea.get_results()
    print("\nنتائج الإزاحات:")
    for node in results["nodes"]:
        print(f"  عقدة {node['id']}: ({node['displacement'][0]:.6f}, {node['displacement'][1]:.6f}) m")

    print("\nإجهادات العناصر:")
    for elem in results["elements"]:
        print(f"  عنصر {elem['id']}: {elem['stress']/1e6:.2f} MPa")


