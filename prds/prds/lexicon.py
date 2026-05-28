import os
import numpy as np
from scipy import sparse
from collections import defaultdict
import re
import json

# ============================================================
# ثوابت الكتل والفيزياء الطورية (PIDLM V2 constants)
# ============================================================
PHYSICAL_CONSTANTS = {
    "h": 1.0,            # ثابت بلانك الدلالي (Semantic Planck)
    "c": 1.0,            # سرعة الضوء الدلالي
    "G": 1.0,            # ثابت الجاذبية الدلالي
    "kB": 0.1,           # ثابت بولتزمان (ضوضاء حرارية دلالية)
    "D": 8,              # عدد أبعاد الفضاء الطوري HD-ROV
    "gravity_scale": 1.0, # مقياس قوة الجاذبية لضبط التوازن مع اقتران كوراموتو (تفعيل كامل بقوة مساوية لـ Kuramoto)
}

LETTER_OMEGA_0 = {
    "أ": 2.71, "إ": 2.65, "آ": 2.75, "ء": 2.70, "ؤ": 2.50, "ئ": 2.55,
    "ا": 2.71, "ب": 1.62, "ت": 1.85, "ث": 1.95, "ج": 2.10, "ح": 2.30,
    "خ": 2.40, "د": 1.75, "ذ": 1.80, "ر": 2.20, "ز": 2.05, "س": 2.15,
    "ش": 2.25, "ص": 2.35, "ض": 2.45, "ط": 2.50, "ظ": 2.55, "ع": 2.60,
    "غ": 2.65, "ف": 2.00, "ق": 2.30, "ك": 1.90, "ل": 2.10, "م": 2.00,
    "ن": 2.15, "ه": 1.80, "و": 1.95, "ي": 2.20, "ة": 1.80, "ى": 2.18
}

class WordPhysics:
    """
    الخصائص الفيزيائية للكلمة (Word Physics Properties)
    """
    def __init__(self, omega: float, energy: float, mass: float, phase_vector: np.ndarray):
        self.omega = omega
        self.energy = energy
        self.mass = mass
        self.phase_vector = phase_vector

class WordRegistry:
    """
    سجل عالمي لكل كلمة وخصائصها الفيزيائية
    """
    def __init__(self, lexicon):
        self.lexicon = lexicon
        self.words = {}
        
    def compute_or_retrieve(self, word: str) -> WordPhysics:
        if word in self.words:
            return self.words[word]
            
        omega = self.lexicon.compute_word_frequency(word)
        h = PHYSICAL_CONSTANTS["h"]
        c = PHYSICAL_CONSTANTS["c"]
        E = h * omega
        m = E / (c ** 2)
        phase = self.lexicon.compute_word_phase_vector(word)
        
        wp = WordPhysics(omega=omega, energy=E, mass=m, phase_vector=phase)
        self.words[word] = wp
        return wp


# ============================================================
# جدول الإعراب الطوري (I'rab Phase Map)
# يُترجم الحركة الإعرابية الأخيرة للكلمة إلى رمز نحوي
# ============================================================
IRAB_MAP = {
    '\u064f': 'n',  # ضمة          → مرفوع  (فاعل / مبتدأ / خبر)
    '\u064c': 'n',  # تنوين ضم     → مرفوع
    '\u064e': 'a',  # فتحة         → منصوب  (مفعول / خبر كان / حال)
    '\u064b': 'a',  # تنوين فتح    → منصوب
    '\u0650': 'g',  # كسرة         → مجرور  (مضاف إليه / اسم حرف جر)
    '\u064d': 'g',  # تنوين كسر    → مجرور
    '\u0652': 'j',  # سكون         → مجزوم  (فعل مجزوم في جواب الشرط)
}

# إزاحة التردد الذاتي ω بحسب الحالة الإعرابية
# المرفوع (فاعل/مبتدأ) → تردد أعلى → بؤرة المذبذب القائد في كوراموتو
# المنصوب/المجرور     → تردد أخفض → يتبع الفاعل طورياً (تابع)
IRAB_OMEGA_BIAS = {
    'n':  0.30,   # مرفوع → +0.30 rad/s  (قائد)
    'a': -0.20,   # منصوب → -0.20 rad/s  (تابع - مفعول)
    'g': -0.30,   # مجرور → -0.30 rad/s  (تابع - إضافة / جر)
    'j': -0.10,   # مجزوم → -0.10 rad/s  (مشروط)
}

_DIACRITIC_RE = re.compile(r'[\u064B-\u0652\u0670\u0640]')
_PUNCT_KEEP_DIACRITICS_RE = re.compile(r'[^\w\s\u064B-\u0652\u0670\u0640]')

class DynamicLexicon:
    """
    المعجم الديناميكي (Dynamic Lexicon)
    يمثل الكلمات كعقد فيزيائية تحمل ترددات ذاتية وأطواراً ديناميكية.
    """
    def __init__(self, omega_range=(1.0, 3.5)):
        self.vocab = {}
        self.id2word = {}
        self.word_counts = defaultdict(int)
        self.doc_counts = defaultdict(int)
        self.omega = None
        self.features = None
        self.omega_range = omega_range
        self.dim = 8  # عدد الأبعاد الفيزيائية (HD-ROV)
        self.num_docs = 0
        self.pinned_words = set()
        
        # تهيئة قنوات الاتصال بقاعدة بيانات المرموز (Arramooz Al-Waseet DB)
        _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.arramooz_db_path = os.environ.get(
            "ARRAMOOZ_DB_PATH",
            os.path.join(_project_root, "data", "arramooz.db")
        )
        self.arramooz_dict = {}
        self.word_roots = {} # word -> root
        self.root2words = defaultdict(list) # root -> list of known words

        # تهيئة محرك مادية الحرف والفيزياء الدلالية (Raqeem Semantic Physics SPEC)
        try:
            from raqeem.src.core.semantic_physics_engine import SemanticPhysicsEngine
            self.spec_engine = SemanticPhysicsEngine()
            try:
                print("SPEC Engine activated successfully.")
            except:
                pass
        except Exception as e:
            try:
                print("SPEC Engine init failed.")
            except:
                pass
            self.spec_engine = None

        # تهيئة مستخرج الجذور العربية (Root-Aware Coupling)
        self.root_extractor = None
        try:
            from prds.arabic_root_extractor import ArabicRootExtractor
            self.root_extractor = ArabicRootExtractor()
        except Exception:
            try:
                import sys
                _qalam_path = os.environ.get(
                    "DYNAMIC_QALAM_PATH",
                    os.path.join(_project_root, "..", "Dynamic_pen", "Dynamic_qalam")
                )
                if _qalam_path not in sys.path and os.path.exists(_qalam_path):
                    sys.path.insert(0, _qalam_path)
                from core.embeddings.root_aware_embedding import ArabicRootExtractor
                self.root_extractor = ArabicRootExtractor()
            except Exception:
                pass

        # تهيئة قاعدة بيانات الحروف وسجل الكلمات الفيزيائي
        self._build_letter_db()
        self.word_registry = WordRegistry(self)


    # ----------------------------------------------------------
    # دوال الحركات والإعراب الطوري
    # ----------------------------------------------------------

    @staticmethod
    def strip_diacritics(word: str) -> str:
        """إزالة الحركات (التشكيل) من الكلمة واسترداد صورتها الجذعية"""
        return _DIACRITIC_RE.sub('', word)

    @staticmethod
    def get_base_form(word: str) -> str:
        """الحصول على الصورة الجذعية للكلمة (بلا حركات) للبحث في المعجم"""
        return DynamicLexicon.strip_diacritics(word)

    @staticmethod
    def extract_irab(word: str) -> str | None:
        """
        استخلاص الحالة الإعرابية من الحركة الأخيرة للكلمة.
        يُعيد: 'n' (مرفوع) | 'a' (منصوب) | 'g' (مجرور) | 'j' (مجزوم) | None
        """
        if not word:
            return None
        # إذا كانت الكلمة تنتهي بألف المد المرافقة لتنوين الفتح (مثال: زيداً أو زيدًا)
        # أو أي ملحقات مشابهة، فإننا نبحث عن التنوين/الحركة في آخر حرفين.
        for char in reversed(word[-2:]):
            if char in IRAB_MAP:
                return IRAB_MAP[char]
        return None

    @staticmethod
    def get_irab_omega_bias(word: str) -> float:
        """
        يُعيد إزاحة التردد الذاتي ω (بـ rad/s) بناءً على الحركة الإعرابية.

        الأساس الفيزيائي:
        في نموذج كوراموتو، المذبذب ذو التردد الأعلى يصبح القائد الذي تتزامن
        حوله باقي المذبذبات. منح الفاعل المرفوع تردداً أعلى يجعله فيزيائياً
        هو بؤرة الجملة، وهو ما يتطابق مع دوره النحوي في اللغة العربية.

        يُعيد 0.0 إذا لم تكن الكلمة مشكّلة أو كانت بلا حركة إعرابية.
        """
        irab = DynamicLexicon.extract_irab(word)
        return IRAB_OMEGA_BIAS.get(irab, 0.0)

    # ================================================================
    # قاموس الكلمات الأصيلة التي تبدأ بحروف قد تُظن سوابق (و، ل، ب، ف، ك)
    # هذه الكلمات لا تُفصَّل أبداً — يُعاملها النظام ككلمة مستقلة دائماً
    # ================================================================
    _LEXICAL_EXCEPTIONS = {
        # كلمات تبدأ بـ "و"
        'وجد', 'وجه', 'وطن', 'وقت', 'ولد', 'وصل', 'ورد', 'وضع', 'ورق', 'وسط',
        'وحيد', 'وداع', 'ودود', 'وفاء', 'وفي', 'وفاة', 'وحشة', 'وعد', 'ولي',
        'وراء', 'وثيق', 'وليد', 'ومضة', 'ونس', 'وهم', 'وهج', 'وميض',
        # كلمات تبدأ بـ "ل"
        'لبن', 'لون', 'لغة', 'لحظة', 'لعب', 'لجأ', 'لذة', 'لطف', 'لمس',
        'لواء', 'لهيب', 'لجنة', 'لئيم', 'لحم', 'لؤلؤ', 'لباس', 'لسان',
        'لحاء', 'لقاء', 'لحد', 'لتر', 'لصق', 'لغو',
        # كلمات تبدأ بـ "ب"
        'بيت', 'بحر', 'بدر', 'برق', 'بئر', 'بدن', 'بطل', 'بكاء', 'بلاغ',
        'بنية', 'بهجة', 'بصر', 'بساط', 'بسمة', 'براء', 'باب', 'بدع',
        # كلمات تبدأ بـ "ف"
        'فجر', 'فخر', 'فكر', 'فقر', 'فهم', 'فلك', 'فنار', 'فقه', 'فطر',
        'فيض', 'فضل', 'فراق', 'فضاء', 'فداء', 'فتنة', 'فصاحة',
        # كلمات تبدأ بـ "ك"
        'كتاب', 'كلام', 'كرم', 'كمال', 'كنز', 'كثير', 'كيف', 'كذب',
        'كفاح', 'كبرياء', 'كسب', 'كوكب', 'كشف', 'كساء',
    }

    def _smart_prefix_split(self, word: str) -> list:
        """
        الفصل الذكي للسوابق المتصلة (و، ف، ب، ك، ل، ال، لل، وال...).

        المبدأ الرئيسي (حل مشكلة الغموض):
        قبل فصل أي سابقة، نتحقق مما إذا كانت الكلمة بأكملها (قبل الفصل)
        كلمةً معروفةً مستقلة في المعجم أو في قائمة الاستثناءات. إذا كانت كذلك،
        نُبقيها كما هي ولا نفصل. مثال:
          - "لبن"  → كلمة مستقلة (حليب) → لا تُفصَّل
          - "لمحمد" → "ل" + "محمد" (لا تبدأ بحرف غريب) → تُفصَّل
          - "وجد" → كلمة مستقلة (found) → لا تُفصَّل
          - "وكتاب" → "و" + "كتاب" → تُفصَّل

        يعتمد خوارزمية التحقق الثلاثية:
        1. هل الكلمة (بأكملها) موجودة في قاموس الاستثناءات الصريح؟
        2. هل الكلمة (بأكملها) موجودة في معجم النموذج بحد ذاتها؟
        3. إذا شُقت الكلمة، هل الجزء الباقي له معنى (موجود في المعجم)؟
        """
        base = DynamicLexicon.strip_diacritics(word)

        # الخطوة 1: فحص قائمة الاستثناءات الصريحة
        if base in self._LEXICAL_EXCEPTIONS:
            return [word]

        # الخطوة 2: فحص وجود الكلمة كاملةً في معجم النموذج
        if base in self.vocab:
            return [word]

        # الخطوة 3: محاولة الفصل الذكي — نتحقق بعد كل فصل
        prefixes_found = []
        working = base

        # تسلسل أولويات السوابق: 3 أحرف أولاً ثم 2 ثم 1
        prefix_candidates = [
            ('وال', ['و', 'ال']),
            ('فال', ['ف', 'ال']),
            ('بال', ['ب', 'ال']),
            ('كال', ['ك', 'ال']),
            ('لال', ['ل', 'ال']),
            ('لل',  ['ل', 'ال']),
            ('ال',  ['ال']),
            ('و',   ['و']),
            ('ف',   ['ف']),
            ('ب',   ['ب']),
            ('ك',   ['ك']),
            ('ل',   ['ل']),
        ]

        for prefix, parts in prefix_candidates:
            if working.startswith(prefix):
                remainder = working[len(prefix):]

                # شرط الحد الأدنى: الجزء الباقي 3 أحرف على الأقل
                if len(remainder) < 2:
                    continue

                # التحقق الذكي: هل الجزء الباقي كلمة مستقلة في المعجم؟
                remainder_in_vocab = remainder in self.vocab
                # أو: هل يبدو منطقياً صرفياً (جذر عربي مبدوء بحرف من غير أحرف المضارعة/السوابق)
                # هذا يُقلص احتمالية الخطأ في حالات مثل "لبن" → "ل" + "بن"
                remainder_plausible = (
                    len(remainder) >= 3 or
                    remainder in self.arramooz_dict
                ) if hasattr(self, 'arramooz_dict') else len(remainder) >= 3

                if remainder_in_vocab or remainder_plausible:
                    prefixes_found = parts
                    working = remainder
                    break  # نأخذ أطول سابقة فقط (أولوية)

        if not prefixes_found:
            return [word]

        # إعادة بناء القائمة: السوابق + الكلمة الجذر
        result = prefixes_found[:]
        result.append(working)
        return result

    def clean_text(self, text: str) -> list[str]:
        """
        تنظيف النص وتقسيمه إلى كلمات مع الحفاظ على الحركات.
        يستخدم الفصل الذكي السياقي للسوابق (و، ف، ب، ك، ل، ال)
        مع تجنب تفكيك الكلمات الأصيلة المبدوءة بهذه الحروف.
        """
        text = _PUNCT_KEEP_DIACRITICS_RE.sub('', text)
        raw_words = text.strip().split()
        processed_words = []

        suffix_re = re.compile(r'^(.{3,})(ها|هم|كم|نا|ه|ك|ني)$')

        for w in raw_words:
            base_len = len(DynamicLexicon.strip_diacritics(w))

            # كلمات قصيرة جداً → لا تُفصَّل
            if base_len <= 2:
                processed_words.append(w)
                continue

            # ── الفصل الذكي للسوابق ──
            parts = self._smart_prefix_split(w)

            # معالجة اللاحقات على الكلمة الأخيرة فقط
            if len(parts) > 0:
                last_part = parts[-1]
                m_suf = suffix_re.match(DynamicLexicon.strip_diacritics(last_part))
                if m_suf and len(m_suf.group(1)) >= 3:
                    parts = parts[:-1] + [m_suf.group(1), m_suf.group(2)]

            processed_words.extend(parts)

        return processed_words


    def _load_arramooz_roots(self):
        """تحميل الجذور الصرفية للكلمات من قاعدة المرموز مع دعم استخراج الجذور عبر CAMeL Tools"""
        import os
        import sqlite3
        import sys
        
        # 1. تهيئة CAMeL Tools كشبكة أمان
        camel_analyzer = None
        _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        _arabic_tools_dir = os.environ.get(
            "ARABIC_TOOLS_PATH",
            os.path.join(_project_root, "arabic_tools")
        )
        if _arabic_tools_dir not in sys.path:
            sys.path.insert(0, _arabic_tools_dir)
            
        try:
            from camel_tools import ensure_camel_tools
            ensure_camel_tools()
            from camel_tools.morphology.database import MorphologyDB
            from camel_tools.morphology.analyzer import Analyzer
            db = MorphologyDB.builtin_calima()
            camel_analyzer = Analyzer(db)
            print("CAMeL Tools Analyzer activated for fallback root extraction.")
        except Exception as e:
            print(f"CAMeL Tools root fallback not available: {e}")

        # 2. جلب المرموز
        if os.path.exists(self.arramooz_db_path):
            try:
                conn = sqlite3.connect(self.arramooz_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT vocalized, root FROM verbs UNION SELECT vocalized, root FROM nouns")
                rows = cursor.fetchall()
                
                for voc, root in rows:
                    if voc and root:
                        clean_voc = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', voc)
                        clean_root = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', root)
                        self.arramooz_dict[clean_voc] = clean_root
                        
                conn.close()
            except Exception as e:
                print(f"تنبيه: تعذر تحميل قاعدة بيانات المرموز: {e}")

        # 3. المطابقة واستخراج الجذور (المرموز أولاً، ثم CAMeL)
        for word in self.vocab:
            if word in self.arramooz_dict:
                r = self.arramooz_dict[word]
                self.word_roots[word] = r
                self.root2words[r].append(word)
            elif camel_analyzer is not None:
                try:
                    analyses = camel_analyzer.analyze(word)
                    if analyses:
                        root_raw = analyses[0].get('root', '')
                        if root_raw and root_raw != 'NOAN':
                            # تنظيف جذر CAMeL (يأتي مفصولاً بنقاط: ك.ت.ب)
                            clean_root = root_raw.replace('.', '').replace(' ', '')
                            self.word_roots[word] = clean_root
                            self.root2words[clean_root].append(word)
                except:
                    pass

    def build(self, corpus_lines):
        """بناء المعجم من المدونة النصية"""
        self.num_docs = len(corpus_lines)
        word_doc_map = defaultdict(set)

        for doc_id, line in enumerate(corpus_lines):
            words = self.clean_text(line)
            for word in words:
                # البناء على الصورة الجذعية (بلا حركات) لتوحيد مدخلات التدريب
                base = self.strip_diacritics(word)
                self.word_counts[base] += 1
                word_doc_map[base].add(doc_id)

        sorted_words = sorted(self.word_counts.keys(), key=lambda w: self.word_counts[w], reverse=True)
        for idx, word in enumerate(sorted_words):
            # المعجم يخزن الصور الجذعية دائماً (بلا حركات)
            base = self.strip_diacritics(word)
            if base not in self.vocab:
                self.vocab[base] = idx
                self.id2word[idx] = base
            self.doc_counts[base] = len(word_doc_map.get(base, set()))

        if "<UNK>" not in self.vocab:
            unk_idx = len(self.id2word)
            self.vocab["<UNK>"] = unk_idx
            self.id2word[unk_idx] = "<UNK>"
            self.doc_counts["<UNK>"] = self.num_docs

        # إضافة الرموز الوظيفية لبوابات التفكير (Milestones)
        milestones = ["<المعطيات>", "<الخطوة_1>", "<الخطوة_2>", "<التحقق>", "<النتيجة>"]
        for m in milestones:
            if m not in self.vocab:
                midx = len(self.id2word)
                self.vocab[m] = midx
                self.id2word[midx] = m
                self.doc_counts[m] = self.num_docs
                self.pinned_words.add(midx)

        vocab_size = len(self.id2word)
        
        idfs = np.zeros(vocab_size)
        spec_energies = np.zeros(vocab_size)
        
        for word, idx in self.vocab.items():
            idfs[idx] = np.log(1 + self.num_docs / (1 + self.doc_counts[word]))
            if self.spec_engine and not word.startswith("<"):
                try:
                    res = self.spec_engine.calculate_filament_resonance(word)
                    spec_energies[idx] = abs(res)
                except:
                    spec_energies[idx] = 1.0
            else:
                spec_energies[idx] = 1.0

        if vocab_size > 0:
            min_idf, max_idf = np.min(idfs), np.max(idfs)
            if max_idf > min_idf:
                norm_idfs = (idfs - min_idf) / (max_idf - min_idf)
                if self.spec_engine:
                    norm_spec = spec_energies / (np.max(spec_energies) + 1e-9)
                    combined_weight = 0.6 * norm_idfs + 0.4 * norm_spec
                    base_omega = self.omega_range[0] + combined_weight * (self.omega_range[1] - self.omega_range[0])
                else:
                    base_omega = self.omega_range[0] + norm_idfs * (self.omega_range[1] - self.omega_range[0])
            else:
                base_omega = np.full(vocab_size, np.mean(self.omega_range))

            # ================================================================
            # فضاء المذبذبات الدلالية متعدد الأبعاد (Semantic HD-Phase Space)
            # كل بعد يُشفّر خاصية لغوية مستقلة للكلمة:
            #   d=0: دلالي (Semantic) — IDF + SPEC Energy
            #   d=1: نحوي (Syntactic/POS) — تمييز الأفعال/الأسماء/الصفات
            #   d=2: صوتي (Phonetic) — طاقة الحروف العربية
            #   d=3: صرفي/جذري (Morphological) — تشابه الجذر العربي
            #   d=4: عاطفي (Emotional/Valence) — تقطيب الكلمات الوجدانية
            #   d=5..7: سياقي حر (Free Contextual) — تعلم هيبي خالص
            # ================================================================
            self.omega = np.zeros((vocab_size, self.dim))

            # ---- d=0: دلالي (Semantic) ----
            self.omega[:, 0] = base_omega

            # ---- d=1: نحوي (Syntactic POS Dimension) ----
            # الأفعال: تردد أعلى (قائد نحوي) | الأسماء: متوسط | الصفات: أدنى
            POS_VERB_MARKERS  = {'ق', 'ن', 'ي', 'ت', 'أ', 'س'}   # أحرف مضارعة/أمر
            POS_ADJ_SUFFIXES  = {'ية', 'ان', 'ين', 'ات', 'ون'}
            for word, idx in self.vocab.items():
                if word.startswith('<'):
                    self.omega[idx, 1] = np.mean(self.omega_range)
                    continue
                first_char = word[0] if word else ''
                if first_char in POS_VERB_MARKERS:
                    self.omega[idx, 1] = self.omega_range[1]          # فعل → تردد عالٍ
                elif any(word.endswith(s) for s in POS_ADJ_SUFFIXES):
                    self.omega[idx, 1] = self.omega_range[0] + 0.5    # صفة → تردد منخفض نسبياً
                else:
                    self.omega[idx, 1] = np.mean(self.omega_range)    # اسم → تردد وسط

            # ---- d=2: صوتي (Phonetic Energy) ----
            # أحرف المد والهمزات والحروف الشمسية لها طاقة صوتية مختلفة
            PHONETIC_HIGH = set('قكطصضظثذ')    # أصوات مقلقلة وشديدة
            PHONETIC_LOW  = set('هوايءألر')    # أصوات مدية ورخوة
            ph_omega = np.full(vocab_size, np.mean(self.omega_range))
            for word, idx in self.vocab.items():
                if word.startswith('<') or not word:
                    continue
                ph_score = sum(1 for c in word if c in PHONETIC_HIGH) - \
                           sum(0.5 for c in word if c in PHONETIC_LOW)
                word_len = max(len(word), 1)
                norm_score = np.tanh(ph_score / word_len)          # [-1, 1]
                ph_omega[idx] = np.mean(self.omega_range) + norm_score * (self.omega_range[1] - self.omega_range[0]) * 0.5
            self.omega[:, 2] = ph_omega

            # ---- d=3: صرفي/جذري (Root Morphology) ----
            # الكلمات الأصيلة الجذرية (3-4 أحرف) تحمل تردداً صرفياً عالياً
            root_omega = np.full(vocab_size, np.mean(self.omega_range))
            for word, idx in self.vocab.items():
                if word.startswith('<') or not word:
                    continue
                base_len = len(word)
                if word in self.word_roots:
                    root = self.word_roots[word]
                    root_len = len(root)
                    # الجذر الثلاثي: إشارة اشتقاقية كاملة → تردد أعلى
                    if root_len == 3:
                        root_omega[idx] = self.omega_range[1]
                    elif root_len == 4:
                        root_omega[idx] = self.omega_range[1] - 0.3
                    else:
                        root_omega[idx] = np.mean(self.omega_range)
                else:
                    # كلمات قصيرة (حروف جر، ضمائر) → تردد صرفي منخفض
                    if base_len <= 2:
                        root_omega[idx] = self.omega_range[0]
                    else:
                        root_omega[idx] = np.mean(self.omega_range) - 0.2
            self.omega[:, 3] = root_omega

            # ---- d=4: عاطفي (Emotional Valence) ----
            # كلمات إيجابية → تردد عالٍ، سلبية → تردد منخفض
            POSITIVE_SEEDS = {'نور', 'جمال', 'حب', 'سلام', 'خير', 'فرح', 'أمل', 'حق',
                              'عدل', 'رحمة', 'بركة', 'نعمة', 'صدق', 'كرم', 'حكمة'}
            NEGATIVE_SEEDS = {'ظلم', 'كذب', 'حرب', 'خوف', 'حزن', 'غضب', 'كره', 'شر',
                              'خيانة', 'فساد', 'عذاب', 'خسارة', 'غدر', 'نفاق', 'ضلال'}
            emo_omega = base_omega.copy()
            for word, idx in self.vocab.items():
                if word in POSITIVE_SEEDS:
                    emo_omega[idx] = self.omega_range[1]
                elif word in NEGATIVE_SEEDS:
                    emo_omega[idx] = self.omega_range[0]
                # التوليد التدريجي: الكلمات التي تشاركها في المعجم تكتسب شحنتها
            self.omega[:, 4] = emo_omega

            # ---- d=5..7: أبعاد سياقية حرة (Free Contextual) ----
            # تبدأ عشوائية وتتطور عبر التعلم الهيبي خلال المحادثة
            for d in range(5, self.dim):
                self.omega[:, d] = base_omega + np.random.normal(0, 0.15, size=vocab_size)

        else:
            self.omega = np.zeros((0, self.dim))

        # تخصيص ترددات ذاتية منخفضة ومستقرة لرموز التفكير (في جميع الأبعاد)
        for m in milestones:
            if m in self.vocab:
                self.omega[self.vocab[m], :] = 1.1

        # تحميل الجذور الصرفية من المرموز
        self._load_arramooz_roots()

        self._build_feature_vectors(corpus_lines)


    def add_dynamic_token(self, word, fixed_omega=2.5, pinning=True, coupling_obj=None):
        """
        حقن كلمة أو ناتج رياضي جديد ديناميكياً في المعجم والذاكرة الطورية.
        تحديد التردد الذاتي وقوة التثبيت (Phase Pinning Force).
        """
        if word in self.vocab:
            wid = self.vocab[word]
            if pinning:
                self.pinned_words.add(wid)
            return wid

        new_id = len(self.id2word)
        self.vocab[word] = new_id
        self.id2word[new_id] = word
        
        new_omega = np.full((1, self.dim), fixed_omega)
        if self.dim > 1:
            new_omega[0, 1:] += np.random.normal(0, 0.2, size=self.dim - 1)
        self.omega = np.vstack([self.omega, new_omega])
        
        self.doc_counts[word] = self.num_docs
        self.word_counts[word] += 1
        if pinning:
            self.pinned_words.add(new_id)

        if coupling_obj is not None and hasattr(coupling_obj, 'expand_vocab'):
            coupling_obj.expand_vocab(len(self.id2word))

        if self.features is not None:
            old_shape = self.features.shape
            from scipy.sparse import csr_matrix, vstack, hstack
            zero_row = csr_matrix((1, old_shape[1]))
            expanded_rows = vstack([self.features, zero_row])
            zero_col = csr_matrix((old_shape[0] + 1, 1))
            self.features = hstack([expanded_rows, zero_col]).tocsr()

        return new_id

    def get_word_id(self, word, inject_oov=False, coupling_obj=None):
        """
        الحصول على معرف الكلمة مع الحفاظ على دعم الكلمات المشكّلة.

        التسلسل الهرمي للبحث:
        1. البحث بالصورة الجذعية (بلا حركات) — الحالة الأساسية
        2. البحث الصرفي عبر المرموز (Arramooz DB Bridge)
        3. مطابقة الجذر (Stemming Fallback)
        4. حقن الكلمة كعنصر جديد (إذا كان inject_oov=True)
        5. رمز <UNK> كملاذ أخير

        ملاحظة: الإزاحة الإعرابية (I'rab bias) تُحسب بـ get_irab_omega_bias()
        وتُمرَّر للمحرك بشكل مستقل ولا تؤثر على معرف الكلمة في المعجم.
        """
        # ← الخطوة 0: استخلاص الصورة الجذعية قبل أي بحث
        base = self.strip_diacritics(word)

        if base in self.vocab:
            return self.vocab[base]
            
        # 1. البحث الصرفي المتقدم عبر المرموز (Arramooz DB Bridge) — بالصورة الجذعية
        if hasattr(self, 'arramooz_dict') and self.arramooz_dict:
            cleaned_stem = re.sub(r'^(ال|ب|ل|ف|ك|و)+', '', base)
            word_to_check = cleaned_stem if cleaned_stem in self.arramooz_dict else base

            if word_to_check in self.arramooz_dict:
                extracted_root = self.arramooz_dict[word_to_check]
                if extracted_root in self.root2words and self.root2words[extracted_root]:
                    matched_word = self.root2words[extracted_root][0]
                    matched_id = self.vocab[matched_word]
                    self.vocab[base] = matched_id
                    return matched_id

        # 2. البحث عن أقرب كلمة تشترك في 3 أحرف متتالية على الأقل (Stemming Fallback)
        best_match = None
        max_overlap = 0
        cleaned_stem = re.sub(r'^(ال|ب|ل|ف|ك|و)+', '', base)
        if len(cleaned_stem) >= 3:
            for known_word, wid in self.vocab.items():
                if known_word == "<UNK>":
                    continue
                known_stem = re.sub(r'^(ال|ب|ل|ف|ك|و)+', '', known_word)
                if cleaned_stem in known_stem or known_stem in cleaned_stem:
                    if len(known_stem) > max_overlap:
                        max_overlap = len(known_stem)
                        best_match = wid

        if best_match is not None:
            self.vocab[base] = best_match
            return best_match

        if inject_oov:
            new_id = self.add_dynamic_token(base, fixed_omega=2.5, coupling_obj=coupling_obj)
            return new_id

        # 3. الملاذ الأخير: استخدام رمز <UNK>
        return self.vocab.get("<UNK>", 0)

    def _build_feature_vectors(self, corpus_lines, window_size=5):
        """بناء متجهات الخصائص المتفرقة للكلمات بناءً على الظهور المشترك"""
        vocab_size = len(self.vocab)
        row_ind = []
        col_ind = []
        data = []

        co_occur = defaultdict(float)

        for line in corpus_lines:
            words = [w for w in self.clean_text(line) if w in self.vocab]
            n = len(words)
            for i in range(n):
                w1 = self.vocab[words[i]]
                for j in range(max(0, i - window_size), min(n, i + window_size + 1)):
                    if i != j:
                        w2 = self.vocab[words[j]]
                        dist = abs(i - j)
                        co_occur[(w1, w2)] += 1.0 / dist  # وزن يتناسب عكسياً مع المسافة

        for (w1, w2), freq in co_occur.items():
            row_ind.append(w1)
            col_ind.append(w2)
            data.append(freq)

        self.features = sparse.csr_matrix((data, (row_ind, col_ind)), shape=(vocab_size, vocab_size))

    def get_omega(self, word_id):
        """الحصول على التردد الذاتي للكلمة"""
        return self.omega[word_id]

    def get_vocab_size(self):
        return len(self.vocab)

    def apply_root_aware_coupling(self, K_matrix):
        """
        تعزيز الجاذبية الدلالية للمصفوفة K بناءً على الترابط الجذري (Root-Aware Coupling).

        الأساس النظري:
        في اللغة العربية، الكلمات التي تشترك في نفس الجذر الصرفي (مثل: علم، عالم، معلوم) 
        غالباً ما تنتمي لنفس الحقل الدلالي الواسع. تقوم هذه الدالة باستخدام `ArabicRootExtractor` 
        من نموذج القلم (Dynamic Qalam) لاستخراج جذور الكلمات الديناميكية. 
        بمجرد اكتشاف كلمات ذات جذر مشترك، يتم مضاعفة معامل الجاذبية الفيزيائي (K_ij) 
        بينها بمعامل 3.0. هذا يضمن أن النظام عندما ينشط كلمة ما، فإنه يجذب لا شعورياً جميع 
        مشتقاتها الصرفية إلى بؤرة الرنين الطوري، مما يعزز الفهم الأصيل للغة.

        المعطيات:
            K_matrix (sparse matrix or ndarray): مصفوفة الاقتران الدلالي الحالية (مصفوفة متفرقة غالباً).

        المخرجات:
            sparse.csr_matrix or ndarray: مصفوفة الاقتران بعد تعزيز روابط الكلمات متحدة الجذر.
        """
        if self.root_extractor is None:
            return K_matrix
            
        # تجميع المعرفات (WIDs) بحسب الجذر لتقليل تعقيد المعالجة من O(V^2) إلى O(V)
        from collections import defaultdict
        root_to_wids = defaultdict(list)
        for word, wid in self.vocab.items():
            if word == "<UNK>" or word.startswith("<"):
                continue
            if word in self.word_roots:
                root_to_wids[self.word_roots[word]].append(wid)
            # تجاوز استخراج الجذور بالذكاء الاصطناعي لكامل المعجم هنا لتسريع الإقلاع
            # سيتم استخدامه للكلمات الجديدة عند الطلب (On-Demand)
                    
        is_sparse = hasattr(K_matrix, "todense") or hasattr(K_matrix, "toarray")
        if hasattr(K_matrix, "toarray"):
            K_dense = K_matrix.toarray()
        elif hasattr(K_matrix, "todense"):
            K_dense = np.asarray(K_matrix.todense())
        else:
            K_dense = np.asarray(K_matrix)

        # تحديث مصفوفة الجاذبية للعناقيد الجذرية باستخدام فهرسة NumPy السريعة
        for root, wids in root_to_wids.items():
            if len(wids) > 1:
                # إنشاء شبكة (Grid) متقاطعة من المعرفات
                grid = np.ix_(wids, wids)
                K_dense[grid] *= 3.0
                    
        if is_sparse:
            from scipy import sparse
            return sparse.csr_matrix(K_dense)
        return K_dense

    def _build_letter_db(self):
        self.letter_db = {}
        _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(_project_root, "raqeem", "src", "core", "letter_physics_matrix.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(_project_root, "raqeem/src/core/letter_physics_matrix.json")
            
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    letters_data = data.get("letters", {})
                    for char, info in letters_data.items():
                        v_22 = info.get("v", [])
                        operator = info.get("operator", "0")
                        if len(v_22) < 22:
                            v_22 = list(v_22) + [0] * (22 - len(v_22))
                        # Split the 22 dimensions into 8 bins and average them
                        chunks = np.array_split(v_22, 8)
                        v_8 = [float(np.mean(chunk)) for chunk in chunks]
                        dimensions = np.array([0.5 + 0.4 * float(val) for val in v_8], dtype=float)
                        
                        omega_0 = LETTER_OMEGA_0.get(char, None)
                        if omega_0 is None:
                            energy = sum(abs(val) for val in v_22) / 22.0
                            op_bias = 0.0
                            if operator == "+1":
                                op_bias = 0.5
                            elif operator == "-1":
                                op_bias = -0.2
                            elif operator == "i":
                                op_bias = 0.3
                            elif operator == "r":
                                op_bias = 0.2
                            omega_0 = float(np.clip(1.5 + 1.5 * energy + op_bias, 1.0, 3.5))
                            
                        self.letter_db[char] = {
                            "omega_0": omega_0,
                            "dimensions": dimensions
                        }
            except Exception as e:
                print(f"Error loading letter matrix: {e}")

    def compute_word_frequency(self, word: str) -> float:
        clean_w = self.strip_diacritics(word)
        if clean_w in ["الله", "الل"]:
            # "الله" (or its tokenized form "الل") is the absolute attractor in Arabic NLP and
            # represents maximum semantic energy and resonance.
            return 3.0

        word_letters = list(clean_w)
        
        root_letters = []
        if self.root_extractor is not None:
            try:
                root_str, _ = self.root_extractor.extract(word)
                root_letters = [ch for ch in root_str.split("-") if ch]
            except Exception:
                pass
                
        if not root_letters:
            root_letters = word_letters
            
        letter_freqs = [self.letter_db.get(ch, {}).get("omega_0", 2.0) for ch in word_letters if ch in self.letter_db]
        if not letter_freqs:
            letter_freqs = [LETTER_OMEGA_0.get(ch, 2.0) for ch in word_letters]
            
        root_freqs = [self.letter_db.get(ch, {}).get("omega_0", 2.0) for ch in root_letters if ch in self.letter_db]
        if not root_freqs:
            root_freqs = [LETTER_OMEGA_0.get(ch, 2.0) for ch in root_letters]
            
        w_freq = np.mean(letter_freqs) if letter_freqs else 2.0
        r_freq = np.mean(root_freqs) if root_freqs else 2.0
        
        return float((w_freq + r_freq) / 2.0)

    def compute_word_phase_vector(self, word: str) -> np.ndarray:
        clean_w = self.strip_diacritics(word)
        word_letters = list(clean_w)
        
        root_letters = []
        if self.root_extractor is not None:
            try:
                root_str, _ = self.root_extractor.extract(word)
                root_letters = [ch for ch in root_str.split("-") if ch]
            except Exception:
                pass
                
        if not root_letters:
            root_letters = word_letters
            
        def char_map_helper(ch: str) -> str:
            mapping = {
                "أ": "ا",
                "إ": "ا",
                "آ": "ا",
                "ة": "ه",
                "ى": "ي",
                "ؤ": "و",
                "ئ": "ي"
            }
            return mapping.get(ch, ch)
            
        vectors = []
        for ch in word_letters:
            mapped_ch = char_map_helper(ch)
            if mapped_ch in self.letter_db:
                vectors.append(self.letter_db[mapped_ch]["dimensions"])
            else:
                vectors.append(np.full(self.dim, 0.5))
                
        root_vectors = []
        for ch in root_letters:
            mapped_ch = char_map_helper(ch)
            if mapped_ch in self.letter_db:
                root_vectors.append(self.letter_db[mapped_ch]["dimensions"])
            else:
                root_vectors.append(np.full(self.dim, 0.5))
                
        combined = np.mean(vectors, axis=0) if vectors else np.full(self.dim, 0.5)
        root_vec = np.mean(root_vectors, axis=0) if root_vectors else np.full(self.dim, 0.5)
        
        return (combined + root_vec) / 2.0

    def __len__(self):
        return len(self.vocab)

