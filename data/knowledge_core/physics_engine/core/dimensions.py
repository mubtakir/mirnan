# RAW TRANSPILED FROM physical_core.bayan - DO NOT EDIT
# PhysiCAL Core - النواة الفيزيائية (Bayan Bayan) v1.2
# =================================================
# Fundamental Physical Types, Units, and Dimensions.

class Dimension:
    """
    تمثيل الأبعاد الفيزيائية السبعة الأساسية (SI)
    Represents the 7 base SI dimensions: [L, M, T, I, Θ, N, J]
    """
    def __init__(self, L=0, M=0, T=0, I=0, Theta=0, N=0, J=0):
        self.dims = [L, M, T, I, Theta, N, J]


    def __eq__(self, other):
        return self.dims == other.dims


    def multiply(self, other):
        new_dims = []
        for i in range(7):
            new_dims.append(self.dims[i] + other.dims[i])

        return Dimension(*new_dims)


    def divide(self, other):
        new_dims = []
        for i in range(7):
            new_dims.append(self.dims[i] - other.dims[i])

        return Dimension(*new_dims)


    def power(self, n):
        new_dims = []
        for i in range(7):
            new_dims.append(self.dims[i] * n)

        return Dimension(*new_dims)



# Base Dimensions
DIM_SCALAR = Dimension()
DIM_LENGTH = Dimension(L=1)
DIM_MASS   = Dimension(M=1)
DIM_TIME   = Dimension(T=1)
DIM_CURRENT = Dimension(I=1)
DIM_TEMP   = Dimension(Theta=1)


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5

    def __str__(self):
        return f"<{self.x:.2f}, {self.y:.2f}, {self.z:.2f}>"

    def __repr__(self):
        return self.__str__()



class PhysicalQuantity:
    """
    كمية فيزيائية: قيمة + وحدة (أبعاد)
    A value (Scalar or Vector) coupled with its physical dimensions and unit label.
    """
    def __init__(self, value, dimensions, unit_name="unit"):
        # Check if value is list/tuple -> convert to Vector3
        if isinstance(value, (list, tuple)):
             if len(value) == 3:
                 self.value = Vector3(float(value[0]), float(value[1]), float(value[2]))
             elif len(value) == 2:
                 self.value = Vector3(float(value[0]), float(value[1]), 0.0)
             else:
                 self.value = float(value[0])

        elif hasattr(value, 'x') and hasattr(value, 'magnitude'):
             self.value = value # It's already a Vector3
        else:
             self.value = float(value)

        
        self.dimensions = dimensions
        self.unit_name = unit_name

    
    @property
    def is_vector(self):
        return hasattr(self.value, 'magnitude')

    
    def magnitude(self):
        if self.is_vector:
            return self.value.magnitude()

        return abs(self.value)


    def __add__(self, other):
        if (isinstance(other, (int, float))):
            # Adding scalar to vector is undefined usually, but for tolerance check maybe?
            # Assuming strictly typed:
            if other == 0: return self
            raise ValueError(f"❌ Dimensional Mismatch: Cannot add scalar {other} to {self.unit_name}")

        if (self.dimensions != other.dimensions):
            raise ValueError(f"❌ Dimensional Mismatch: Cannot add {self.unit_name} and {other.unit_name}")

        return PhysicalQuantity(self.value + other.value, self.dimensions, self.unit_name)


    def __sub__(self, other):
        if (isinstance(other, (int, float))):
            if other == 0: return self
            raise ValueError(f"❌ Dimensional Mismatch: Cannot subtract scalar {other} from {self.unit_name}")

        if (self.dimensions != other.dimensions):
            raise ValueError(f"❌ Dimensional Mismatch: Cannot subtract {self.unit_name} and {other.unit_name}")

        return PhysicalQuantity(self.value - other.value, self.dimensions, self.unit_name)


    def __mul__(self, other):
        if (isinstance(other, (int, float))):
            return PhysicalQuantity(self.value * other, self.dimensions, self.unit_name)

        # PQ * PQ
        new_dims = self.dimensions.multiply(other.dimensions)
        val = 0
        
        if self.is_vector and other.is_vector:
             # Dot Product? Or component wise?
             # Usually Physics engines assume Dot Product for vectors, but wait...
             # v * t -> Vector * Scalar.
             # If other.value is scalar, it works via Vector.__mul__
             # If other.value is Vector, we assume Dot Product? 
             # Let's check implicit behavior of python objects. 
             # Vector3 does NOT have __mul__ for Vector.
             # So we must handle it. 
             pass

        
        # If one is vector and other is scalar (wrapped in PQ)
        if self.is_vector and not hasattr(other.value, 'magnitude'):
             val = self.value * other.value
        elif not self.is_vector and hasattr(other.value, 'magnitude'):
             val = self.value * other.value # Scalar * Vector = Vector (via Commutative)
             # Wait, float * Vector3 might fail if Vector3 doesnt have __rmul__
             val = other.value * self.value
        else:
             # Scalar * Scalar
             val = self.value * other.value

        
        return PhysicalQuantity(val, new_dims, f"({self.unit_name}*{other.unit_name})")


    def __truediv__(self, other):
        if (isinstance(other, (int, float))):
            return PhysicalQuantity(self.value / other, self.dimensions, self.unit_name)

        new_dims = self.dimensions.divide(other.dimensions)
        
        # Vector / Scalar
        if self.is_vector and not hasattr(other.value, 'magnitude'):
             val = self.value / other.value
             return PhysicalQuantity(val, new_dims, f"({self.unit_name}/{other.unit_name})")

        
        # Scalar / Scalar 
        if not self.is_vector and not hasattr(other.value, 'magnitude'):
             val = self.value / other.value
             return PhysicalQuantity(val, new_dims, f"({self.unit_name}/{other.unit_name})")

        
        raise ValueError("❌ Vector Division Undefined")


    def __str__(self):
        return f"{self.value} {self.unit_name}"


    def __repr__(self):
        return self.__str__()


    # Reflection Operators
    def __radd__(self, other):
        return self.__add__(other)


    def __rsub__(self, other):
        # other - self
        # Only supported if other is 0 (negation)
        if isinstance(other, (int, float)) and other == 0:
            # Negate vector or scalar
            return PhysicalQuantity(self.value * -1, self.dimensions, self.unit_name)

        raise ValueError(f"❌ Dimensional Mismatch: Cannot subtract {self.unit_name} from scalar") 


    def __rmul__(self, other):
        return self.__mul__(other)



# --- Helper Factory Functions ---
def Meter(v):
    return PhysicalQuantity(v, DIM_LENGTH, "m") 

def Kg(v):
    return PhysicalQuantity(v, DIM_MASS, "kg") 

def Second(v):
    return PhysicalQuantity(v, DIM_TIME, "s") 


# Derived Helpers
def Velocity(v):
    return PhysicalQuantity(v, DIM_LENGTH.divide(DIM_TIME), "m/s") 


def Force(v):
    # F = M * L / T^2
    dim_force = DIM_MASS.multiply(DIM_LENGTH).divide(DIM_TIME.power(2))
    return PhysicalQuantity(v, dim_force, "N")


def Acceleration(v):
    # a = L / T^2
    dim_accel = DIM_LENGTH.divide(DIM_TIME.power(2))
    return PhysicalQuantity(v, dim_accel, "m/s^2")


# --- Angular & Rotational Helpers ---
def Radian(v):
    return PhysicalQuantity(v, DIM_SCALAR, "rad")


def AngularVelocity(v):
    return PhysicalQuantity(v, DIM_SCALAR.divide(DIM_TIME), "rad/s")


def AngularAcceleration(v):
    # alpha = 1 / T^2
    dim_alpha = DIM_SCALAR.divide(DIM_TIME.power(2))
    return PhysicalQuantity(v, dim_alpha, "rad/s^2")


def Inertia(v):
    # I = M * L^2
    dim_inertia = DIM_MASS.multiply(DIM_LENGTH.power(2))
    return PhysicalQuantity(v, dim_inertia, "kg*m^2")


def Torque(v):
    # Tau = F * L = M * L^2 / T^2
    dim_torque = DIM_MASS.multiply(DIM_LENGTH.power(2)).divide(DIM_TIME.power(2))
    return PhysicalQuantity(v, dim_torque, "N*m")

# --- Physical Constants ---
class PhysicalConstants:
    c = 299792458.0 # Speed of Light (m/s)
    G = 6.67430e-11 # Gravitational Constant
    h = 6.62607015e-34 # Planck Constant


# --- Relativistic Mechanics ---
def LorentzFactor(v_magnitude):
    """Calculates γ (Gamma) = 1 / sqrt(1 - v^2/c^2)"""
    c = PhysicalConstants.c
    if v_magnitude >= c:
        return float('inf')

    return 1.0 / ((1.0 - (v_magnitude**2 / c**2))**0.5)


def RelativisticMass(rest_mass_val, velocity_magnitude):
    """m_rel = γ * m_0"""
    gamma = LorentzFactor(velocity_magnitude)
    return rest_mass_val * gamma


# --- Physical Laws System ---
class PhysicalLaw:
    """Base class for all physical laws acting as system constraints."""
    def __init__(self, name):
        self.name = name

    
    def check(self, system_state):
        """Returns (passed: bool, message: str)"""
        return True, "Law active"

    
    def enforce(self, system_state):
        """Optional: Correct the system state to obey the law."""
        pass



class ConservationOfEnergy(PhysicalLaw):
    def __init__(self, tolerance=1e-9):
        self.name = "Conservation of Energy"
        self.tolerance = tolerance
        self.initial_energy = None

    
    def check(self, current_energy):
        if self.initial_energy is None:
            self.initial_energy = current_energy
            return True, f"Initial Energy set to {current_energy}"

        
        diff = abs(current_energy - self.initial_energy)
        if diff > self.tolerance:
            return False, f"⚠️ Energy Violation! ΔE = {diff} (Tolerance: {self.tolerance})"

        return True, "Energy conserved"

# --- Physical Entity ---
# Moved from simulation_kernel for shared access (Tier 4 Integration)

class PhysicalEntity:
    def __init__(self, name, mass, position, velocity):
        self.name = name
        self.mass = mass 
        self.position = position 
        self.velocity = velocity 
        
        # Default zero acceleration
        self.acceleration = Acceleration(0.0)
        
        # Expert Physics Properties
        # Rotational state
        self.angle = Radian(0)
        self.angular_velocity = AngularVelocity(0)
        self.angular_acceleration = AngularAcceleration(0.0) 
        self.inertia = Inertia(1.0) 
        
        self.is_dynamic = True
