#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""تنظيف مستند نصي ليصبح متوافقاً مع معمارية مرنان.

الاستخدام:
  python clean_corpus.py input.txt [-o output.txt] [--lang ar|en|both]

يقوم بـ:
  • إزالة Markdown بالكامل (عناوين، تنسيق، جداول، كود، روابط، صور)
  • إزالة HTML/XML tags
  • إزالة الروابط والـ URLs
  • إزالة الأحرف المتكررة والتشكيل والكشيدة
  • توحيد أشكال الحروف العربية (أ,إ,آ → ا | ة → ه | ى → ئ)
  • تقسيم النص الطويل إلى أسطر (جمل منفصلة)
  • إزالة الأسطر الفارغة المتتالية
"""
import re, os, sys, argparse
from typing import List

# ─── 1. تنظيف Markdown ───

_RE_MD_HEADER = re.compile(r'^#{1,6}\s*.*$', re.MULTILINE)
_RE_MD_TABLE = re.compile(r'^\|.*\|$', re.MULTILINE)
_RE_MD_TABLE_SEP = re.compile(r'^[\s|:\-]+$', re.MULTILINE)
_RE_MD_CODE_FENCE = re.compile(r'```[\s\S]*?```|~~~[\s\S]*?~~~', re.MULTILINE)
_RE_MD_INLINE_CODE = re.compile(r'`([^`]+)`')
_RE_MD_IMAGE = re.compile(r'!\[([^\]]*)\]\([^)]+\)')
_RE_MD_LINK = re.compile(r'\[([^\]]+)\]\([^)]+\)')
_RE_MD_BOLD_ITALIC = re.compile(r'\*{1,3}([^*]+)\*{1,3}')
_RE_MD_UNDERLINE_BOLD = re.compile(r'_{1,3}([^_]+)_{1,3}')
_RE_MD_STRIKETHROUGH = re.compile(r'~~(.*?)~~')
_RE_MD_HR = re.compile(r'^[\s]*[-*_]{3,}[\s]*$', re.MULTILINE)
_RE_MD_LIST = re.compile(r'^[\s]*(?:[-*+]|\d+[.)])\s+', re.MULTILINE)
_RE_MD_BLOCKQUOTE = re.compile(r'^>\s?', re.MULTILINE)

# ─── 2. تنظيف HTML ───
_RE_HTML_TAG = re.compile(r'<[^>]+>')
_RE_HTML_ENTITY = re.compile(r'&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;')

# ─── 3. URLs ───
_RE_URL = re.compile(r'https?://[^\s<>"\'\[\]]+|www\.[^\s<>"\'\[\]]+')

# ─── 4. أحرف عربية خاصة ───
_RE_TASHKEEL = re.compile(r'[\u064B-\u065F\u0670]')  # تشكيل (فتحة ضمة كسرة سكون شدّة...)
_RE_KASHIDA = re.compile(r'[\u0640]')                 # كشيدة (تطويل)
_RE_LONG_TATWEEL = re.compile(r'(.)\1{3,}')           # تكرار الحرف 4+ مرات

# أشكال موحّدة للحروف
_ARABIC_NORMALIZE = str.maketrans({
    '\u0622': '\u0627',  # آ → ا
    '\u0623': '\u0627',  # أ → ا
    '\u0625': '\u0627',  # إ → ا
    '\u0624': '\u0648',  # ؤ → و
    '\u0626': '\u064A',  # ئ → ي
    '\u0629': '\u0647',  # ة → ه
    '\u0649': '\u064A',  # ى → ي
})

# ─── 5. فواصل غير مرغوب فيها ───
_RE_PUNCT_MULTI = re.compile(r'[!?؟]{2,}')       # تكرار علامات التعجب والاستفهام
_RE_DOTS = re.compile(r'\.{3,}')                 # نقط متتالية
_RE_WHITESPACE = re.compile(r'[ \t]+')           # مسافات متتالية
_RE_EMPTY_LINES = re.compile(r'\n{3,}')          # أسطر فارغة متتالية
_RE_LINE_WS = re.compile(r'^\s+|\s+$', re.MULTILINE)  # فراغات في بداية/نهاية السطر

# أحرف غير عربية ولا إنجليزية (للإزالة الاختيارية)
_RE_NON_AR_EN = re.compile(
    r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF'
    r'\u0041-\u005A\u0061-\u007A\u0030-\u0039'
    r'\s\.\,\!\?\:\;\-\+\/\[\]\(\)\'\u2018\u2019\"\u201C\u201D\u060C\u061B\u061F]'
)


def strip_markdown(text: str) -> str:
    text = _RE_MD_CODE_FENCE.sub(' ', text)
    text = _RE_MD_IMAGE.sub(r'\1', text)
    text = _RE_MD_LINK.sub(r'\1', text)
    text = _RE_MD_HEADER.sub('', text)
    text = _RE_MD_TABLE.sub('', text)
    text = _RE_MD_TABLE_SEP.sub('', text)
    text = _RE_MD_HR.sub('', text)
    text = _RE_MD_BLOCKQUOTE.sub('', text)
    text = _RE_MD_LIST.sub('', text)
    text = _RE_MD_INLINE_CODE.sub(r'\1', text)
    text = _RE_MD_BOLD_ITALIC.sub(r'\1', text)
    text = _RE_MD_UNDERLINE_BOLD.sub(r'\1', text)
    text = _RE_MD_STRIKETHROUGH.sub(r'\1', text)
    return text


def strip_html(text: str) -> str:
    text = _RE_HTML_TAG.sub(' ', text)
    text = _RE_HTML_ENTITY.sub(' ', text)
    return text


def strip_urls(text: str) -> str:
    return _RE_URL.sub('', text)


def normalize_arabic(text: str) -> str:
    text = _RE_TASHKEEL.sub('', text)
    text = _RE_KASHIDA.sub('', text)
    text = text.translate(_ARABIC_NORMALIZE)
    text = _RE_LONG_TATWEEL.sub(r'\1', text)
    return text


def clean_special(text: str, keep_english: bool = True) -> str:
    text = _RE_PUNCT_MULTI.sub('!', text)
    text = _RE_DOTS.sub('.', text)
    if not keep_english:
        text = _RE_NON_AR_EN.sub(' ', text)
    return text


def split_sentences(text: str) -> List[str]:
    """تقسيم النص إلى جمل — كل جملة سطر مستقل."""
    # فواصل الجمل: نقطة، علامة استفهام، علامة تعجب، فاصلة منقوطة، سطر جديد
    lines = []
    for paragraph in text.split('\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        sentences = re.split(r'(?<=[.!?؟])\s+', paragraph)
        for s in sentences:
            s = s.strip()
            if s:
                lines.append(s)
    return lines


def clean_corpus(text: str, keep_english: bool = True,
                 max_line_len: int = 500,
                 min_line_len: int = 2) -> str:
    """تنظيف متكامل لنص أولي إلى كوربوس مرنان."""
    original_len = len(text)
    stats = {'bytes_in': original_len}

    # ترتيب مهم: إزالة Markdown و HTML و URLs قبل كل شيء
    text = strip_markdown(text)
    stats['after_md'] = len(text)

    text = strip_html(text)
    stats['after_html'] = len(text)

    text = strip_urls(text)
    stats['after_urls'] = len(text)

    # تطبيع العربية
    text = normalize_arabic(text)
    stats['after_norm'] = len(text)

    # إزالة أحرف خاصة
    text = clean_special(text, keep_english)
    stats['after_clean'] = len(text)

    # تحويل المسافات
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = _RE_LINE_WS.sub('', text)
    text = _RE_WHITESPACE.sub(' ', text)

    # تقسيم إلى جمل
    lines = split_sentences(text)

    # تصفية
    filtered = []
    for line in lines:
        if len(line) < min_line_len:
            continue
        if len(line) > max_line_len:
            # تقسيم الجمل الطويلة
            parts = re.split(r'(?<=[.!?؟،])\s*', line)
            for p in parts:
                p = p.strip()
                if len(p) >= min_line_len:
                    filtered.append(p)
        else:
            filtered.append(line)

    # إزالة الأسطر المتطابقة والفراغات المتتالية
    final = []
    seen = set()
    for line in filtered:
        if line not in seen:
            seen.add(line)
            final.append(line)

    result = '\n'.join(final)
    stats['bytes_out'] = len(result)
    stats['lines'] = len(final)
    stats['removed_pct'] = round((1 - len(result) / max(original_len, 1)) * 100, 1)

    return result, stats


# ─── 6. كشف وإصلاح Mojibake (ترميز معكوس) ───
# الأنماط المعروفة للـ Mojibake العربي:
# UTF-8 Arabic bytes (0xD8-0xDB) مقروءة كـ Latin-1 → تنتج أحرفاً مثل Ø (0xD8), Ù (0xD9), Û (0xDB)
_MOJIBAKE_PATTERN = re.compile(r'[\xc3-\xdb][\x80-\xbf]')


def read_with_encoding(path: str) -> str:
    """يقرأ ملفاً بأي ترميز ويعيد نصاً UTF-8 صحيحاً.

    يكشف Mojibake: إذا قرأنا UTF-8 كـ Latin-1 نحصل على
    Ù‡ÙŠ (هي), Ø§Ù„ (ال) — نصلحها بـ encode(latin1)→decode(utf8).
    """
    with open(path, 'rb') as f:
        raw = f.read()

    def has_arabic(s: str) -> bool:
        return any('\u0600' <= c <= '\u06FF' for c in s)

    def has_mojibake(s: str) -> bool:
        """يبحث عن أنماط Mojibake المعروفة للعربية."""
        return bool(_MOJIBAKE_PATTERN.search(s))

    def repair(s: str) -> str:
        try:
            return s.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return s

    # 1. UTF-8 أولاً
    try:
        text_utf8 = raw.decode('utf-8')
        if has_arabic(text_utf8) and not has_mojibake(text_utf8):
            return text_utf8  # سليم
        if has_mojibake(text_utf8):
            repaired = repair(text_utf8)
            if has_arabic(repaired):
                print('  [تنبيه] تم إصلاح Mojibake (UTF-8→Latin-1→UTF-8)')
                return repaired
        # لا عربي ولا Mojibake — قد يكون إنكليزياً صرفاً
        return text_utf8
    except UnicodeDecodeError:
        pass

    # 2. جرب ترميزات عربية
    for enc in ('windows-1256', 'cp1256', 'iso-8859-6'):
        try:
            return raw.decode(enc).encode('utf-8').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue

    # 3. Latin-1 مع إصلاح
    try:
        text_latin = raw.decode('latin-1')
        if has_mojibake(text_latin):
            repaired = repair(text_latin)
            if has_arabic(repaired):
                print('  [تنبيه] تم إصلاح Mojibake (Latin-1→UTF-8)')
                return repaired
        return text_latin
    except UnicodeDecodeError:
        pass

    # 4. Fallback
    print('  [تحذير] ترميز غير معروف — أحرف تالفة قد تبقى')
    return raw.decode('utf-8', errors='replace')



def main():
    parser = argparse.ArgumentParser(
        description='تنظيف مستند نصي لمعمارية مرنان')
    parser.add_argument('input', help='مسار الملف المدخل')
    parser.add_argument('-o', '--output', help='مسار المخرج (اختياري)')
    parser.add_argument('--lang', choices=['ar', 'en', 'both'], default='both',
                        help='اللغة: ar (عربي فقط), en (إنكليزي فقط), both (الاثنان)')
    parser.add_argument('--max-line', type=int, default=500,
                        help='الحد الأقصى لطول السطر (افتراضي: 500)')
    parser.add_argument('--min-line', type=int, default=2,
                        help='الحد الأدنى لطول السطر (افتراضي: 2)')
    parser.add_argument('--fix-encoding', action='store_true', default=True,
                        help='كشف وإصلاح Mojibake تلقائياً (افتراضي: نعم)')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'خطأ: الملف {args.input} غير موجود')
        sys.exit(1)

    raw = read_with_encoding(args.input) if args.fix_encoding else open(args.input, encoding='utf-8', errors='replace').read()

    keep_english = args.lang in ('en', 'both')
    result, stats = clean_corpus(
        raw,
        keep_english=keep_english,
        max_line_len=args.max_line,
        min_line_len=args.min_line,
    )

    if args.output:
        out_path = args.output
    else:
        base, ext = os.path.splitext(args.input)
        out_path = f'{base}_cleaned{ext}'

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f'تمت المعالجة: {args.input}')
    print(f'  حجم المدخل:      {stats["bytes_in"]:,} بايت')
    print(f'  حجم المخرج:      {stats["bytes_out"]:,} بايت')
    print(f'  نسبة الإزالة:    {stats["removed_pct"]}%')
    print(f'  عدد الأسطر:      {stats["lines"]:,}')
    print(f'  المخرج:          {out_path}')
    print()
    print(f'المراحل:')
    print(f'  بعد Markdown:     {stats["after_md"]:,} بايت')
    print(f'  بعد HTML:         {stats["after_html"]:,} بايت')
    print(f'  بعد URLs:         {stats["after_urls"]:,} بايت')
    print(f'  بعد التطبيع:     {stats["after_norm"]:,} بايت')
    print(f'  بعد التنظيف:     {stats["after_clean"]:,} بايت')


if __name__ == '__main__':
    main()
