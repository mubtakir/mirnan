# Physics Engine - المحرك الفيزيائي السيادي
# ==========================================
# Independent physics simulation and validation engine.
# Provides dimensional analysis, simulation, and physical intuition.

from physics_engine.core.dimensions import (
    Dimension, Vector3, PhysicalQuantity,
    Meter, Kg, Second, Velocity, Force, Acceleration,
    Radian, AngularVelocity
)
from physics_engine.simulation.kernel import BayanSimulationKernel, PhysicalEntity
from physics_engine.materials.ontology import MaterialManager
from physics_engine.intuition.validator import PhysicalIntuition

__all__ = [
    # Core Types
    'Dimension', 'Vector3', 'PhysicalQuantity',
    # Units
    'Meter', 'Kg', 'Second', 'Velocity', 'Force', 'Acceleration',
    'Radian', 'AngularVelocity',
    # Simulation
    'BayanSimulationKernel', 'PhysicalEntity',
    # Materials
    'MaterialManager',
    # Intuition
    'PhysicalIntuition'
]

__version__ = "1.0.0"
