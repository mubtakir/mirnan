"""
Tawaqu - Enhanced Symbolic Reasoning Engine
محرك التفكير الرمزي المتقدم - محركات قواعد متعددة
"""

import re
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class DomainExpert:
    """خبير مجال متخصص"""
    
    def __init__(self, name: str, rules: Dict, analysis_template: str):
        self.name = name
        self.rules = rules
        self.template = analysis_template
    
    def analyze(self, topic: str, context: str = "") -> str:
        """تحليل باستخدام القواعد"""
        topic_lower = topic.lower()
        relevant_rules = []
        
        for keyword, rule in self.rules.items():
            if keyword.lower() in topic_lower:
                relevant_rules.append(rule)
        
        if not relevant_rules:
            relevant_rules = list(self.rules.values())[:3]
        
        return self._apply_template(topic, relevant_rules, context)
    
    def _apply_template(self, topic: str, rules: List, context: str) -> str:
        """تطبيق القواعد على القالب"""
        if callable(self.template):
            return self.template(topic, rules, context)
        template = self.template.format(topic=topic, rules=rules, context=context)
        return template


class EconomicExpert(DomainExpert):
    """خبير الاقتصاد"""
    
    def __init__(self):
        rules = {
            "سيادة": "السيادة الاقتصادية تؤثر على الاستقرار",
            "iş": "العمل والمشاريع تخلق فرصemployment",
            "نقود": "التضخم يضعف القوة الشرائية",
            "استثمار": "الاستثمار الأجنبي يدعم النمو",
            "قطاع": "القطاعات الإنتاجية تحتاج دعمgovernment",
            "مصرف": "البنوك المركزية تتحكم بالسيولة",
            "سوق": "العرض والطلب يحددان الأسعار",
            "تنمية": "التنمية المستدامة تحتاج إصلاحلات",
            "بطالة": "البطالة ترفع تكاليف的生产",
            "دفع": "الدفع الحكومي يحفز الاقتصاد",
        }
        super().__init__("الاقتصاد", rules, self._template)
    
    def _template(self, topic: str, rules: List, context: str) -> str:
        return f"""## التحليل الاقتصادي: {topic}

### المنظور الاقتصادي:
اقتصادياً، يواجه {topic} عدة عوامل مؤثرة:

**العوامل الجوهرية:**
{chr(10).join(f"- {r}" for r in rules[:5])}

### المؤشرات الاقتصادية:
| المؤشر | الوضع | التوقع |
|--------|--------|---------|
| النمو الاقتصادي | متقلب | {-1,+1}% |
| التضخم | مرتفع | 3-8% |
| الاستثمار | محدود | -5% |
| البطالة | مرتفعة | 8-15% |

### السيناريوهات:
**أ) سيناريو تفاقم (30%):**
- تراجع الاستثمار الخاص
- ارتفاع البطالة
- تضخم اقتصادي

**ب) سيناريو استقرار (50%):**
- نمو متواضع 2-3%
- استقرار التضخم
- بطالة مرتفعة لكن ثابتة

**ج) سيناريو تعافي (20%):**
- إصلاحات هيكلية
- نمو 4-5%
- انخفاض البطالة

### التوصيات:
1. **تبعثر المالية**: دعم القطاعات الإنتاجية
2. **تنمية مصادر ا��دخل**: تنويع مصادر الإيرادات
3. **إصلاح السوق**: تحسين بيئة الأعمال
4. **الحماية الاجتماعية**: دعم الفئات vulnerable
"""


class PoliticalExpert(DomainExpert):
    """خبير السياسة"""
    
    def __init__(self):
        rules = {
            "حكم": "الحكم الرشيد يضمن الاستقرار",
            "شرعية": "الشرعية الشعبية أساس الحكم",
            "معارضة": "المعارضة البناءة تطور السياسة",
            "دولة": "مؤسسات الدولة تتحمل المسؤولية",
            "شعب": "الشعب basis الشرعية",
            "سلطة": "السلطة مسؤولية وليست امتياز",
            "قرار": "القرارات السياسية affected بالضغط",
            "توافق": "التوافق الوطني solves الأزمات",
            "إصلاح": "الإصلاح السياسي يحتاج وقت",
            "ثورة": "التغيير الثوري has ثمن",
        }
        super().__init__("السياسة", rules, self._template)
    
    def _template(self, topic: str, rules: List, context: str) -> str:
        return f"""## التحليل السياسي: {topic}

### السياق السياسي:
{topic} يتأثر بـ:

**القوى الفاعلة:**
{chr(10).join(f"- {r}" for r in rules[:5])}

### تحليل stakeholders:
| الفاعل | الموقف | التأثير |
|--------|--------|---------|
| الحكومة | [موقف] | عالي |
| المعارضة | [موقف] | متوسط |
| الشعب | [موقف] | عالي |
| مؤسسات الدولة | [موقف] | متوسط |
| القوى الخارجية | [موقف] | منخفض |

### السيناريوهات:
**1. سيناريو الإصلاح (40%):**
- تفاوض وتشاور
- إصلاحات تدريجية
- دعم شعبي

**2. سيناريو التصعيد (30%):**
- فشل التفاوض
- تصعيد الصراع
- تدخل خارجي محتمل

**3. سيناريو الجمود (30%):**
- حالة شلل سياسي
- استمرار الأزمة
- استياء شعبي متزايد

### التوصيات:
1. **تشكيل لجنة تفاوض**:representation واسعة
2. **EDULE مرونة**: في المواقف
3. **الحوار المستمر**: مع جميع الأطراف
4. **الشفافية**: في القرارات
"""


class StrategyExpert(DomainExpert):
    """خبير الاستراتيجية"""
    
    def __init__(self):
        rules = {
            "ميزة": "الميزة التنافسية تسود",
            "موارد": "الموارد تحدد возможности",
            "فرصة": "الفرص يجب استغلالها",
            "تهديد": "التهديدات must مواجهتها",
            "نقاط قوة": "النقاط القوية must تستخدم",
            "نقاط ضعف": "النقاط الضعيمة must تعالج",
            "هدف": "الأهداف واضحة must تكون",
            "خطة": "الخطة must مرنة",
            "تنفيذ": "التنفيذ must متابع",
            "تقييم": "التقييم must دوري",
        }
        super().__init__("الاستراتيجية", rules, self._template)
    
    def _template(self, topic: str, rules: List, context: str) -> str:
        return f"""## التحليل الاستراتيجي: {topic}

### التحليل الرباعي (SWOT):

**نقاط القوة (S):**
{chr(10).join(f"- {r}" for r in rules[:2])}

**نقاط الضعف (W):**
- موارد محدودة
- خبرة محدودة

**الفرص (O):**
- تطورات технологиية
- أسواق جديدة

**التهديدات (T):**
- منافسة قوية
- تغيرات السوق

### خطة العمل الاستراتيجي:

**الأولوية القصوى:**
1. [هدف] في quarter القادم

**الخطوات التنفيذية:**
1. **الأسبوع 1-2**: [إجراء]
2. **الأسبوع 3-4**: [إجراء]
3. **الشهر 2**: [إجراء]

**مؤشرات النجاح:**
- KPI 1: [قيمة]
- KPI 2: [قيمة]
- KPI 3: [قيمة]

### إدارة المخاطر:
| الخطر | الاحتمال | الأثر | الخطة |
|-------|----------|------|--------|
| تأخر التنفيذ | 40% | متوسط | خطة بديلة |
| نقص الموارد | 30% | عالي | احتياطي |
| تغيير السوق | 50% | منخفض | مرونة |
"""


class CaseLibrary:
    """مكتبة السوابق"""
    
    def __init__(self):
        self.cases = self._load_cases()
    
    def _load_cases(self) -> List[Dict]:
        """تحميل السوابق"""
        return [
            {
                "topic": "أزمة اقتصادية",
                "case": "أزمة 2008 المالية",
                "lesson": "التدخل الحكومي السريع ضروري",
                "outcome": "انتعاش بعد سنتين",
            },
            {
                "topic": "إصلاح سياسي",
                "case": "التحول الدنماركي",
                "lesson": "الإصلاح التدريجي ناجح",
                "outcome": "استقرار طويل الأمد",
            },
            {
                "topic": "تنمية اقتصادية",
                "case": "النموKorean",
                "lesson": "التعليم والصناعة مفتاح النجاح",
                "outcome": "نمو 10% سنوياً",
            },
            {
                "topic": "مقاومة التضخم",
                "case": "مقاومة في岸يض",
                "lesson": "السياسة النقدية الصارمة ضرورية",
                "outcome": "انخفاض التضخم",
            },
        ]
    
    def find_similar(self, topic: str) -> List[Dict]:
        """البحث عن سوابق مشابهة"""
        results = []
        for case in self.cases:
            if any(word in case["topic"] for word in topic.split()):
                results.append(case)
        return results[:3]


class CausalChain:
    """السلسلة السببية"""
    
    def __init__(self):
        self.chains = {
            "اقتصادي": [
                ["تراجع الاست会导致 →", "ارتفاع البطالة会导致 →", "تراجع الطلب会导致 →", "ركود اقتصادي"],
                ["ارتفاع الفائدة会导致 →", "تراجع الاستثمار会导致 →", "تباطؤ النمو会导致 →", "بطالة"],
            ],
            "سياسي": [
                ["أزمة اقتصادية会导致 →", "استياء شعبي会导致 →", ",ضغط على الحكومة会导致 →", "إصلاح أو تصعيد"],
                ["تدخل خارجي会导致 →", "صراع سياسي会导致 →", "انقسام مجتمعي会导致 →", "أزمة نظام"],
            ],
        }
    
    def analyze(self, topic: str) -> str:
        """تحليل سببي"""
        topic_lower = topic.lower()
        
        for domain, chains in self.chains.items():
            if domain in topic_lower:
                results = chains
                break
        else:
            return "لا توجد سلسلة سببية متاحة"
        
        output = f"## السلسلة السببية: {topic}\n\n"
        for i, chain in enumerate(results[:2], 1):
            output += f"**السلسلة {i}:**\n"
            for step in chain:
                output += f"→ {step}\n"
            output += "\n"
        
        return output


class EnhancedSymbolicEngine:
    """المحرك الرمزي المتقدم"""
    
    def __init__(self):
        self.economic_expert = EconomicExpert()
        self.political_expert = PoliticalExpert()
        self.strategy_expert = StrategyExpert()
        self.case_library = CaseLibrary()
        self.causal_chain = CausalChain()
        
        self.topic_patterns = {
            "econom": self.economic_expert,
            "اقتصاد": self.economic_expert,
            "مال": self.economic_expert,
            "سياسة": self.political_expert,
            "حكم": self.political_expert,
            "دولة": self.political_expert,
            "strategy": self.strategy_expert,
            "خطة": self.strategy_expert,
            "هدف": self.strategy_expert,
        }
    
    def reason(self, prompt: str, system: str = "") -> str:
        """الاستدلال الرئيسي"""
        prompt_lower = prompt.lower()
        
        # تحديد المجال
        expert = self.strategy_expert  # default
        for keyword, exp in self.topic_patterns.items():
            if keyword in prompt_lower:
                expert = exp
                break
        
        # تحليل الموضوع
        analysis = expert.analyze(prompt, system)
        
        # إضافة السوابق
        similar_cases = self.case_library.find_similar(prompt)
        if similar_cases:
            analysis += "\n\n## السوابق المشابهة:\n"
            for case in similar_cases:
                analysis += f"- **{case['case']}**: {case['lesson']}\n"
        
        # إضافة السلسلة السببية
        causal = self.causal_chain.analyze(prompt)
        if causal and "لا توجد" not in causal:
            analysis += f"\n\n{causal}"
        
        return analysis


# Singleton
_enhanced_engine = None


def get_enhanced_engine() -> EnhancedSymbolicEngine:
    """الحصول على المحرك المتقدم"""
    global _enhanced_engine
    if _enhanced_engine is None:
        _enhanced_engine = EnhancedSymbolicEngine()
    return _enhanced_engine


def reason(prompt: str, system: str = "") -> str:
    """الدالة الرئيسية"""
    engine = get_enhanced_engine()
    return engine.reason(prompt, system)
