import os
import sys
import importlib.util
import numpy as np
from scipy import sparse
from prds.lexicon import DynamicLexicon
from prds.coupling import PhaseCoupling

def save_model_to_py(file_path, lexicon, coupling):
    """
    حفظ نموذج مِرنان بالكامل كملف كود بايثون (.py) متطور وتوسعي
    يحاكي أسلوب القلم في حفظ الأوزان والمعاجم برمجياً.
    """
    # تحويل المصفوفات إلى تنسيق COO لاستخلاص الإحداثيات والقيم
    C_coo = coupling.C.tocoo()
    K_coo = coupling.K.tocoo()
    T_coo = coupling.T.tocoo()

    # كتابة ملف البايثون
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("# نموذج مِرنان اللغوي الفيزيائي - كود الأوزان الجيني المطور\n")
        f.write("# هذا الملف تم توليده تلقائياً ككود بايثون قابل للتطوير الديناميكي.\n\n")
        f.write("import numpy as np\n\n")
        
        # حفظ المتغيرات الأساسية للموديل
        f.write(f"vocab_size = {lexicon.get_vocab_size()}\n")
        f.write(f"num_docs = {lexicon.num_docs}\n")
        f.write(f"omega_range = {lexicon.omega_range}\n")
        f.write(f"eta = {coupling.eta}\n")
        f.write(f"max_weight = {coupling.max_weight}\n\n")

        # حفظ المعاجم والخرائط اللغوية
        f.write("# المعاجم والخصائص اللغوية\n")
        f.write(f"vocab = {repr(lexicon.vocab)}\n\n")
        f.write(f"id2word = {repr(lexicon.id2word)}\n\n")
        
        # تحويل المعاجم التلقائية (defaultdict) لخرائط عادية للحفظ
        f.write(f"word_counts = {repr(dict(lexicon.word_counts))}\n\n")
        f.write(f"doc_counts = {repr(dict(lexicon.doc_counts))}\n\n")
        
        # حفظ الترددات الذاتية كقائمة
        f.write(f"omega = {repr(lexicon.omega.tolist())}\n\n")
        
        # حفظ الكلمات المثبتة والجذور الصرفية
        f.write(f"pinned_words = {repr(list(lexicon.pinned_words))}\n\n")
        f.write(f"word_roots = {repr(lexicon.word_roots)}\n\n")
        
        # تحويل root2words العادي
        f.write(f"root2words = {repr(dict(lexicon.root2words))}\n\n")
        f.write(f"arramooz_dict = {repr(lexicon.arramooz_dict)}\n\n")

        # حفظ المصفوفات المتفرقة (Sparse Matrices) كإحداثيات COO
        f.write("# مصفوفات الاقتران الطورية وقيم الـ COO\n")
        f.write(f"C_rows = np.array({C_coo.row.tolist()}, dtype=np.int32)\n")
        f.write(f"C_cols = np.array({C_coo.col.tolist()}, dtype=np.int32)\n")
        f.write(f"C_data = np.array({C_coo.data.tolist()}, dtype=np.float32)\n\n")

        f.write(f"K_rows = np.array({K_coo.row.tolist()}, dtype=np.int32)\n")
        f.write(f"K_cols = np.array({K_coo.col.tolist()}, dtype=np.int32)\n")
        f.write(f"K_data = np.array({K_coo.data.tolist()}, dtype=np.float32)\n\n")

        f.write(f"T_rows = np.array({T_coo.row.tolist()}, dtype=np.int32)\n")
        f.write(f"T_cols = np.array({T_coo.col.tolist()}, dtype=np.int32)\n")
        f.write(f"T_data = np.array({T_coo.data.tolist()}, dtype=np.float32)\n\n")

        # دالة حقن الأوزان في كائن الموديل
        f.write("def inject_weights(lexicon_obj, coupling_obj):\n")
        f.write("    from scipy import sparse\n")
        f.write("    print('[EVOLUTION] Injecting dynamic weight layers into Mirnan...')\n")
        f.write("    lexicon_obj.vocab = vocab\n")
        f.write("    lexicon_obj.id2word = id2word\n")
        f.write("    from collections import defaultdict\n")
        f.write("    lexicon_obj.word_counts.update(word_counts)\n")
        f.write("    lexicon_obj.doc_counts.update(doc_counts)\n")
        f.write("    lexicon_obj.omega = np.array(omega, dtype=np.float64)\n")
        f.write("    lexicon_obj.num_docs = num_docs\n")
        f.write("    lexicon_obj.pinned_words = set(pinned_words)\n")
        f.write("    lexicon_obj.word_roots = word_roots\n")
        f.write("    for r, words in root2words.items():\n")
        f.write("        lexicon_obj.root2words[r] = words\n")
        f.write("    lexicon_obj.arramooz_dict = arramooz_dict\n\n")
        
        f.write("    coupling_obj.vocab_size = vocab_size\n")
        f.write("    coupling_obj.C = sparse.csr_matrix((C_data, (C_rows, C_cols)), shape=(vocab_size, vocab_size))\n")
        f.write("    coupling_obj.K = sparse.csr_matrix((K_data, (K_rows, K_cols)), shape=(vocab_size, vocab_size))\n")
        f.write("    coupling_obj.T = sparse.csr_matrix((T_data, (T_rows, T_cols)), shape=(vocab_size, vocab_size))\n")
        f.write("    print('[EVOLUTION] Successful injection: Mirnan is fully aligned.')\n")

    print(f"[EVOLUTION] Model saved as Python code at: {file_path}")

def load_model_from_py(file_path):
    """
    تحميل نموذج مِرنان برمجياً وديناميكياً من ملف كود بايثون (.py).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"تعذر العثور على ملف أوزان مِرنان في: {file_path}")

    # استيراد ملف الكود ديناميكياً لتفادي OOV وتعارضات المسارات
    module_name = "mirnan_brain_weights"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # بناء الكائنات الفارغة وحقن الأوزان من الموديول المستورد
    lexicon = DynamicLexicon(omega_range=module.omega_range)
    coupling = PhaseCoupling(lexicon, eta=module.eta, max_weight=module.max_weight)
    
    module.inject_weights(lexicon, coupling)
    
    return lexicon, coupling
