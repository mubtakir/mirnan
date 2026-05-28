# Physical Intuition - الحدس الفيزيائي (Bayan Bayan)
# ======================================================
# The "Subconscious" layer that validates designs against physical reality.
# Connects Design Analysis -> Material Ontology -> PhysiCAL Engine.

class PhysicalIntuition:
    """
    الحدس الفيزيائي: يحول الكلمات إلى واقع فيزيائي
    """
    def __init__(self):
        self.simulation = None
        
        # Load Material Knowledge (Bayan)
        from physics_engine.materials.ontology import MaterialManager
        self.materials = MaterialManager()
        
        # Load Physics Kernel
        from physics_engine.simulation.kernel import BayanSimulationKernel
        self.simulation = BayanSimulationKernel()
        
        print("🧠 Physical Intuition Layer (Tier 4) Active")

    def simulate_design(self, analysis_dict):
        """
        Runs a micro-simulation based on design parameters.
        Returns: IntuitionReport (str)
        """
        # 1. Parse Analysis
        params = analysis_dict.get('parameters', {})
        shape = analysis_dict.get('shape', 'cube')
        mat_name = analysis_dict.get('material', 'steel') or 'steel'
        
        # 2. Extract Dimensions (Default to 1.0 if missing)
        # We need to normalize units. Analyst returns raw float, assuming meters/kg or we need conversion.
        # For this prototype, we assume SI (Meters).
        width = params.get('width', 1.0)
        height = params.get('height', 1.0)
        diameter = params.get('diameter', 1.0)
        
        # 3. Calculate Volume (Geometry Logic)
        volume = 0.0
        if shape == 'cube' or shape == 'base':
             volume = width * width * height # Simplification
        elif shape == 'cylinder' or shape == 'rod' or shape == 'shaft':
             radius = diameter / 2.0
             # Simple math
             volume = 3.14159 * (radius**2) * height
        else:
             # Default fallback volume
             volume = width * height * 0.1 
        
        # 4. Get Material Density
        density = self.materials.get_density(mat_name)
        
        # 5. Mass Calculation
        mass_val = density * volume
        
        # 6. Instantiate Physical Entity
        from physics_engine.core.dimensions import Kg, Vector3, Meter, Velocity
        from physics_engine.simulation.kernel import PhysicalEntity
        
        # Create Entity at height 10m to test free fall impact?
        # Or just static analysis for now?
        # "Intuition" often means "How heavy is this?"
        
        entity = PhysicalEntity(
            name="DesignedObject",
            mass=Kg(mass_val),
            position=Vector3(0.0, 10.0, 0.0), # 10m high
            velocity=Velocity(Vector3(0.0, 0.0, 0.0))
        )
        
        # 7. Generate Report
        report = []
        report.append(f"🔍 تحليل فيزيائي ({mat_name} - {shape}):")
        report.append(f"   - الحجم المقدر: {volume:.4f} m^3")
        report.append(f"   - الكتلة (الوزن): {mass_val:.2f} kg")
        
        # Heuristic Intuition Rules (Like a human engineer feeling the weight)
        if mass_val > 1000.0:
            report.append("⚠️ تنبيه بديهي: هذا التصميم ثقيل جداً! (>1 طن). تأكد من دعامات الرفع.")
        elif mass_val > 50.0:
            report.append("💡 ملاحظة: يحتاج إلى شخصين أو رافعة صغيرة للتحريك.")
        else:
            report.append("✅ الوزن محمول يدوياً.")
        
        # Energy Check (Potential Energy at 10m)
        pe = mass_val * 9.81 * 10
        report.append(f"   - الطاقة الكامنة (عند 10م): {pe:.2f} Joules")
        
        return "\n".join(report)

    def parse_text_physics(self, text):
        """
        Parses text for simple mass comparisons or collisions.
        Returns: Report string or None if no physics detected.
        """
        import re
        
        # 1. Detect Scenario: "Object1 Mass1 vs Object2 Mass2"
        # Regex for "X weight Y unit" in Arabic
        # (وزن|كتلة) (word) (number) (unit)
        # Simplified: Look for numbers followed by units
        
        units = {
            "طناً": 1000.0, "طن": 1000.0, "tons": 1000.0, "ton": 1000.0,
            "كيلوغرام": 1.0, "كيلو": 1.0, "كغ": 1.0, "kg": 1.0, "kgs": 1.0,
            "غرام": 0.001, "جم": 0.001, "gram": 0.001, "g": 0.001 
        }
        
        # Naive extractor: Find all (Number, Unit) pairs
        matches = []
        words = text.split()
        for i, w in enumerate(words):
            try:
                val = float(w)
                # Next word is unit?
                if i+1 < len(words):
                    u = words[i+1].lower()
                    # Clean punctuation
                    u = u.replace('.', '').replace(',', '')
                    if u in units:
                        matches.append((val, units[u], u)) # (Value, Multiplier, UnitName)
            except:
                pass
        
        if len(matches) >= 2:
            # We have a comparison!
            m1 = matches[0][0] * matches[0][1]
            m2 = matches[1][0] * matches[1][1]
            
            report = ["⚖️ تحليل التصادم الفيزيائي:"]
            report.append(f"   - الجسم الأول: {m1:.3f} kg")
            report.append(f"   - الجسم الثاني: {m2:.3f} kg")
            
            ratio = max(m1, m2) / (min(m1, m2) + 0.0001)
            
            if ratio > 1000:
                report.append(f"💥 نتيجة كارثية: الجسم الأكبر ({max(m1,m2)} كجم) سيسحق الأصغر تماماً!")
                report.append(f"   (نسبة الكتلة {ratio:.0f}:1 تشبه دهس شاحنة لنملة)")
            elif ratio > 10:
                report.append("⚠️ تصادم غير متكافئ: الجسم الأكبر سيزيح الأصغر بسهولة.")
            else:
                report.append("⚔️ تصادم متكافئ: الصراع سيعتمد على السرعة والمتانة.")
                
            return "\n".join(report)

        # 2. Detect Speed Paradox: "Slow beat Fast"?
        # Units: km/h, m/s
        speed_units = {
            "km/h": 1.0, "كيلومتر": 1.0, "كم/س": 1.0, "kph": 1.0,
            "m/s": 3.6, "متر/ثانية": 3.6, "mps": 3.6
        }
        
        
        speeds = []
        for i, w in enumerate(words):
            try:
                val = float(w)
                # Next few words for unit?
                # "كيلو" "متر" "في" "الساعة" -> 4 words!
                # Simple check: just look for 'val' and context words nearby
                neighborhood = " ".join(words[i+1:i+10]).lower() # Increase window
                if "ساعة" in neighborhood or "hour" in neighborhood or "km" in neighborhood or "كيلومتر" in neighborhood:
                     speeds.append(val)
            except:
                pass
        
        if len(speeds) >= 2:
            # Check for victory verbs
            victory_keywords = ["غلب", "فاز", "beat", "won", "faster", "أسرع", "سبق"]
            is_race = any(k in text.lower() for k in victory_keywords)
            
            if is_race:
                s1 = speeds[0]
                s2 = speeds[1]
                
                # Run A True Physics Simulation (Bayan Calculation)
                return self.run_race_simulation(s1, s2)
                
        return None

    def run_race_simulation(self, speed_a_kmh, speed_b_kmh):
        """
        Runs a time-stepped simulation using the Physical Core.
        Proves mathematically who wins.
        """
        from physics_engine.core.dimensions import Kg, Vector3, Velocity, Meter
        from physics_engine.simulation.kernel import PhysicalEntity
        
        # Convert to m/s
        v1_ms = speed_a_kmh / 3.6
        v2_ms = speed_b_kmh / 3.6
        
        # Create Entities
        car_a = PhysicalEntity("Car A", Kg(1000), Vector3(0,0,0), Velocity(Vector3(v1_ms, 0, 0)))
        car_b = PhysicalEntity("Car B", Kg(1000), Vector3(0,0,0), Velocity(Vector3(v2_ms, 0, 0)))
        
        # Simulation Parameters
        dt = 1.0 # 1 second steps
        duration = 60.0 # Simulate 1 minute race
        
        # Run Loop
        for t in range(int(duration)):
            # Update Position: P = P + V*dt (Euler integration from scratch for demo, or use kernel if available)
            # Since PhysicalEntity just stores state, we act as the kernel here.
            
            # Car A
            dist_a = car_a.velocity.value.x * dt
            car_a.position.x += dist_a
            
            # Car B
            dist_b = car_b.velocity.value.x * dt
            car_b.position.x += dist_b
            
        # Final Verification
        pos_a = car_a.position.x
        pos_b = car_b.position.x
        
        report = [f"🏁 محاكاة فيزيائية (لمدة {duration} ثانية):"]
        report.append(f"   - السيارة الأولى قطعت: {pos_a:.2f} متر")
        report.append(f"   - السيارة الثانية قطعت: {pos_b:.2f} متر")
        
        if pos_a > pos_b:
             report.append(f"✅ النتيجة: السيارة الأولى أسرع ({speed_a_kmh} > {speed_b_kmh}).")
        elif pos_b > pos_a:
             if speed_a_kmh > speed_b_kmh:
                 # This should technically be impossible if logic holds, unless we added drag?
                 pass 
             report.append(f"❌ النتيجة: السيارة الثانية أسرع ({speed_b_kmh} > {speed_a_kmh}).")
             report.append("   (لذلك قولك بأن الأولى غلبت الثانية هو مستحيل فيزيائياً!)")
        else:
             report.append("🤝 تعادل.")
             
        return "\n".join(report)
