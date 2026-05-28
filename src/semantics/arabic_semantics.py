# -*- coding: utf-8 -*-
"""
Arabic Semantics - Adapted for Mirnan
=====================================

تضمين واعٍ بالمعاني الفلسفية للحروف والجذور العربية.
تم تحويله ليعتمد على مصفوفات NumPy وموجات Phase Vectors ليتوافق
مع معمارية المرنان (No Neural Networks).
"""

import json
import os
import math
import sqlite3
from typing import Dict, List, Optional, Tuple
import numpy as np


class CharacterSemanticEmbedding:
    """
    تضمين دلالي للحروف العربية
    
    كل حرف عربي له معنى دلالي وفلسفي خاص به.
    هذه الفئة تولد موجات Phase Vectors بناءً على هذه المعاني 
    لتغذية المرنان بفلسفة الحروف بشكل رياضي فيزيائي.
    """
    
    def __init__(self, dim: int = 16):
        self.dim = dim
        self.arabic_letters = list("أبتثجحخدذرزسشصضطظعغفقكلمنهوي")
        self.letter_to_idx = {l: i for i, l in enumerate(self.arabic_letters)}
        
        # معاني الحروف الدلالية (الجانب الفلسفي للمرنان)
        self.semantic_categories = {
            "أ": 0,  # ابتداء
            "ب": 1,  # بناء
            "ت": 2,  # إتيان
            "ث": 3,  # كثرة
            "ج": 4,  # جمع
            "ح": 5,  # حياة
            "خ": 6,  # خفاء
            "د": 7,  # دخول
            "ذ": 8,  # إشارة
            "ر": 9,  # تكرار
            "ز": 10, # زيادة
            "س": 11, # سر
            "ش": 12, # انتشار
            "ص": 13, # صفاء
            "ض": 14, # ضغط
            "ط": 15, # امتداد
            "ظ": 16, # ظهور
            "ع": 17, # اقتلاع
            "غ": 18, # غياب
            "ف": 19, # فتح
            "ق": 20, # قوة
            "ك": 21, # عطاء
            "ل": 22, # إحاطة
            "م": 23, # استيعاب
            "ن": 24, # ظهور
            "ه": 25, # جهد
            "و": 26, # وجهة
            "ي": 27, # عمق
        }
        
        self.num_categories = 28
        self._cache = {}

    def _generate_phase_vector(self, category_idx: int) -> np.ndarray:
        """
        توليد موجة جيبية (Sine/Cosine Phase Vector) بناءً على الفئة الدلالية.
        """
        vec = np.zeros(self.dim)
        for i in range(self.dim):
            # نوزع الترددات بناءً على الفئة لتشكيل بصمة رياضية (Phase fingerprint)
            freq = (category_idx + 1) * math.pi / self.num_categories
            if i % 2 == 0:
                vec[i] = math.sin(freq * (i + 1))
            else:
                vec[i] = math.cos(freq * (i + 1))
        
        # Normalization
        norm = np.linalg.norm(vec)
        if norm > 1e-10:
            vec = vec / norm
        return vec

    def get_character_vector(self, char: str) -> np.ndarray:
        if char in self._cache:
            return self._cache[char]
            
        cat_idx = self.semantic_categories.get(char, -1)
        if cat_idx == -1:
            vec = np.zeros(self.dim)
        else:
            vec = self._generate_phase_vector(cat_idx)
            
        self._cache[char] = vec
        return vec

    def get_word_semantic_vector(self, word: str) -> np.ndarray:
        """
        حساب المتجه الفلسفي للكلمة عن طريق دمج متجهات حروفها كمتوسط حسابي متساوٍ.
        """
        vectors = []
        
        for char in word:
            vec = self.get_character_vector(char)
            if np.any(vec):
                vectors.append(vec)
                
        if not vectors:
            return np.zeros(self.dim)
            
        semantic_vec = np.mean(vectors, axis=0)
        norm = np.linalg.norm(semantic_vec)
        if norm > 1e-10:
            semantic_vec = semantic_vec / norm
            
        return semantic_vec


class ArabicRootExtractor:
    """
    مستخرج الجذور العربية الديناميكي والخوارزمي.
    يعتمد على المطابقة مع الأوزان الصرفية بدلاً من القاموس الثابت.
    """
    
    def __init__(self, semantic_db_path: Optional[str] = None):
        self.augmentation_letters = set("سألتمونيها")
        self.definite_article = "ال"
        
        self.attached_pronouns = [
            "هم", "هن", "هما", "ها", "ه", "ون", "ين", "ان", "ات",
            "كم", "كن", "كما", "ك", "تم", "تن", "تما", "وا",
            "نا", "ني", "ي", "ت"
        ]
        
        self.prefixes = ["و", "ف", "ب", "ل", "ك"]
        
        # أوزان الصرف الأساسية: (الوزن، مواقع ف-ع-ل)
        self.patterns = [
            ("استفعال", [3, 4, 6]),  # استخراج -> خرج
            ("مستفعل", [3, 4, 5]),   # مستخرج -> خرج
            ("استفعل", [3, 4, 5]),   # استخرج -> خرج
            ("يتفعلون", [3, 4, 5]),  # يتساءلون (not exactly but you get the idea)
            ("انفعال", [2, 3, 5]),   # انكسار -> كسر
            ("افتعال", [1, 3, 5]),   # استماع -> سمع
            ("مفاعيل", [1, 3, 5]),   # مصابيح -> صبـح
            ("مفاعلة", [1, 3, 4]),   # مشاركة -> شرك (إذا لم تُحذف التاء المربوطة)
            ("مفاعل", [1, 3, 4]),    # مساجد -> سجد
            ("تفعيل", [1, 2, 4]),    # تسليم -> سلم
            ("تفاعل", [1, 3, 4]),    # تعارف -> عرف
            ("تفعّل", [1, 2, 4]),    # تجمع -> جمع
            ("مفعول", [1, 2, 4]),    # مكتوب -> كتب
            ("فعائل", [0, 1, 4]),    # صحائف -> صحف
            ("فواعل", [0, 3, 4]),    # ظواهر -> ظهر
            ("أفعال", [1, 2, 4]),    # أبطال -> بطل
            ("إفعال", [1, 2, 4]),    # إكرام -> كرم
            ("أفعل", [1, 2, 3]),     # أجمل -> جمل
            ("مفعل", [1, 2, 3]),     # مسجد -> سجد
            ("فاعل", [0, 2, 3]),     # كاتب -> كتب
            ("فعال", [0, 1, 3]),     # كتاب -> كتب
            ("فعول", [0, 1, 3]),     # قبول -> قبل
            ("فعيل", [0, 1, 3]),     # جميل -> جمل
            ("فعلة", [0, 1, 2]),     # ضربة -> ضرب (إذا لم تُحذف التاء المربوطة)
            ("يفعل", [1, 2, 3]),     # يكتب -> كتب
            ("تفعل", [1, 2, 3]),     # تكتب -> كتب
            ("نفعل", [1, 2, 3]),     # نكتب -> كتب
            ("أفعل", [1, 2, 3]),     # أكتب -> كتب
        ]
        
        self.known_roots = {}
        self.word_to_root_cache = {}
        
        if semantic_db_path and os.path.exists(semantic_db_path):
            self._load_semantic_db(semantic_db_path)
            
        # إعداد قاعدة الرموز (Arramooz)
        self.arramooz_conn = None
        self.arramooz_cursor = None
        try:
            db_path = os.path.join(os.path.dirname(__file__), '../../arabic_tools/arramooz/arramooz.db')
            db_path = os.path.abspath(db_path)
            if os.path.exists(db_path):
                self.arramooz_conn = sqlite3.connect(db_path, check_same_thread=False)
                self.arramooz_cursor = self.arramooz_conn.cursor()
        except Exception as e:
            print(f"Warning: Could not connect to Arramooz DB at {db_path}: {e}")

    def __del__(self):
        if hasattr(self, 'arramooz_conn') and self.arramooz_conn:
            self.arramooz_conn.close()
    
    def _load_semantic_db(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            roots = data.get("roots", {})
            for root_key, root_data in roots.items():
                root = root_data.get("root", root_key)
                self.known_roots[root_key] = root
                
                derivatives = root_data.get("derivatives", [])
                for deriv in derivatives:
                    self.word_to_root_cache[deriv] = root_key
                    
        except Exception as e:
            pass
    
    def extract(self, word: str) -> Tuple[str, float]:
        if word in self.word_to_root_cache:
            return self.word_to_root_cache[word], 1.0
        
        clean_word = self._clean_word(word)
        
        if clean_word in self.word_to_root_cache:
            return self.word_to_root_cache[clean_word], 0.9
            
        # محاولة البحث الدقيق في قاعدة بيانات الرموز
        arramooz_root = self._lookup_arramooz(clean_word)
        if arramooz_root:
            self.word_to_root_cache[word] = arramooz_root
            self.word_to_root_cache[clean_word] = arramooz_root
            return arramooz_root, 1.0
        
        root, confidence = self._extract_algorithmic(clean_word)
        
        # حفظ النتيجة لعدم تكرار المعالجة
        self.word_to_root_cache[word] = root
        
        return root, confidence
        
    def _lookup_arramooz(self, word: str) -> Optional[str]:
        if not self.arramooz_cursor:
            return None
        
        try:
            # البحث في الأفعال
            self.arramooz_cursor.execute("SELECT root FROM verbs WHERE unvocalized = ? LIMIT 1", (word,))
            row = self.arramooz_cursor.fetchone()
            if row and row[0]:
                return row[0]
            
            # البحث في الأسماء
            self.arramooz_cursor.execute("SELECT root FROM nouns WHERE unvocalized = ? LIMIT 1", (word,))
            row = self.arramooz_cursor.fetchone()
            if row and row[0]:
                return row[0]
        except Exception:
            pass
        return None
    
    def _clean_word(self, word: str) -> str:
        word = self._remove_diacritics(word)
        
        # إزالة "ال" التعريف
        if word.startswith(self.definite_article) and len(word) > 4:
            word = word[2:]
        
        # إزالة السوابق (تراكمية)
        for _ in range(2): # كرر مرتين لإزالة سوابق متعددة مثل (وبالـ)
            for prefix in self.prefixes:
                if word.startswith(prefix) and len(word) > 4:
                    word = word[1:]
                    break
        
        # إزالة اللواحق (الضمائر)
        for pronoun in sorted(self.attached_pronouns, key=len, reverse=True):
            if word.endswith(pronoun) and len(word) > len(pronoun) + 2:
                word = word[:-len(pronoun)]
                break
                
        # إزالة التاء المربوطة
        if word.endswith("ة") and len(word) > 3:
            word = word[:-1]
        
        return word
    
    def _remove_diacritics(self, text: str) -> str:
        diacritics = "ًٌٍَُِّْـ"
        return ''.join(c for c in text if c not in diacritics)
    
    def _extract_algorithmic(self, word: str) -> Tuple[str, float]:
        if len(word) <= 3:
            return "-".join(list(word)), 0.8
            
        # محاولة المطابقة مع الأوزان الصرفية
        for pattern, root_indices in self.patterns:
            if len(word) == len(pattern):
                root_chars = []
                match = True
                for i in range(len(word)):
                    if i in root_indices:
                        root_chars.append(word[i])
                    elif word[i] != pattern[i] and word[i] in self.augmentation_letters:
                        # تساهل بسيط لحروف العلة أو الهمزات
                        if pattern[i] == 'ا' and word[i] in 'أإآويا':
                            continue
                        elif pattern[i] == 'ء' and word[i] in 'ؤئء':
                            continue
                        else:
                            match = False
                            break
                    elif word[i] != pattern[i]:
                        match = False
                        break
                        
                if match and len(root_chars) >= 3:
                    return "-".join(root_chars[:3]), 0.95
        
        # فشل المطابقة؟ تفكيك حرفي (تجريد تجريبي)
        root_letters = []
        for i, char in enumerate(word):
            if i == 0 or char not in self.augmentation_letters or len(root_letters) < 3:
                root_letters.append(char)
        
        if len(root_letters) >= 3:
            return "-".join(root_letters[:3]), 0.6
        elif len(root_letters) == 2:
            return "-".join(root_letters), 0.4
        else:
            return word[0] if word else "؟", 0.2
            
    def batch_extract(self, words: List[str]) -> List[Tuple[str, float]]:
        return [self.extract(word) for word in words]
