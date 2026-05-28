import numpy as np
from typing import Union, List

class Multivector22:
    """
    [NEW V17.0] Truncated Clifford Multivector for 22D SPEC Space.
    Supports Grades 0 (Scalar), 1 (Vector), and 2 (Bivector).
    Total components: 1 (S) + 22 (V) + 231 (B) = 254.
    """
    DIM = 22
    BIV_DIM = DIM * (DIM - 1) // 2

    def __init__(self, scalar=0.0, vector=None, bivector=None, pseudoscalar=0.0):
        self.s = float(scalar)
        self.v = np.array(vector, dtype=float) if vector is not None else np.zeros(self.DIM)
        self.b = np.array(bivector, dtype=float) if bivector is not None else np.zeros(self.BIV_DIM)
        self.p = float(pseudoscalar) # Grade 22

    @classmethod
    def from_vector(cls, v):
        return cls(vector=v)

    def norm(self):
        return np.sqrt(self.s**2 + np.sum(self.v**2) + np.sum(self.b**2))

    def normalize(self):
        n = self.norm()
        if n > 0:
            self.s /= n
            self.v /= n
            self.b /= n
            self.p /= n
        return self

    def dual(self):
        """Returns the Dual of the multivector (A * I^-1)"""
        # In 22D, I^-1 = -I
        return Multivector22(scalar=-self.p, vector=None, bivector=None, pseudoscalar=self.s)

    def __add__(self, other):
        return Multivector22(self.s + other.s, self.v + other.v, self.b + other.b)

    def __sub__(self, other):
        return Multivector22(self.s - other.s, self.v - other.v, self.b - other.b)

    def __mul__(self, other):
        """Geometric Product: A * B (Truncated SVB with Semantic Heritage)"""
        # 1. Scalar * Multivector / Multivector * Scalar
        res_s = self.s * other.s
        res_v = self.s * other.v + other.s * self.v
        res_b = self.s * other.b + other.s * self.b

        # 2. Vector * Vector = Dot + Wedge
        res_s += np.dot(self.v, other.v)
        res_b += self._wedge_vv(self.v, other.v)

        # 3. Vector * Bivector / Bivector * Vector interaction
        # [V31.4] PPU PHASE LOCKING: 
        # Increase bivector persistence to 0.7 if bivector norm is strong (Stable Phase).
        b_norm = np.linalg.norm(self.b)
        persistence = 0.7 if b_norm > 0.5 else 0.3
        
        heritage = self._contract_bv(self.b, other.v)
        res_v += heritage
        res_b += self.b * persistence # Persist prefix orientation (The Flow)
        
        # Converse
        res_v -= self._contract_bv(other.b, self.v)
        res_b += other.b * persistence

        return Multivector22(res_s, res_v, res_b, self.s * other.p + other.s * self.p)

    def _wedge_vv(self, v1, v2):
        """Outer product: v1 ^ v2 (231 components)"""
        b = np.zeros(self.BIV_DIM)
        k = 0
        for i in range(self.DIM):
            for j in range(i + 1, self.DIM):
                b[k] = v1[i] * v2[j] - v1[j] * v2[i]
                k += 1
        return b

    def _contract_bv(self, b, v):
        """Inner product: B . v (Contraction to Vector)"""
        res_v = np.zeros(self.DIM)
        k = 0
        for i in range(self.DIM):
            for j in range(i + 1, self.DIM):
                # B_ij (e_i ^ e_j) . e_m = delta_jm e_i - delta_im e_j
                val = b[k]
                res_v[i] -= val * v[j]
                res_v[j] += val * v[i]
                k += 1
        return res_v

    def get_scalar_essence(self):
        """Returns the 'Common Thread' magnitude (Scalar component)."""
        return self.s

    def get_bivector_orientation(self):
        """Returns the 'Interaction Plane' magnitude (Bivector component)."""
        return np.linalg.norm(self.b)

    def __repr__(self):
        return f"MV22(S:{self.s:.2f}, |V|:{np.linalg.norm(self.v):.2f}, |B|:{np.linalg.norm(self.b):.2f})"

# Helper to index bivectors if needed
def get_biv_indices(dim=22):
    indices = []
    for i in range(dim):
        for j in range(i + 1, dim):
            indices.append((i, j))
    return indices
