# BWW Assistant Chatbot - PowerShell Startup
# تشغيل المشروع على PowerShell

Write-Host "🎯 BWW ASSISTANT CHATBOT - تشغيل PowerShell" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

# تعيين مسار Python
$env:PYTHONPATH = "."
Write-Host "✅ تم تعيين PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 بدء تشغيل المشروع..." -ForegroundColor Yellow
Write-Host "اضغط Ctrl+C للإيقاف" -ForegroundColor Yellow
Write-Host ""

try {
    # تشغيل المشروع
    python scripts/run.py
} catch {
    Write-Host "❌ خطأ في تشغيل التطبيق: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "👋 تم إيقاف التطبيق" -ForegroundColor Green