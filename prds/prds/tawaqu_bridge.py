import sys
import os
import re

class TawaquBridge:
    """
    جسر التوقع الاستراتيجي ونظرية الألعاب (Tawaqu Strategic Foresight Bridge).
    يربط محرك PIDLM بمحركات التوقع الاستراتيجي في نظام Tawaqu V2.0 Supreme.
    """
    def __init__(self, engine):
        self.engine = engine
        self.tawaqu_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tawaqu'))
        if self.tawaqu_path not in sys.path:
            sys.path.insert(0, self.tawaqu_path)
            
        try:
            from backend.engines.enhanced_symbolic import get_enhanced_engine
            self.enhanced_engine = get_enhanced_engine()
            try:
                print("Tawaqu Enhanced Symbolic Engine activated successfully.")
            except:
                pass
        except Exception as e:
            try:
                print(f"Tawaqu init failed: {e}")
            except:
                pass
            self.enhanced_engine = None

    def detect_and_forecast(self, user_message):
        """
        فحص ما إذا كانت الرسالة تتطلب استبصاراً استراتيجياً أو تحليلاً للأزمات،
        وتوليد تقرير التوقع الاستراتيجي الشامل.
        """
        keywords = [
            "توقع", "سيناريو", "أزمة", "صراع", "استراتيجية", "مستقبل", 
            "تضخم", "حرب", "اقتصاد", "سياسة", "مفاوضات", "تهديد", "فرصة", "تحليل"
        ]
        if not any(w in user_message for w in keywords):
            return {"forecasted": False}

        if not self.enhanced_engine:
            return {"forecasted": False, "error": "Tawaqu engine not initialized"}

        try:
            analysis_text = self.enhanced_engine.reason(user_message, system="أنت خبير استراتيجي سيادي في نظام PIDLM.")
            
            return {
                "forecasted": True,
                "forecast_report": analysis_text,
                "summary": "تم تفعيل الاستبصار الاستراتيجي لمحاكاة أطوار الأزمة وتحديد السيناريوهات المحتملة."
            }
        except Exception as e:
            return {"forecasted": False, "error": str(e)}
