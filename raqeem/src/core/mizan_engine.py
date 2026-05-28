import math

class AlMizanEngine:
    def __init__(self):
        self.verdicts = {
            "CONSONANT_REALITY": "مستقر (حقيقة متوافقة)",
            "DISSONANT": "متنافر (تناقض/خداع)",
            "FLUCTUATING": "متذبذب (احتمالية خداع أو شك)"
        }

    def calculate_unified_score(self, physics_score, stability, strategic_alignment):
        # Weighted sum of physical harmony and semantic stability
        return (physics_score * 0.4) + (stability * 0.4) + (strategic_alignment * 0.2)

    def generate_mizan_report(self, data):
        p_score = data.get("physics_score", 0.0)
        stability = data.get("stability", 0.0)
        strategic = data.get("strategic_alignment", 1.0)
        
        unified_score = self.calculate_unified_score(p_score, stability, strategic)
        
        # Determine verdict based on unified_score and stability
        if unified_score >= 0.75 and stability > 0.8:
            verdict_key = "CONSONANT_REALITY"
        elif unified_score < 0.4 or stability < 0.5:
            verdict_key = "DISSONANT"
        else:
            verdict_key = "FLUCTUATING"
            
        truth_ratio = max(0.0, min(1.0, unified_score))
        deception_score = max(0.0, min(1.0, 1.0 - truth_ratio + (1.0 - stability) * 0.5))
        
        return {
            "unified_score": unified_score,
            "verdict": verdict_key,
            "truth_ratio": truth_ratio,
            "deception_score": deception_score,
            "equilibrium_state": self.verdicts[verdict_key]
        }
