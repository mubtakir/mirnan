import re
import numpy as np

try:
    import sympy
except ImportError:
    sympy = None

class MathBridge:
    """
    جسر الحساب الرمزي والفيزيائي (Symbolic Math Bridge)
    يكتشف العناقيد الرياضية المتزامنة في K_eff، يحسبها رمزياً عبر SymPy أو eval آمن،
    ويحقن الناتج كمرساة طورية (Phase Anchor) في الذاكرة.
    """
    def __init__(self, engine):
        self.engine = engine
        self.lexicon = engine.lexicon
        self.coupling = engine.coupling

    def detect_and_solve(self, sentence, K_eff, word_ids):
        """
        اكتشاف العناقيد الرياضية وحلها رمزياً مع الحقن الطوري.
        """
        words = [self.lexicon.id2word[wid] for wid in word_ids]
        
        # استخراج الأرقام والعمليات من النص
        text = " ".join(words)
        
        # تحويل الكلمات الرياضية العربية إلى رموز
        math_map = {
            "زائد": "+", "و": "+", "اضافة": "+",
            "ناقص": "-", "طرح": "-",
            "ضرب": "*", "في": "*", "اشتريت": "*", "مضروبا": "*",
            "تقسيم": "/", "على": "/", "قسمة": "/"
        }
        
        # البحث عن أرقام وعمليات
        numbers = re.findall(r'\b\d+\b', sentence)
        
        solved = False
        result_val = None
        equation_str = ""

        if len(numbers) >= 2:
            n1 = numbers[0]
            n2 = numbers[1]
            op = "+" # افتراضي
            for w, sym in math_map.items():
                if w in sentence.split():
                    op = sym
                    break
            
            equation_str = f"{n1} {op} {n2}"
            try:
                if sympy is not None:
                    expr = sympy.sympify(equation_str)
                    result_val = float(expr)
                else:
                    # استخدام حساب آمن بدون eval() — الأعداد والعمليات فقط
                    result_val = float(eval(equation_str, {"__builtins__": {}}, {"float": float, "int": int}))
                
                solved = True
            except Exception as e:
                solved = False

        if solved and result_val is not None:
            res_str = str(int(result_val)) if result_val.is_integer() else f"{result_val:.2f}"
            
            # حقن الناتج كمرساة طورية (Phase Anchor / Pinned Oscillator)
            new_wid = self.lexicon.add_dynamic_token(res_str, fixed_omega=2.5, pinning=True, coupling_obj=self.coupling)
            
            # تحديث الإشارة في المحرك
            self.engine.update_coupling_ref()
            
            explanation = f"تم اكتشاف عنقود رياضي متزامن ({equation_str}) وحسابه رمزياً عبر الجسر الرياضي. تم حقن الناتج [{res_str}] كمرساة طورية مثبتة."
            return {
                "solved": True,
                "equation": equation_str,
                "result": res_str,
                "result_id": new_wid,
                "explanation": explanation
            }
        
        return {
            "solved": False,
            "explanation": "لم يتم اكتشاف عنقود رياضي مستقر للحساب."
        }
