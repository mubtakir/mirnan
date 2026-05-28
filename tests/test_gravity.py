import numpy as np
from src.physics.gravity import gravitational_force
from src.physics.constants import PHASE_DIM


class TestGravityForce:
    def test_same_vector_zero_force(self):
        v = np.ones(PHASE_DIM)
        f = gravitational_force(1.0, v, 1.0, v, 1.0)
        assert np.linalg.norm(f) == 0.0

    def test_force_direction_toward_heavier(self):
        v1 = np.zeros(PHASE_DIM)
        v2 = np.ones(PHASE_DIM)
        f = gravitational_force(1.0, v1, 10.0, v2, 1.0)
        assert np.dot(f, v2 - v1) > 0

    def test_force_scales_with_mass(self):
        v1 = np.zeros(PHASE_DIM)
        v2 = np.ones(PHASE_DIM)
        f1 = gravitational_force(1.0, v1, 1.0, v2, 1.0)
        f2 = gravitational_force(2.0, v1, 3.0, v2, 1.0)
        assert np.linalg.norm(f2) > np.linalg.norm(f1)

    def test_force_scales_with_distance(self):
        v1 = np.zeros(PHASE_DIM)
        v2 = np.ones(PHASE_DIM)
        f_near = gravitational_force(1.0, v1, 1.0, v2, 0.5)
        f_far = gravitational_force(1.0, v1, 1.0, v2, 5.0)
        assert np.linalg.norm(f_near) > np.linalg.norm(f_far)

    def test_output_shape(self):
        v1 = np.zeros(PHASE_DIM)
        v2 = np.ones(PHASE_DIM)
        f = gravitational_force(1.0, v1, 1.0, v2, 1.0)
        assert f.shape == (PHASE_DIM,)
