# BWW Assistant Chatbot - Linux/Mac Startup
# تشغيل المشروع على Linux/Mac

echo "🎯 BWW ASSISTANT CHATBOT - تشغيل Linux/Mac"
echo "============================================"
echo ""

# تعيين مسار Python
export PYTHONPATH=.
echo "✅ تم تعيين PYTHONPATH: $PYTHONPATH"

echo ""
echo "🚀 بدء تشغيل المشروع..."
echo "اضغط Ctrl+C للإيقاف"
echo ""

# تشغيل المشروع
python3 scripts/run.py

echo ""
echo "👋 تم إيقاف التطبيق"