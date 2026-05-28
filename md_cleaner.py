#!/usr/bin/env python3
"""
Markdown Cleaner Script
ينظف ملفات النصوص من علامات ورموز مارك داون
يدعم العمل مع ملف واحد أو مجلد كامل
"""

import os
import re
import argparse
from pathlib import Path
import shutil

class MarkdownCleaner:
    def __init__(self):
        # أنماط رموز مارك داون للإزالة
        self.patterns = [
            # العناوين
            (r'^#{1,6}\s+', ''),  # # عنوان
            (r'^(.+)\n[=]+\s*$', r'\1'),  # عنوان مع =
            (r'^(.+)\n[-]+\s*$', r'\1'),  # عنوان مع -
            
            # التنسيق
            (r'\*\*(.+?)\*\*', r'\1'),  # **غامق**
            (r'__(.+?)__', r'\1'),  # __غامق__
            (r'\*(.+?)\*', r'\1'),  # *مائل*
            (r'_(.+?)_', r'\1'),  # _مائل_
            (r'~~(.+?)~~', r'\1'),  # ~~مشطوب~~
            
            # الروابط
            (r'\[([^\]]+)\]\([^\)]+\)', r'\1'),  # [نص](رابط)
            (r'\[([^\]]+)\]\[[^\]]*\]', r'\1'),  # [نص][مرجع]
            
            # الصور
            (r'!\[([^\]]*)\]\([^\)]+\)', r'\1'),  # ![وصف](رابط)
            
            # القوائم
            (r'^\s*[-*+]\s+', ''),  # - قائمة غير مرتبة
            (r'^\s*\d+[.)]\s+', ''),  # 1. قائمة مرتبة
            
            # الاقتباسات
            (r'^\s*>\s+', ''),  # > اقتباس
            
            # الخطوط الأفقية
            (r'^[-*_]{3,}\s*$', ''),  # --- أو ***
            
            # التعليمات البرمجية
            (r'`([^`]+)`', r'\1'),  # `كود`
            (r'```[\s\S]*?```', ''),  # كتلة كود
            
            # رموز HTML الشائعة
            (r'<br\s*/?>', '\n'),  # <br>
            (r'<[^>]+>', ''),  # أي وسم HTML
            
            # أحرف الهروب
            (r'\\([\\`*_{}\[\]()#+\-.!|])', r'\1'),
            
            # جداول مارك داون (تبسيط)
            (r'^\|(.+)\|\s*$', r'\1'),  # صفوف الجدول
            (r'^\|[-:\s|]+\|\s*$', ''),  # فواصل الجدول
            
            # المسافات الزائدة
            (r'\n{3,}', '\n\n'),  # أسطر فارغة متعددة
            (r' {2,}', ' '),  # مسافات متعددة
        ]
    
    def clean_text(self, text):
        """تنظيف النص من رموز مارك داون"""
        cleaned_text = text
        
        for pattern, replacement in self.patterns:
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.MULTILINE)
        
        # تنظيف إضافي للأسطر الفارغة
        cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    def process_file(self, file_path, backup=True):
        """معالجة ملف واحد"""
        try:
            file_path = Path(file_path)
            
            # قراءة الملف
            with open(file_path, 'r', encoding='utf-8') as f:
                original_text = f.read()
            
            # تنظيف النص
            cleaned_text = self.clean_text(original_text)
            
            # إنشاء نسخة احتياطية إذا طلب
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                shutil.copy2(file_path, backup_path)
                print(f"✓ تم إنشاء نسخة احتياطية: {backup_path.name}")
            
            # حفظ الملف المنظف
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            print(f"✓ تم تنظيف: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"✗ خطأ في معالجة {file_path.name}: {str(e)}")
            return False
    
    def process_directory(self, dir_path, extensions=None, backup=True):
        """معالجة جميع الملفات النصية في مجلد"""
        if extensions is None:
            extensions = {'.txt', '.md', '.markdown', '.text', '.rst'}
        
        dir_path = Path(dir_path)
        processed = 0
        failed = 0
        
        for ext in extensions:
            for file_path in dir_path.glob(f'*{ext}'):
                if self.process_file(file_path, backup):
                    processed += 1
                else:
                    failed += 1
        
        # البحث في المجلدات الفرعية
        for subdir in dir_path.iterdir():
            if subdir.is_dir():
                p, f = self.process_directory(subdir, extensions, backup)
                processed += p
                failed += f
        
        return processed, failed

def main():
    parser = argparse.ArgumentParser(
        description='منظف ملفات مارك داون - يزيل رموز وعلامات مارك داون من الملفات النصية',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
أمثلة:
  python md_cleaner.py file.txt                    # تنظيف ملف واحد
  python md_cleaner.py ./documents                 # تنظيف كل الملفات في مجلد
  python md_cleaner.py file.txt --no-backup        # بدون نسخة احتياطية
  python md_cleaner.py ./docs --ext .txt .md       # تحديد الامتدادات
        '''
    )
    
    parser.add_argument(
        'path',
        help='مسار الملف أو المجلد المراد تنظيفه'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='عدم إنشاء نسخ احتياطية'
    )
    
    parser.add_argument(
        '--ext',
        nargs='+',
        default=['.txt', '.md', '.markdown', '.text', '.rst'],
        help='امتدادات الملفات للمعالجة (افتراضي: .txt .md .markdown .text .rst)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='معاينة التغييرات فقط بدون حفظ'
    )
    
    args = parser.parse_args()
    
    # إنشاء المنظف
    cleaner = MarkdownCleaner()
    
    # التحقق من المسار
    path = Path(args.path)
    if not path.exists():
        print(f"✗ المسار غير موجود: {args.path}")
        return
    
    # معالجة ملف واحد
    if path.is_file():
        if args.dry_run:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            cleaned = cleaner.clean_text(text)
            print("=== معاينة النص المنظف ===")
            print(cleaned[:500] + "..." if len(cleaned) > 500 else cleaned)
        else:
            cleaner.process_file(path, backup=not args.no_backup)
    
    # معالجة مجلد
    elif path.is_dir():
        if args.dry_run:
            print("=== وضع المعاينة - لن يتم تعديل أي ملفات ===")
            for ext in args.ext:
                for file_path in path.glob(f'*{ext}'):
                    print(f"سيتم معالجة: {file_path.name}")
        else:
            extensions = set(args.ext)
            print(f"بدء تنظيف الملفات في: {path}")
            print(f"الامتدادات المستهدفة: {', '.join(extensions)}")
            print("-" * 50)
            
            processed, failed = cleaner.process_directory(
                path, 
                extensions, 
                backup=not args.no_backup
            )
            
            print("-" * 50)
            print(f"✓ تمت معالجة {processed} ملفات بنجاح")
            if failed > 0:
                print(f"✗ فشلت معالجة {failed} ملفات")

if __name__ == "__main__":
    main()