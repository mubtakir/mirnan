# المحرك الأساسي لنظام العلاقات الطورية الديناميكي (PRDS)
# Phase-Relational Dynamical System Core Package

from .lexicon import DynamicLexicon
from .coupling import PhaseCoupling
from .engine import KuramotoEngine
from .analyzer import PRDSAnalyzer
from .serialization import save_model_to_py, load_model_from_py

__all__ = ["DynamicLexicon", "PhaseCoupling", "KuramotoEngine", "PRDSAnalyzer",
           "save_model_to_py", "load_model_from_py", "read_paragraphs"]


def read_paragraphs(filepath: str, encoding: str = "utf-8") -> list[str]:
    """
    قراءة ملف نصي وتجميع أسطره في فقرات دلالية متماسكة.

    قاعدة الفصل:
      - السطر الفارغ = فاصل فقرة (الحالة الأساسية)
      - البادئة (سؤال: / السؤال:) = بداية فقرة جديدة مطلقاً
        حتى لو لم يسبقها سطر فارغ، لضمان عدم دمج سؤالين.

    السلوك عند غياب السطور الفارغة:
      - كل سطر يصبح فقرة مستقلة (توافق مع السلوك القديم تماماً)

    المخرجات:
      قائمة من النصوص، كل نص = فقرة مدمجة بمسافة واحدة بين أسطرها.
    """
    _QUESTION_PREFIXES = ("سؤال:", "السؤال:")

    paragraphs: list[str] = []
    current_lines: list[str] = []

    def _flush():
        text = " ".join(current_lines).strip()
        if text:
            paragraphs.append(text)
        current_lines.clear()

    try:
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            for raw_line in f:
                line = raw_line.rstrip("\r\n")

                # سطر فارغ → إغلاق الفقرة الحالية
                if not line.strip():
                    _flush()
                    continue

                stripped = line.strip()

                # بادئة سؤال جديد → أغلق الفقرة السابقة ثم ابدأ فقرة جديدة
                if any(stripped.startswith(p) for p in _QUESTION_PREFIXES):
                    _flush()

                current_lines.append(stripped)

        # الفقرة الأخيرة إن لم تنته بسطر فارغ
        _flush()

    except FileNotFoundError:
        pass

    return paragraphs
