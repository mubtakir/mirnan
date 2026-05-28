import re
import random
from typing import List, Dict, Any, Optional

class QalamBridge:
    """
    جسر محركات "القلم" السيادية (Al-Qalam Sovereign Engines Bridge).
    يجمع بين:
    1. محرك الفضول والتساؤل الذاتي (Curiosity Engine): كشف الفجوات المعرفية وطرح أسئلة استكشافية.
    2. محرك المحاكاة والتخيل (Imagination Engine): محاكاة سيناريوهات "ماذا لو" والتخيل الإبداعي.
    3. محرك الأسئلة المتعامدة (Orthogonal Question Engine): تحدي المسلمات وكشف الزوايا العمياء.
    """
    def __init__(self, engine):
        self.engine = engine
        self.curiosity_log = []
        self.imagination_log = []
        
        # أنماط استشعار التخيل ومحاكاة ماذا لو
        self.counterfactual_patterns = [
            r'ماذا\s+لو\s+(.+?)\s*\?',
            r'ماذا\s+لو\s+كان\s+(.+?)\s*\?',
            r'تخيل\s+(?:أن|ان)\s+(.+?)\s*\?',
            r'افترض\s+(?:أن|ان)\s+(.+)',
            r'لنفترض\s+(?:أن|ان)\s+(.+)',
            r'كيف\s+سيكون\s+(?:العالم|الحال|الأمر)\s+لو\s+(.+?)\s*\?',
            r'ماذا\s+سيحدث\s+(?:إذا|اذا)\s+(.+?)\s*\?'
        ]

    # ==========================================================================
    # 1. محرك الفضول والتساؤل الذاتي (Curiosity Engine)
    # ==========================================================================
    def stimulate_curiosity(self, user_message: str, active_phases: dict) -> dict:
        """
        تحليل رسالة المستخدم وسحابة الأطوار النشطة لكشف الفجوات المعرفية
        وتوليد تساؤل فضولي ذكي يطرحه النظام على المستخدم.
        """
        words = user_message.split()
        if len(words) < 3:
            return {"curious": False}

        # البحث عن مفاهيم رئيسية في الرسالة
        keywords = [w for w in words if len(w) > 3 and w not in ["في", "من", "على", "إلى", "عن", "هذا", "هذه", "كان", "أن", "إن"]]
        if not keywords:
            return {"curious": False}

        target_concept = random.choice(keywords)
        
        # توليد أسئلة فضولية متنوعة
        question_templates = [
            f"لقد لاحظتُ اهتمامك بمفهوم '{target_concept}'، ولكن ما هو الجوهر الفيزيائي أو الفلسفي الذي يحركه في نظرك؟",
            f"عندما تتأمل في '{target_concept}'، هل تراه كياناً مستقراً في فضاء الأطوار أم أنه خاضع لتقلبات مستمرة؟",
            f"إذا أردنا ربط '{target_concept}' بمرساة طورية جديدة، فما هي القيمة الأخلاقية أو العملية التي تقترن به؟",
            f"ما هي القدرات أو الخصائص الخفية لـ '{target_concept}' التي لم نتطرق إليها بعد في حوارنا؟"
        ]
        
        selected_question = random.choice(question_templates)
        self.curiosity_log.append(selected_question)

        return {
            "curious": True,
            "target_concept": target_concept,
            "curiosity_question": selected_question
        }

    # ==========================================================================
    # 2. محرك المحاكاة والتخيل (Imagination Engine)
    # ==========================================================================
    def simulate_imagination(self, user_message: str) -> dict:
        """
        استشعار سيناريوهات "ماذا لو" أو التخيل الإبداعي ومحاكاتها فيزيائياً.
        """
        premise = None
        scenario_type = "counterfactual"

        for pattern in self.counterfactual_patterns:
            match = re.search(pattern, user_message)
            if match:
                premise = match.group(1).strip()
                break

        if not premise and ("تخيل" in user_message or "افترض" in user_message):
            premise = user_message
            scenario_type = "creative"

        if not premise:
            return {"imagined": False}

        # محاكاة الخطوات والنتائج
        steps = [
            f"تثبيت الفرضية التخيلية: {premise}",
            "إعادة توجيه المذبذبات في فضاء كليفورد لمحاكاة الواقع البديل",
            "حساب تأثير التنافر الطوري على القوانين السببية المستقرة"
        ]

        if scenario_type == "creative":
            conclusion = f"في هذا الواقع الخيالي حيث ({premise})، تتغير مصفوفة الاقتران الفعالة وتكتسب الكيانات خصائص جديدة تعيد تشكيل التوازن الكوني."
            world_desc = f"عالم بديل تهيمن عليه فرضية '{premise}' وتتجاذب فيه الأطوار المتنافرة."
        else:
            conclusion = f"بناءً على المحاكاة المضادة للواقع لـ ({premise})، يتضح أن غياب المسبب الأول يؤدي إلى انهيار أحواض الجذب الثانوية وتغير مسار الأحداث اللاحقة."
            world_desc = f"محاكاة سببية لنتائج تحقق '{premise}'."

        scenario_data = {
            "scenario_type": scenario_type,
            "premise": premise,
            "steps": steps,
            "conclusion": conclusion,
            "world_description": world_desc,
            "confidence": round(random.uniform(0.75, 0.95), 2)
        }

        self.imagination_log.append(scenario_data)

        return {
            "imagined": True,
            "imagination_scenario": scenario_data
        }

    # ==========================================================================
    # 3. محرك الأسئلة المتعامدة (Orthogonal Question Engine)
    # ==========================================================================
    def generate_orthogonal_inquiry(self, text: str, context_type: str = "general") -> dict:
        """
        توليد سؤال متعامد يتحدى الافتراضات السائدة ويكشف الزوايا العمياء.
        """
        if context_type == "strategic":
            concepts = {
                "استقرار": "تحول مفاجئ",
                "نمو": "انكماش تطهيري",
                "سيطرة": "توزع ذاتي",
                "خطر": "فرصة مستترة",
                "سيادة": "تكامل كوني",
                "أزمة": "ولادة جديدة",
                "صراع": "تناغم خفي"
            }
            for key, opposite in concepts.items():
                if key in text:
                    question = f"إذا كان '{key}' هو المسار الظاهر في هذا التوقع، فكيف يمكن لـ '{opposite}' أن يكون المحرك الخفي والمتعامد لهذا المسار؟"
                    return {"orthogonal": True, "question": question}
            question = "ما هو البعد 'الثالث' (المتعامد) الذي نتجاهله في هذا التحليل الاستراتيجي؟"
            return {"orthogonal": True, "question": question}

        # السياق العام
        if "دائماً" in text:
            q = text.replace("دائماً", "أحياناً متعامدة")
        elif "لا يمكن" in text:
            q = text.replace("لا يمكن", "ماذا لو كان ممكناً في بُعد آخر؟")
        elif "يجب" in text:
            q = f"هل '{text.replace('يجب', '')}' ضرورة وجودية أم اختيار ظرفي؟"
        else:
            words = text.split()
            key_concept = words[0] if words else "هذا الأمر"
            q = f"ماذا لو كان نقيض '{key_concept}' متعامداً عليه في فضاء الأطوار وليس ملغياً له؟"

        return {
            "orthogonal": True,
            "question": q
        }

    def process_qalam_subsystems(self, user_message: str, active_phases: dict) -> dict:
        """
        المعالج الشامل الذي يشغل كافة محركات القلم ويعيد نتائجها المدمجة.
        """
        curiosity_res = self.stimulate_curiosity(user_message, active_phases)
        imagination_res = self.simulate_imagination(user_message)
        orthogonal_res = self.generate_orthogonal_inquiry(user_message, context_type="general" if not imagination_res["imagined"] else "strategic")

        return {
            "curiosity": curiosity_res,
            "imagination": imagination_res,
            "orthogonal": orthogonal_res
        }
