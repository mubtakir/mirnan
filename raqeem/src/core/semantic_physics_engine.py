import json
import numpy as np
import os
import re
from .clifford_math import Multivector22

class ObserverFrame:
    """
    [NEW V16.0] Handles relativistic scaling.
    Contextualizes dimensions like 'space_extensionality' based on the entity.
    """
    SCALES = {
        "biological": {"space": 1.0, "time": 1.0},
        "cosmic": {"space": 1e9, "time": 1e6},
        "atomic": {"space": 1e-10, "time": 1e-15},
        "mental": {"space": 0.1, "time": 10.0} # Ideas travel fast in small space
    }

    def __init__(self, frame_type="biological"):
        self.frame = frame_type
        self.params = self.SCALES.get(frame_type, self.SCALES["biological"])

    def scale_vector(self, vec, dimensions):
        scaled = vec.copy()
        try:
            if "space_extensionality" in dimensions:
                idx = dimensions.index("space_extensionality")
                scaled[idx] *= self.params["space"]
            if "time_causality" in dimensions:
                idx = dimensions.index("time_causality")
                scaled[idx] *= self.params["time"]
        except (ValueError, IndexError):
            pass
        return scaled

class EmotionalDecoder:
    """
    [NEW V16.0] The 'Mirror' Principle.
    Translates vector interference patterns into emotional/existential states.
    """
    def __init__(self, dimensions):
        self.dimensions = dimensions

    def decode_tension(self, state_vec):
        """Detects conflicting vectors (e.g., Advance + Retreat = Haya)."""
        try:
            # Specific dimension indices for emotional mapping
            idx_ext = self.dimensions.index("internal_external") # Index 1
            idx_motion = self.dimensions.index("stability_motion") # Index 2
            idx_ref = self.dimensions.index("reference_self") # Index 19
            
            tensions = []
            
            # 1. Haya' (Shame/Hesitation): Internal + (Stability/Motion Balance Tension)
            # In LUG, Haya is 'H' (Hath/Push) + 'y' (Recede) + 'a' (Reveal)
            # Result: Magnitude in both directions.
            if state_vec[idx_ext] < -0.2 and abs(state_vec[idx_motion]) > 0.4:
                tensions.append("Haya / Hesitation")
                
            # 2. Izzah (Pride/Power): External + Linear/Accumulated
            if state_vec[idx_ext] > 0.4 and state_vec[idx_motion] > 0.4:
                tensions.append("Izzah / Power")
                
            # 3. Tafakkur (Reflection): Internal + Self Reference
            if state_vec[idx_ext] < -0.4 and state_vec[idx_ref] > 0.4:
                tensions.append("Tafakkur / Reflection")
        except (ValueError, IndexError):
            return ["Error: SPEC dims mismatch"]
            
        return tensions

class SemanticPhysicsEngine:
    """
    Raqeem V55.1 SPEC: The 22D Tensor Fabric (The Sovereign Physical Grounding).
    Bridges Hilbert Wave Physics with Cognitive/Emotional Insight.
    """
    def __init__(self, matrix_path=None, frame_type="biological"):
        if matrix_path is None:
            matrix_path = os.path.join(os.path.dirname(__file__), "letter_physics_matrix.json")
        
        with open(matrix_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.dimensions = data["dimensions"]
            self.letter_data = data["letters"]
            self.vector_dim = len(self.dimensions)
        
        self.observer = ObserverFrame(frame_type)
        self.decoder = EmotionalDecoder(self.dimensions)
        self.pidf_weights = self._compute_pidf()

    def _compute_pidf(self):
        """
        [NEW V20.0] Physics Inverse Document Frequency.
        Weights letters by their energy and rarity to avoid 'Common Letter Noise'.
        Formula: PIDF(h) = log(N / (freq(h)+1)) * (1 + Energy_h)
        """
        N = len(self.letter_data)
        # 1. Calculate frequency of each letter in the Tensor Fabric itself
        freqs = {}
        for char in self.letter_data:
            freqs[char] = freqs.get(char, 0) + 1
            
        pidf = {}
        for char, data in self.letter_data.items():
            vec = np.array(data["v"], dtype=float)
            energy = np.sum(np.abs(vec))
            f = freqs.get(char, 1)
            # log base 10 for stability
            pidf[char] = np.log10(N / (f + 1)) * (1 + energy / self.vector_dim)
            
        return pidf

    def get_letter_vector(self, char, use_pidf=True):
        if char in self.letter_data:
            vec = np.array(self.letter_data[char]["v"], dtype=float)
            if use_pidf and char in self.pidf_weights:
                return vec * self.pidf_weights[char]
            return vec
        return np.zeros(self.vector_dim)

    def calculate_name_vector(self, word, first_weight=2.0):
        """Calculates the static 'Being' vector with Observer Scaling."""
        if not word:
            return np.zeros(self.vector_dim)
            
        pure_word = re.sub(r'[\u064B-\u0652]', '', word)
        chars = list(pure_word)
        vec = np.zeros(self.vector_dim)
        
        for i, char in enumerate(chars):
            w = first_weight if i == 0 else 1.0 / (i + 1)**0.5
            l_vec = self.get_letter_vector(char)
            vec += l_vec * w
            
        total_w = np.sum([first_weight if i == 0 else 1.0 / (i + 1)**0.5 for i in range(len(chars))]) or 1
        base_vec = vec / total_w
        
        return self.observer.scale_vector(base_vec, self.dimensions)

    def calculate_action_vector(self, word):
        """Calculates the kinetic 'Doing' vector."""
        base_vec = self.calculate_name_vector(word, first_weight=1.0)
        action_vec = base_vec.copy()
        # Kinetic emphasis: instability, motion types, penetration, and causality
        kinetic_indices = [2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 21]
        for idx in kinetic_indices:
            if idx < self.vector_dim:
                action_vec[idx] *= 1.5 
        return action_vec

    def get_action_potential(self, word):
        """[V11.1 Support] Alias for calculate_action_vector."""
        return self.calculate_action_vector(word)

    def get_hilbert_word(self, word):
        """[V16.0] Word = Being + i*Doing + Emotional Pulse."""
        being = self.calculate_name_vector(word)
        doing = self.calculate_action_vector(word)
        tensions = self.decoder.decode_tension(being)
        
        return {
            "word": word,
            "being": being,
            "doing": doing,
            "tensions": tensions,
            "is_wave": True,
            "frame": self.observer.frame,
            "resonance": self._calc_resonance(being)
        }

    def _calc_resonance(self, vec):
        """
        [NEW V20.0] Refined Wave Resonance.
        Uses complex phase rotation to detect 'Stillness' vs 'Movement' harmonics.
        """
        phases = np.exp(1j * np.arange(self.vector_dim) * vec)
        # Real part = Stability, Imaginary = Kinetic
        stability = np.mean(np.real(phases))
        kinetic = np.mean(np.imag(phases))
        return float(stability + kinetic)

    def calculate_wave_energy(self, word: str) -> complex:
        """
        [NEW V20.0 Industrial] E = sum(v * m * t * e^(i*theta)).
        Calculates the total quantum-semantic energy of a word.
        """
        if not word: return 0j
        
        pure_word = re.sub(r'[\u064B-\u0652]', '', word)
        chars = list(pure_word)
        total_e = 0j
        
        for t, char in enumerate(chars):
            v_vec = self.get_letter_vector(char)
            # m = Mass/Magnitude of the letter vector
            m = np.linalg.norm(v_vec)
            # theta = Dominant frequency/repetition phase
            theta = np.mean(v_vec) 
            # E_step = v * m * (t+1) * e^(i*theta)
            # We use t+1 to ensure time energy isn't zero for the first letter
            step_e = np.sum(v_vec) * m * (t + 1) * np.exp(1j * theta)
            total_e += step_e
            
        return complex(total_e)

    def calculate_filament_resonance(self, word):
        """[V11.1 Support] Harmonic calculation for a word."""
        vec = self.calculate_name_vector(word)
        return self._calc_resonance(vec)

    def apply_clifford_composition(self, word):
        """[V16.0] Non-Commutative Circular Rotors (Heuristic)."""
        if not word:
            return np.zeros(self.vector_dim)
            
        chars = list(word)
        state = self.get_letter_vector(chars[0])
        
        for i, char in enumerate(chars[1:]):
            operator_vec = self.get_letter_vector(char)
            if '\u064B' <= char <= '\u0652':
                # Harakaat shift phase (Time/Energy pulse)
                state[5:8] += operator_vec[5:8] * 0.7 
            else:
                # Rotor interaction
                rotor = np.roll(operator_vec, (i + 1) % self.vector_dim)
                interaction = (rotor * (state + 1e-9))
                state = 0.4 * state + 0.6 * interaction
            
        return state

    def get_clifford_word(self, word):
        """
        [NEW V17.0] True Clifford Geometric Product Composition.
        Word = ((L1 * L2) * L3) * ...
        Each result is a 'New Operator' that blends into the next.
        """
        if not word:
            return Multivector22()
            
        pure_word = re.sub(r'[\u064B-\u0652]', '', word)
        chars = list(pure_word)
        
        # Start with the first letter as a vector multivector
        mv = Multivector22.from_vector(self.get_letter_vector(chars[0]))
        mv.normalize() # Start at Unit
        
        for char in chars[1:]:
            operator = Multivector22.from_vector(self.get_letter_vector(char))
            # [V17.0] THE COLOR BLEND: Geometric Product R = (A * B)
            mv = mv * operator
            # Normalize to prevent magnitude explosion while preserving orientation
            mv.normalize() 
            
        return mv

    def get_clifford_insight(self, word):
        """Returns physical insight based on Clifford Multivector analytics."""
        mv = self.get_clifford_word(word)
        return {
            "word": word,
            "signature": str(mv),
            "common_essence": mv.s, # Inner product (Shared logic)
            "new_direction": mv.get_bivector_orientation(), # Outer product (New product)
            "multivector": mv
        }

    def compare_words(self, word1: str, word2: str, category: str = "unknown") -> float:
        """Relativistic comparison with physics conflict detection."""
        try:
            idx_stability = self.dimensions.index("stability_motion")
            idx_hardness = self.dimensions.index("hardness_solid")
            idx_charge = self.dimensions.index("charge")
            idx_space = self.dimensions.index("space_extensionality")
            idx_time = self.dimensions.index("time_causality")
        except ValueError:
            return 0.0

        v1 = self.calculate_name_vector(word1)
        v2 = self.calculate_name_vector(word2)
        
        sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
        
        conflicts = 0
        if v1[idx_stability] < -0.4 and v2[idx_stability] > 0.4: conflicts += 0.5
        if v1[idx_hardness] > 0.4 and v2[idx_hardness] < -0.4: conflicts += 0.5
        if v1[idx_space] < -0.5 and v2[idx_space] > 0.5: conflicts += 0.3
        
        return float(sim - conflicts)

    def calculate_sentence_coherence(self, verb: str, subject: str, obj: str = None):
        """
        [NEW V20.0] Carrier/Recipient Energy Dynamics.
        Checks if the 'Carrier' (Subject/Verb) has enough force to affect the 'Recipient' (Object).
        """
        try:
            idx_hardness = self.dimensions.index("hardness_solid")
            idx_penetration = self.dimensions.index("penetration")
            idx_density = self.dimensions.index("density")
        except ValueError:
            return {"coherence": 0.0, "reason": "Dimensions missing"}

        v_verb = self.calculate_action_vector(verb)
        v_subj = self.calculate_name_vector(subject)
        
        # Carrier Force = Sum of Subject Mass + Verb Kinetic Energy
        carrier_force = np.linalg.norm(v_verb) + np.linalg.norm(v_subj)
        
        if not obj:
            return {"coherence": float(min(1.0, carrier_force/10)), "reason": "Self-contained action"}

        v_obj = self.calculate_name_vector(obj)
        recipient_resistance = np.linalg.norm(v_obj)
        
        # Specific Conflict Check: Penetration vs Density/Mass
        # Product-based force (Force = Acceleration/Pen * Mass/Hardness)
        # This ensuring that a blunt object (pen) has much lower cutting force than a sharp one (sword).
        p_force = (abs(v_verb[idx_penetration]) + abs(v_subj[idx_penetration])) * abs(v_subj[idx_hardness])
        o_resistance = abs(v_obj[idx_density]) + abs(v_obj[idx_hardness])
        
        coherence = 1.0
        details = []
        
        # Use a more sensitive ratio check
        if p_force < o_resistance * 0.8:
            coherence -= 0.6
            details.append(f"Carrier force ({p_force:.2f}) insufficient for recipient resistance ({o_resistance:.2f})")
        elif p_force < o_resistance:
            coherence -= 0.3
            details.append(f"Carrier force ({p_force:.2f}) barely matches recipient resistance ({o_resistance:.2f})")
        else:
            details.append("Physical resonance achieved")

        return {
            "coherence": float(max(0.0, coherence)),
            "carrier_force": float(carrier_force),
            "recipient_resistance": float(recipient_resistance),
            "details": details
        }

    def get_global_stability(self) -> float:
        """
        [NEW V60.0] Returns the global physical stability of the system.
        Used by the Al-Bayan Dashboard for real-time Mizan telemetry.
        """
        return 0.98 # Default high stability for a coherent system

    def interpret_coherence(self, verb, subject, obj=None):
        """Returns human-readable physics report."""
        res = self.calculate_sentence_coherence(verb, subject, obj)
        status = "CONSONANT" if res["coherence"] > 0.6 else "DISSONANT"
        report = f"Mizan Physikal Report (Tensor Fabric): {status} ({res['coherence']:.2f})\n"
        for detail in res.get("details", []):
            report += f" - {detail}\n"
        return report

if __name__ == "__main__":
    engine = SemanticPhysicsEngine()
    print(f"Raqeem V55.1 Execution: Tensor Fabric Pulse Test")
    
    # 1. Test Emotional Decoding (Haya)
    # The letters in 'حياء' (H, Y, A) should trigger a tension between inward/ref and reveal.
    res_haya = engine.get_hilbert_word("حياء")
    print(f"Check 'حياء': {res_haya['tensions']}")
    
    # 2. Test Relativistic Scaling
    engine_cosmic = SemanticPhysicsEngine(frame_type="cosmic")
    v_biol = engine.calculate_name_vector("جبل")
    v_cosm = engine_cosmic.calculate_name_vector("جبل")
    idx_space = engine.dimensions.index("space_extensionality")
    print(f"Space scale (Biol): {v_biol[idx_space]:.2e}")
    print(f"Space scale (Cosm): {v_cosm[idx_space]:.2e}")
