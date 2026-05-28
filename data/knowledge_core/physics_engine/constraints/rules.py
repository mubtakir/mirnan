# RAW TRANSPILED FROM physical_constraints.bayan - DO NOT EDIT
# Physical Constraints System - نظام القيود الفيزيائية (Bayan Bayan)
# ===============================================================
# Defines interactions like Springs, Dampers, and Rigid Joints.

from bayan_core.physical_core import PhysicalQuantity, DIM_LENGTH, DIM_TIME, DIM_MASS

class SpringConstraint:
    """
    قيد الزنبرك - يطبق قانون هوك
    Spring Constraint representing Hooke's Law: F = -k * x
    """
    def __init__(self, k, rest_length):
        self.k = k # Stiffness (N/m)
        self.rest_length = rest_length # rest_length (m)
        self.damping = 0.5 # Damping coefficient


    def compute_force(self, p1, p2):
        """
        حساب القوة المؤثرة بين جسيمين
        Calculates the restorative force vector between two physical points.
        """
        # 1. Compute displacement vector
        r_vec = p2.position - p1.position
        dist = r_vec.value # Scalar magnitude (assuming PhysicalQuantity supports .value)
        
        # 2. Hooke's Law: Force magnitude
        displacement = dist - self.rest_length.value
        force_mag = -self.k.value * displacement
        
        # 3. Apply damping (Velocity relative)
        v_rel = (p2.velocity - p1.velocity).value
        force_mag -= self.damping * v_rel
        
        # 4. Convert back to Vector Force (Simplification: 1D or along r_vec)
        # For now, let's assume 1D or logic-based force application
        return force_mag



class RigidJoint:
    """
    وصلة صلبة - تحافظ على مسافة ثابتة
    Rigid Joint that enforces a fixed distance between two entities using constraints.
    """
    def __init__(self, target_distance):
        self.target_distance = target_distance


    def resolve(self, p1, p2):
        """
        تصحيح المواضع للحفاظ على القيد الصارم
        Position correction to maintain rigid constraint distance.
        """
        current_r = p2.position - p1.position
        error = current_r.value - self.target_distance.value
        
        if (abs(error) > 0.001):
            # Minimal correction logic (Simple shift)
            correction = error / 2.0
            p1.position.value += correction
            p2.position.value -= correction




class MagneticSnapConstraint:
    """
    قيد الانجذاب المغناطيسي - يسحب الأجزاء لمحاذاة دقيقة
    Magnetic Snap Constraint - pulls entities together when close.
    """
    def __init__(self, strength, threshold):
        self.strength = strength # Force per distance (N/m or similar)
        self.threshold = threshold # Distance threshold for snapping (m)


    def compute_snap_force(self, p1, p2):
        """حساب قوة السحب المغناطيسي بين نقطتين"""
        # Calculate distance
        r_vec = p2.position - p1.position
        dist = abs(r_vec.value)
        
        if (dist < self.threshold.value and dist > 0.0001):
            # Pull force: gets stronger as we get closer, then stabilizes
            # F = strength * (1 - dist/threshold)
            force_mag = self.strength.value * (1.0 - dist/self.threshold.value)
            # return magnitude; direction is handled by kernel
            return force_mag

        return 0.0



class KinematicGearConstraint:
    """
    قيد التروس الحركي - يربط سرعات الدوران
    Kinematic Gear Constraint - links angular velocities by ratio R.
    Omega2 = - (R1 / R2) * Omega1
    """
    def __init__(self, r1, r2):
        self.ratio = r1.value / r2.value


    def resolve(self, p1, p2):
        """ضبط السرعة الزاوية للحفاظ على علاقة التروس"""
        # Simplification: Force p2 to follow p1's rotation with ratio and inversion
        target_omega = - (self.ratio * p1.angular_velocity.value)
        
        # Apply correction (Instantaneous velocity constraint)
        p2.angular_velocity.value = target_omega
        
        # Update angle to maintain phase (Optional/Simplified)
        p2.angle.value = - (self.ratio * p1.angle.value)


