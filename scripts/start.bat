@echo off
REM BWW Assistant Chatbot - Windows Startup
REM تشغيل المشروع على Windows

echo 🎯 BWW ASSISTANT CHATBOT - تشغيل Windows
echo ============================================
echo.

REM تعيين مسار Python
set PYTHONPATH=.
echo ✅ تم تعيين PYTHONPATH: %PYTHONPATH%

echo.
echo 🚀 بدء تشغيل المشروع...
echo اضغط Ctrl+C للإيقاف
echo.

REM تشغيل المشروع
python scripts/run.py

echo.
echo 👋 تم إيقاف التطبيق
pause