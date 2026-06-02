#!/bin/bash
# تنظيف حالة التدريب — يحذف المخابئ المؤقتة فقط
# Matrix K (K_sem.npz, K_syn.npz, etc.) تبقى كما هي

echo "تنظيف مخابئ مرنان المؤقتة..."

# مخبأ المتجهات الطورية — يتولد عند أول تشغيل
rm -f model/_all_pv_cache.npy
echo "  ✓ حذف: model/_all_pv_cache.npy"

# مخبأ القاعدة الهولوغرافية — سيبني من الحقائق المنسقة
rm -f data/holographic_kb.npz
echo "  ✓ حذف: data/holographic_kb.npz"

# مخابئ طيفية (Spectra caches)
rm -f model/contextual_spectra.npy
rm -f model/dialogue_spectra.npy
rm -f data/gss_dict.npy
rm -f data/gss_ground.npy
rm -f data/spectral_gss_dict.npy
rm -f data/spectral_gss_ground.npy
echo "  ✓ حذف: spectral caches"

# أي ملفات __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "  ✓ حذف: __pycache__"

echo ""
echo "تم. عند التشغيل التالي، سيبني مرنان المخابئ تلقائياً."
echo "مصفوفات K الأساسية باقية:"
ls -la model/K_*.npz 2>/dev/null
