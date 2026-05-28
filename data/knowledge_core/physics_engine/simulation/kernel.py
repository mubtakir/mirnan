# RAW TRANSPILED FROM simulation_kernel.bayan - DO NOT EDIT
# Simulation Kernel - نواة المحاكاة (Bayan Bayan)
# ===================================================
# Orchestrates time-stepping and entity updates.

import time

class BayanSimulationKernel:
    """
    نواة المحاكاة السيادية - تدير الوقت والتطور الفيزيائي
    Manages physical evolution across discrete time steps.
    """
    def __init__(self, start_time=None):
        self.entities = []
        self.laws = []
        self.current_time = start_time if start_time else 0.0
        self.dt = None
        self.running = False
        
        # Initialize default laws
        from physics_engine.core.dimensions import ConservationOfEnergy
        self.laws.append(ConservationOfEnergy())


    def add_entity(self, entity):
        self.entities.append(entity)
        print(f"🌍 Added physical entity: {entity.name} (m0={entity.mass})")

    
    def calculate_system_energy(self):
        # Calculate Total Kinetic Energy + Potential Energy
        # K = (γ - 1)mc^2
        # U = -G*m1*m2/r (Gravitational Potential)
        total_energy = 0.0
        from physics_engine.core.dimensions import LorentzFactor, PhysicalConstants
        c = PhysicalConstants.c
        G = PhysicalConstants.G
        
        # 1. Kinetic Energy
        for ent in self.entities:
            if ent.is_dynamic:
                # Handle Vector Velocity
                v_mag = ent.velocity.magnitude() # Logic handles Scalar/Vector transparently
                
                m0 = ent.mass.value
                gamma = LorentzFactor(v_mag)
                if gamma == float('inf'):
                     k = float('inf')
                else:
                     k = (gamma - 1.0) * m0 * (c**2)

                total_energy += k


        
        # 2. Potential Energy (Gravity)
        n = len(self.entities)
        for i in range(n):
            for j in range(i + 1, n):
                ent1 = self.entities[i]
                ent2 = self.entities[j]
                
                # Position diff
                r_vec = ent2.position - ent1.position
                r = r_vec.magnitude()
                
                if r > 1e-9:
                    # U = - G * m1 * m2 / r
                    # Note: These are scalar math operations on values
                    u = - (G * ent1.mass.value * ent2.mass.value) / r
                    total_energy += u



        
        return total_energy


    def calculate_forces(self):
        """
        Recalculate all forces (N-Body Gravity)
        """
        from physics_engine.core.dimensions import PhysicalConstants, Force, Acceleration
        G = PhysicalConstants.G
        
        # Reset forces/accelerations
        for ent in self.entities:
            if ent.is_dynamic:
                # print(f"DEBUG_FORCE: {ent.name} is_vector={ent.position.is_vector}")
                if ent.position.is_vector:
                    from physics_engine.core.dimensions import Vector3
                    ent.acceleration.value = Vector3(0.0, 0.0, 0.0)
                else:
                    ent.acceleration.value = 0.0



        
        # Apply Gravity
        n = len(self.entities)
        for i in range(n):
            for j in range(i + 1, n):
                ent1 = self.entities[i]
                ent2 = self.entities[j]
                
                r_vec_pq = ent2.position - ent1.position # PQ(Vector)
                r_vec = r_vec_pq.value # Vector3
                r = r_vec.magnitude()
                
                if r > 1e-9:
                    # F = G * m1 * m2 / r^2
                    # F_vec = F * (r_vec / r) = (G * m1 * m2 / r^3) * r_vec
                    
                    scaler = (G * ent1.mass.value * ent2.mass.value) / (r**3)
                    f_vec_val = r_vec * scaler # Vector3
                    
                    # Apply to ent1 (towards ent2 -> positive direction of r_vec relative to 1?)
                    # r_vec = p2 - p1. Force on 1 is towards 2. So +F_vec.
                    # a1 = F1 / m1
                    a1_val = f_vec_val / ent1.mass.value
                    
                    # Force on 2 is opposite. -F_vec.
                    # a2 = -F2 / m2
                    a2_val = (f_vec_val * -1.0) / ent2.mass.value
                    
                    # Accumulate Accelerations
                    # We operate on .value directly to avoid creating excessive PQ objects in tight loop
                    # This implies 'ent.acceleration.value' is mutable if it's a Vector3? 
                    # No, Vector3 is immutable in our impl (returns new Vector3).
                    ent1.acceleration.value = ent1.acceleration.value + a1_val
                    ent2.acceleration.value = ent2.acceleration.value + a2_val





    def step(self):
        """
        Symplectic Integration Step (Velocity Verlet)
        Preserves energy for orbital mechanics.
        """
        from physics_engine.core.dimensions import Second, PhysicalConstants
        dt_phys = Second(self.dt)
        half_dt = Second(self.dt * 0.5)

        # 1. First Half-Kick (Update v by 0.5*a*dt)
        for ent in self.entities:
            if ent.is_dynamic:
                # DEBUG TYPE
                # print(f"DEBUG: {ent.name} AccType: {ent.acceleration.value}")
                
                # v(t + 0.5dt) = v(t) + 0.5 * a(t) * dt
                dv = ent.acceleration * half_dt
                ent.velocity = ent.velocity + dv



        # 2. Drift (Update x by v_half * dt)
        for ent in self.entities:
            if ent.is_dynamic:
                # x(t + dt) = x(t) + v(t + 0.5dt) * dt
                dx = ent.velocity * dt_phys
                ent.position = ent.position + dx


        
        # 3. Recalculate Forces/Accelerations a(t+dt) based on new x
        self.calculate_forces()

        # 4. Second Half-Kick (Update v by 0.5*a_new*dt)
        for ent in self.entities:
            if ent.is_dynamic:
                 # v(t + dt) = v(t + 0.5dt) + 0.5 * a(t+dt) * dt
                 dv = ent.acceleration * half_dt
                 ent.velocity = ent.velocity + dv
                 
                # Relativistic Clamp
                 c = PhysicalConstants.c
                 v_val = ent.velocity.value
                 
                 # Optimization: Check magnitude only if vector or direct compare if scalar
                 v_mag = 0.0
                 if hasattr(v_val, 'magnitude'):
                     v_mag = v_val.magnitude()
                 else:
                     v_mag = abs(v_val)


                 if v_mag >= c:
                     # print(f"⚠️ Speed Limit Reached for {ent.name}! Clamping to 0.99c")
                     if hasattr(v_val, 'magnitude'):
                         # Scale Vector
                         scale = (c * 0.9999) / v_mag
                         ent.velocity.value = v_val * scale
                     else:
                         ent.velocity.value = c * 0.9999




        
        self.current_time += self.dt
        
        # Law Enforcement
        current_E = self.calculate_system_energy()
        for law in self.laws:
            valid, msg = law.check(current_E)
            if not valid:
                print(f"🚨 LAW VIOLATION: {msg}")




    def run(self, steps=100):
        self.running = True
        print(f"🚀 Simulation started (Symplectic Verlet). DT={self.dt}s")
        
        # Initialize Forces/Accelerations for t=0
        self.calculate_forces()
        
        # Initial Energy Snapshot
        E_init = self.calculate_system_energy()
        self.laws[0].check(E_init)
        
        for i in range(steps):
            self.step()

        self.running = False
        print(f"🏁 Simulation complete. Total T={self.current_time}s")



class PhysicalEntity:
    def __init__(self, name, mass, position, velocity):
        self.name = name
        self.mass = mass 
        self.position = position 
        self.velocity = velocity 
        
        from physics_engine.core.dimensions import Acceleration, Radian, AngularVelocity, AngularAcceleration, Inertia
        self.acceleration = Acceleration(0.0)
        
        # Expert Physics Properties
        # Momentum p = mv (Derived, but we track state)
        # We assume 'mass' is invariant rest mass for now, handled by Relativistic utils elsewhere
        
        # Rotational
        self.angle = Radian(0)
        self.angular_velocity = AngularVelocity(0)
        self.angular_acceleration = AngularAcceleration(0.0) 
        self.inertia = Inertia(1.0) 
        
        self.is_dynamic = True


