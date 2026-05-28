import sys
import os
import io
import csv
import time
from datetime import datetime

# لضمان توافق الترميز في الويندوز
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.physics.synchronize import synchronize
from src.physics.generator import Generator

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("="*60)
    print(" مرنان V5.1 - أداة التقييم البشري (Human Evaluation Tool)")
    print("="*60)
    
    print("\nجاري تحميل الفضاء اللغوي (Corpus)...")
    # نستخدم نصوصاً تجريبية لضمان وجود المفردات
    corpus = [
        "السلام عليكم ورحمة الله وبركاته.", 
        "الفيزياء هي علم دراسة الطبيعة.", 
        "الحروف العربية تحمل طاقة ومعاني عميقة.",
        "الصياد في البيت ينتظر الفجر.",
        "الليل طويل والنجوم ساطعة.",
        "العلم نور والجهل ظلام مدقع."
    ]
    
    vocab, K, syntax = synchronize(corpus, window=5)
    gen = Generator(vocab, K, beam_width=3, top_k=50, syntax_field=syntax)
    
    test_prompts = [
        ("السلام", "quantum", {}),
        ("الفيزياء هي", "quantum", {}),
        ("الصياد في", "standard", {}),
        ("الليل", "poetic", {'poetic_meter': 'tawil', 'poetic_rhyme': 'ة'})
    ]
    
    results_file = os.path.join(os.path.dirname(__file__), 'human_eval_results.csv')
    file_exists = os.path.isfile(results_file)
    
    with open(results_file, mode='a', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Prompt', 'Mode', 'Output', 'Coherence_Score', 'Syntax_Score', 'Aesthetic_Score', 'Comments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        print("\nتم التحميل. ستبدأ الآن جلسة التقييم.")
        print("المعايير (الدرجة من 0 إلى 5):")
        print("1. Coherence (الترابط الدلالي والقصدي)")
        print("2. Syntax (السلامة النحوية والصرفية)")
        print("3. Aesthetics (الجمالية والوزن إن وجد)")
        print("-" * 60)
        
        for prompt, mode, kwargs in test_prompts:
            print(f"\n[المدخل]: {prompt}")
            print(f"[الوضع]: {mode} | {kwargs}")
            print("جاري التوليد...")
            
            start_t = time.time()
            output = gen.generate(prompt, max_words=6, mode=mode, **kwargs)
            gen_time = time.time() - start_t
            
            print(f"\n[المخرج]: {prompt} {output}")
            print(f"(زمن التوليد: {gen_time:.2f} ثانية)")
            
            print("\nأدخل التقييمات (0-5):")
            try:
                coherence = input("الترابط (Coherence): ")
                syntax_score = input("النحو (Syntax): ")
                aesthetics = input("الجمالية (Aesthetics): ")
                comment = input("تعليق إضافي (اختياري): ")
            except KeyboardInterrupt:
                print("\nتم إيقاف التقييم.")
                break
                
            writer.writerow({
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Prompt': prompt,
                'Mode': mode,
                'Output': output,
                'Coherence_Score': coherence,
                'Syntax_Score': syntax_score,
                'Aesthetic_Score': aesthetics,
                'Comments': comment
            })
            print("-" * 60)
            
    print(f"\nتم حفظ النتائج بنجاح في: {results_file}")
    print("شكراً لتقييمك!")

if __name__ == '__main__':
    main()
