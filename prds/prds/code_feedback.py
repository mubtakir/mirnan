import ast
import numpy as np

class CodeFeedback:
    """
    حلقة التنافر التصحيحي للأكواد البرمجية (Code Feedback & Phase Repulsion)
    تستقبل الكود المولد، تفحصه عبر محلل AST، وتحول الأخطاء النحوية والمنطقية
    إلى موجات تنافر طوري تضرب المذبذبات المسببة للخطأ.
    """
    def __init__(self, engine):
        self.engine = engine
        self.lexicon = engine.lexicon
        self.coupling = engine.coupling

    def evaluate_and_repel(self, code_str, word_ids):
        """
        فحص الكود وتوليد التنافر الطوري عند وجود أخطاء.
        """
        success = False
        error_type = None
        error_msg = ""
        
        try:
            tree = ast.parse(code_str)
            # فحص المتغيرات غير المعرفة (Static NameError Analysis via AST)
            defined_names = {'print', 'range', 'len', 'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple', 'True', 'False', 'None'}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    defined_names.add(node.name)
                    for arg in node.args.args:
                        defined_names.add(arg.arg)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_names.add(target.id)
                elif isinstance(node, ast.For):
                    if isinstance(node.target, ast.Name):
                        defined_names.add(node.target.id)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        defined_names.add(alias.asname or alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        defined_names.add(alias.asname or alias.name)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    if node.id not in defined_names:
                        raise NameError(f"اسم المتغير '{node.id}' غير معرف في هذا النطاق.")
                        
            success = True
        except SyntaxError as e:
            success = False
            error_type = "SyntaxError"
            error_msg = str(e)
        except NameError as e:
            success = False
            error_type = "NameError"
            error_msg = str(e)
        except Exception as e:
            success = False
            error_type = type(e).__name__
            error_msg = str(e)

        if not success:
            # توليد موجة التنافر الطوري (Phase Repulsion Wave)
            eta_error = 2.0 if error_type == "SyntaxError" else 1.0
            
            n = len(word_ids)
            for i in range(n):
                w1 = word_ids[i]
                for j in range(n):
                    if i != j:
                        w2 = word_ids[j]
                        # تطبيق التنافر
                        self.coupling.K[w1, w2] -= eta_error
                        self.coupling.K[w1, w2] = np.clip(self.coupling.K[w1, w2], -self.coupling.max_weight, self.coupling.max_weight)
                        self.coupling.K[w2, w1] = self.coupling.K[w1, w2]
            
            # تحديث K2 في المحرك
            self.engine.update_coupling_ref()
            
            explanation = f"فشل فحص الكود بسبب [{error_type}: {error_msg}]. تم إطلاق موجة تنافر طوري تصحيحي بقوة {-eta_error} لإعادة التوزيع."
            return {
                "success": False,
                "error_type": error_type,
                "error_msg": error_msg,
                "explanation": explanation
            }
        
        # إذا نجح الكود، نكافئ المذبذبات بتعزيز التجاذب
        n = len(word_ids)
        for i in range(n):
            w1 = word_ids[i]
            for j in range(n):
                if i != j:
                    w2 = word_ids[j]
                    self.coupling.K[w1, w2] += 0.5
                    self.coupling.K[w1, w2] = np.clip(self.coupling.K[w1, w2], -self.coupling.max_weight, self.coupling.max_weight)
                    self.coupling.K[w2, w1] = self.coupling.K[w1, w2]
        
        self.engine.update_coupling_ref()
        
        return {
            "success": True,
            "explanation": "اجتاز الكود الفحص النحوي بنجاح. تم تعزيز التجاذب الطوري للمجموعة البرمجية."
        }
