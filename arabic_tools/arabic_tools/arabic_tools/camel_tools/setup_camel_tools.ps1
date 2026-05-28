# سكريبت إعداد camel-tools المحلي
# Setup Local Camel-Tools with Models

Write-Host "🐪 إعداد camel-tools المحلي للمشروع السيادي..." -ForegroundColor Cyan
Write-Host ("=" * 60)

$ExternalDir = "C:\Users\allmy\Desktop\Rasimiyyat_Sovereign_Project\external"
$CamelToolsDir = Join-Path $ExternalDir "camel_tools"
$DataDir = Join-Path $CamelToolsDir "data"

# التحقق من وجود camel_tools
if (-not (Test-Path $CamelToolsDir)) {
    Write-Host "❌ لم يتم العثور على مجلد camel_tools في: $CamelToolsDir" -ForegroundColor Red
    Write-Host "يرجى تشغيل السكريبت الرئيسي أولاً لنقل camel-tools" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ تم العثور على camel_tools في: $CamelToolsDir" -ForegroundColor Green

# التحقق من مجلد البيانات
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    Write-Host "📁 تم إنشاء مجلد البيانات: $DataDir" -ForegroundColor Green
}

# التحقق من حجم البيانات الحالي
$DataSize = 0
if (Test-Path $DataDir) {
    $DataSize = (Get-ChildItem $DataDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $DataSizeMB = [math]::Round($DataSize / 1MB, 2)
    Write-Host "📊 حجم البيانات الحالي: $DataSizeMB MB" -ForegroundColor Yellow
}

# تحميل النماذج
Write-Host "`n📥 تحميل نماذج camel-tools إلى المسار المحلي..." -ForegroundColor Cyan
Write-Host "قد يستغرق هذا بعض الوقت حسب سرعة الإنترنت..." -ForegroundColor Yellow

# إضافة المسار المحلي
$env:PYTHONPATH = $ExternalDir

try {
    # محاولة تحميل النماذج باستخدام Python
    $PythonScript = @"
import sys
import os

# Add external directory to path
sys.path.insert(0, r'$ExternalDir')

# Download models to local directory
os.environ['CAMEL_TOOLS_DATA'] = r'$DataDir'

from camel_tools.scripts.download_models import download_all
download_all(data_dir=r'$DataDir')
print('✅ تم تحميل النماذج بنجاح!')
"@
    
    $PythonScript | Out-File -FilePath "temp_download.py" -Encoding UTF8
    python temp_download.py
    Remove-Item "temp_download.py" -Force -ErrorAction SilentlyContinue
    
    Write-Host "`n✅ تم تحميل النماذج بنجاح!" -ForegroundColor Green
}
catch {
    Write-Host "`n⚠️ فشل في تحميل النماذج تلقائياً" -ForegroundColor Yellow
    Write-Host "يرجى تشغيل الأمر يدوياً:" -ForegroundColor Yellow
    Write-Host "  python -m camel_tools.scripts.download_models -d `"$DataDir`"" -ForegroundColor White
}

# التحقق النهائي
$FinalSize = 0
if (Test-Path $DataDir) {
    $FinalSize = (Get-ChildItem $DataDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
    $FinalSizeMB = [math]::Round($FinalSize / 1MB, 2)
    Write-Host "`n📊 حجم البيانات النهائي: $FinalSizeMB MB" -ForegroundColor Green
}

if ($FinalSize -gt 1MB) {
    Write-Host "`n🎉 camel-tools المحلي جاهز للاستخدام!" -ForegroundColor Green
    Write-Host "المسار: $CamelToolsDir" -ForegroundColor Cyan
} else {
    Write-Host "`n⚠️ بيانات camel-tools قد تكون ناقصة" -ForegroundColor Yellow
    Write-Host "تأكد من اتصالك بالإنترنت وأعد المحاولة" -ForegroundColor Yellow
}

Write-Host "`n📝 ملاحظة:" -ForegroundColor Cyan
Write-Host "  - سيتم استخدام camel-tools المحلي تلقائياً عند وجوده" -ForegroundColor Gray
Write-Host "  - في حال عدم الوجود، سيعود النظام للطرق الهجينة (Heuristics)" -ForegroundColor Gray
