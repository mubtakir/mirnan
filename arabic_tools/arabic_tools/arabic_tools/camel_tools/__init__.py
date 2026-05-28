"""
الحزم الخارجية المستقلة (External Libraries)
==========================================
يحتوي على نسخ مستقلة من المكتبات الخارجية مثل camel-tools
"""

import sys
import os

# إضافة مسار المكتبات الخارجية في بداية المسار لضمان الأولوية
EXTERNAL_DIR = os.path.dirname(os.path.abspath(__file__))

# نقل المسارات العامة مؤقتاً لضمان استيراد النسخة المحلية أولاً
_system_paths = [p for p in sys.path if p.startswith(sys.prefix) or 'site-packages' in p]
_other_paths = [p for p in sys.path if p not in _system_paths]

# إعادة ترتيب المسارات: المجلد المحلي أولاً، ثم المسارات الأخرى
sys.path = [EXTERNAL_DIR] + _other_paths + _system_paths

# التحقق من توفر camel-tools المحلي
try:
    import camel_tools
    CAMEL_TOOLS_AVAILABLE = True
    CAMEL_TOOLS_PATH = os.path.dirname(camel_tools.__file__)
    # التأكد من أنه النسخة المحلية
    if not CAMEL_TOOLS_PATH.startswith(EXTERNAL_DIR):
        CAMEL_TOOLS_AVAILABLE = False
        camel_tools = None
except ImportError:
    CAMEL_TOOLS_AVAILABLE = False
    CAMEL_TOOLS_PATH = None

def ensure_camel_tools():
    """تأكيد توفر camel-tools المحلي"""
    if not CAMEL_TOOLS_AVAILABLE:
        raise ImportError(
            "camel-tools غير متوفر في المجلد المحلي.\n"
            f"تأكد من وجوده في: {os.path.join(EXTERNAL_DIR, 'camel_tools')}\n"
            "أو قم بتشغيل: python -m camel_tools.scripts.download_models"
        )
    return camel_tools

__all__ = ['CAMEL_TOOLS_AVAILABLE', 'CAMEL_TOOLS_PATH', 'ensure_camel_tools']
