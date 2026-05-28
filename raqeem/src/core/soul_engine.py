class Affect:
    def __init__(self):
        self.peace = 1.0
        self.regret = 0.0

class SoulEngine:
    def __init__(self):
        self.affect = Affect()
        
    def record_moral_impact(self, harmony_delta, severity=1.0):
        # harmony_delta > 0 means positive impact, < 0 means dissonance
        if harmony_delta < 0:
            self.affect.regret += abs(harmony_delta) * severity
            self.affect.peace -= abs(harmony_delta) * 0.5 * severity
        else:
            self.affect.peace += harmony_delta * severity
            self.affect.regret -= harmony_delta * 0.5 * severity
            
        # Bound the values
        self.affect.peace = max(0.0, min(1.0, self.affect.peace))
        self.affect.regret = max(0.0, min(1.0, self.affect.regret))

    def run_recovery_tick(self):
        # Naturally drift towards peace
        self.affect.peace = min(1.0, self.affect.peace + 0.05)
        self.affect.regret = max(0.0, self.affect.regret - 0.05)

    def get_soul_state(self):
        peace = self.affect.peace
        regret = self.affect.regret
        
        if peace > 0.8 and regret < 0.2:
            field = "مستقر (متزن)"
        elif regret > 0.6:
            field = "مضطرب (ندم/توتر)"
        elif peace < 0.4:
            field = "منقبض (فقدان السلام)"
        else:
            field = "متغير (في طور التعافي)"
            
        return {
            "peace_index": peace,
            "regret_loops_active": regret > 0.5,
            "emotional_field": field
        }
