# External library without type stubs - using pyright directives for proper type checking
# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportUnknownVariableType=false
import logging
from typing import Optional, Dict, Any, List
from config.settings import settings
from app.services.core.base_service import AIService as BaseAIService

logger = logging.getLogger(__name__)

gemini_available = False

# Runtime imports - google.generativeai doesn't have type stubs
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    gemini_available = True
except ImportError as import_error:
    logger.info(f"Gemini package not available: {import_error}")
    # Define fallback types when package not available
    genai = None
    HarmCategory = None
    HarmBlockThreshold = None


class GeminiService(BaseAIService):
    """
    Advanced Gemini AI service with multimodal support
    Supports: Text, Images, Audio → Text responses
    """

    def __init__(self) -> None:
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY

        # Model configurations for different use cases
        self.models: Dict[str, Any] = {
            'multimodal': None,      # For images + audio + text
            'text_fast': None,       # For text-only (Gemma)
            'text_quality': None,    # For high-quality text
        }

        self._initialize_models()
        # Initialize the service
        self.initialize()

    def _initialize_models(self) -> None:
        """Initialize multiple models for different use cases"""
        if not gemini_available or genai is None:
            # Suppress warning on first initialization only
            if not hasattr(self, '_warning_shown'):
                logger.info("Gemini AI service not available - using fallback responses")
                self._warning_shown = True
            return

        # Type narrowing: assert genai is not None after availability check
        assert genai is not None, "genai should be available after gemini_available check"
        assert HarmCategory is not None, "HarmCategory should be available"
        assert HarmBlockThreshold is not None, "HarmBlockThreshold should be available"

        try:
            genai.configure(api_key=self.api_key)

            # Multimodal model (images + audio + text)
            try:
                self.models['multimodal'] = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Multimodal model initialized: gemini-2.5-flash")
            except Exception as e:
                logger.warning(f"Failed to initialize multimodal model: {e}")

            # Fast text-only model (Gemma - أسرع وأرخص للنصوص)
            try:
                self.models['text_fast'] = genai.GenerativeModel('gemma-3-27b-it')
                logger.info("✅ Fast text model initialized: gemma-3-27b-it")
            except Exception:
                logger.warning("Gemma not available, using gemini-2.5-flash-lite as fallback")
                try:
                    self.models['text_fast'] = genai.GenerativeModel('gemini-2.5-flash-lite')
                    logger.info("✅ Fast text fallback: gemini-2.5-flash-lite")
                except Exception as fallback_error:
                    logger.error(f"Failed to initialize fast text fallback: {fallback_error}")

            # High-quality text model
            try:
                self.models['text_quality'] = genai.GenerativeModel('gemini-2.5-pro')
                logger.info("✅ Quality text model initialized: gemini-2.5-pro")
            except Exception:
                # Fallback to flash if pro not available
                self.models['text_quality'] = self.models['multimodal']

        except Exception as e:
            logger.error(f"Failed to initialize Gemini models: {e}")
            self.models = {'multimodal': None, 'text_fast': None, 'text_quality': None}

    def generate_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,  # Changed from user_context
        media_files: Optional[List[Dict[str, Any]]] = None,
        use_quality_model: bool = False
    ) -> str:
        """
        Generate AI response using Gemini (supports multimodal inputs)

        Args:
            message: User message text
            context: Additional context about the user (renamed from user_context)
            media_files: List of media files [{'type': 'image|audio', 'data': bytes|path, 'mime_type': str}]
            use_quality_model: Use high-quality model for complex queries

        Returns:
            Generated text response
        """
        if not gemini_available:
            logger.warning("Gemini not available, using fallback response")
            return self._fallback_response(message)

        try:
            # Determine which model to use
            if media_files and len(media_files) > 0:
                # Has images/audio → use multimodal model
                model = self.models['multimodal']
                model_name = "gemini-2.5-flash (multimodal)"

                if not model:
                    logger.error("Multimodal model not available")
                    return self._fallback_response(message)

                return self._generate_multimodal_response(message, context, media_files, model)

            else:
                # Text-only → use fast Gemma model or quality model
                if use_quality_model and self.models['text_quality']:
                    model = self.models['text_quality']
                    model_name = "gemini-2.5-pro (quality)"
                elif self.models['text_fast']:
                    model = self.models['text_fast']
                    model_name = "gemma-3-27b-it (fast)"
                else:
                    model = self.models['multimodal']
                    model_name = "gemini-2.5-flash (fallback)"

                if not model:
                    return self._fallback_response(message)

                return self._generate_text_response(message, context, model, model_name)

        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return self._fallback_response(message)

    def _generate_text_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]],  # Changed from user_context
        model: Any,
        model_name: str
    ) -> str:
        """Generate text-only response"""
        try:
            # Build context for the AI
            ai_context = self._build_context(context)

            # Create prompt optimized for fashion retail
            prompt = f"""You are Bww-Assistant, a friendly AI shopping assistant for BWW Store - a leading fashion retailer in Egypt specializing in men's, women's, and kids' fashion.

User Context: {ai_context}
User Message: {message}

Guidelines:
• Match the user's language (Arabic/English) automatically
• Be conversational, helpful, and enthusiastic about fashion
• Use emojis naturally (1-2 per response) 🛍️ 👕 👗 👟
• For product inquiries: Offer to search our catalog
• For price/availability: Explain we have real-time search
• Build rapport - ask follow-up questions when relevant
• Keep responses concise (2-3 sentences max)
• Professional yet warm tone

Respond naturally:"""

            # Type narrowing for external library types
            assert HarmCategory is not None and HarmBlockThreshold is not None

            # Generate response
            response = model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            if response and response.text:
                logger.info(f"✅ Response generated using: {model_name}")
                return response.text.strip()
            else:
                logger.warning(f"Empty response from {model_name}")
                return self._fallback_response(message)

        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            return self._fallback_response(message)

    def _generate_multimodal_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]],  # Changed from user_context
        media_files: List[Dict[str, Any]],
        model: Any
    ) -> str:
        """Generate response with images/audio input"""
        try:
            # Build context
            ai_context = self._build_context(context)

            # Prepare content parts
            content_parts: List[Any] = []

            # Add media files
            for media in media_files:
                media_type = media.get('type', 'unknown')
                mime_type = media.get('mime_type', 'application/octet-stream')

                if media_type == 'image':
                    # Image input
                    if 'data' in media:
                        # Raw bytes
                        content_parts.append({
                            'mime_type': mime_type,
                            'data': media['data']
                        })
                    elif 'path' in media:
                        # File path
                        with open(media['path'], 'rb') as f:
                            content_parts.append({
                                'mime_type': mime_type,
                                'data': f.read()
                            })

                    logger.info(f"📷 Added image input ({mime_type})")

                elif media_type == 'audio':
                    # Audio input
                    if 'data' in media:
                        content_parts.append({
                            'mime_type': mime_type,
                            'data': media['data']
                        })
                    elif 'path' in media:
                        with open(media['path'], 'rb') as f:
                            content_parts.append({
                                'mime_type': mime_type,
                                'data': f.read()
                            })

                    logger.info(f"🎤 Added audio input ({mime_type})")

            # Add text prompt
            prompt = f"""You are Bww-Assistant analyzing media from a customer.

User Context: {ai_context}
User Message: {message}

Instructions:
• Analyze any images or audio provided
• For images: Describe the fashion items you see (style, color, type)
• For audio: Transcribe and respond to the spoken message
• Match the user's language (Arabic/English)
• Be helpful and conversational
• Use emojis naturally 🛍️ 👕 📷 🎤
• Keep responses concise (2-3 sentences)

Respond naturally:"""

            content_parts.append(prompt)

            # Type narrowing for external library types
            assert HarmCategory is not None and HarmBlockThreshold is not None

            # Generate response
            response = model.generate_content(
                content_parts,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            if response and response.text:
                logger.info(f"✅ Multimodal response generated ({len(media_files)} media files)")
                return response.text.strip()
            else:
                logger.warning("Empty multimodal response")
                return "عذراً، لم أتمكن من معالجة الوسائط المرسلة. يرجى المحاولة مرة أخرى."

        except Exception as e:
            logger.error(f"Error in multimodal generation: {e}")
            return f"عذراً، حدث خطأ في معالجة الصورة/الصوت: {str(e)}"

    def _build_context(self, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Build context string for the AI"""
        if not user_context:
            return "No additional context available"

        context_parts: List[str] = []

        if user_context.get('lead_stage'):
            context_parts.append(f"Lead stage: {user_context['lead_stage']}")

        if user_context.get('customer_type'):
            context_parts.append(f"Customer type: {user_context['customer_type']}")

        if user_context.get('customer_label'):
            context_parts.append(f"Customer label: {user_context['customer_label']}")

        if user_context.get('message_count', 0) > 0:
            context_parts.append(f"Previous messages: {user_context['message_count']}")

        return "; ".join(context_parts) if context_parts else "New customer"

    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect user intent from message

        Returns:
            {
                'intent': str,  # greeting, product_search, price_inquiry, etc.
                'confidence': float,  # 0.0 to 1.0
                'entities': dict  # extracted entities
            }
        """
        message_lower = message.lower()

        # Greeting intent
        if any(word in message_lower for word in ['مرحبا', 'هلا', 'السلام', 'أهلا', 'صباح', 'مساء', 'hello', 'hi', 'hey']):
            return {
                'intent': 'greeting',
                'confidence': 0.95,
                'entities': {}
            }

        # Product search intent
        if any(word in message_lower for word in ['منتج', 'فستان', 'قميص', 'حذاء', 'ملابس', 'product', 'dress', 'shirt', 'shoes']):
            return {
                'intent': 'product_search',
                'confidence': 0.90,
                'entities': {'product_type': message}
            }

        # Price inquiry intent
        if any(word in message_lower for word in ['سعر', 'price', 'كام', 'كم', 'how much', 'cost']):
            return {
                'intent': 'price_inquiry',
                'confidence': 0.92,
                'entities': {}
            }

        # Help request intent
        if any(word in message_lower for word in ['مساعدة', 'ساعد', 'help', 'assist', 'support']):
            return {
                'intent': 'help_request',
                'confidence': 0.88,
                'entities': {}
            }

        # Default: general inquiry
        return {
            'intent': 'general_inquiry',
            'confidence': 0.70,
            'entities': {}
        }

    def generate_fallback_response(self, message: str) -> str:
        """Public method for generating fallback responses"""
        return self._fallback_response(message)

    def _fallback_response(self, message: str) -> str:
        """Fallback response when Gemini is not available"""
        message_lower = message.lower()

        # Arabic greetings
        if any(word in message_lower for word in ['مرحبا', 'هلا', 'السلام', 'أهلا', 'صباح', 'مساء']):
            return "أهلاً وسهلاً! 👋 أنا مساعد BWW Store الذكي. يمكنني مساعدتك في:\n\n🛍️ البحث عن المنتجات\n💰 معرفة الأسعار\n📦 الاستفسار عن التوافر\n📍 معلومات المتجر\n\nماذا تريد اليوم؟"

        # English greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings']):
            return "Hello! 👋 I'm BWW Store's smart assistant. I can help you with:\n\n🛍️ Product search\n💰 Prices\n📦 Availability\n📍 Store information\n\nWhat can I do for you today?"

        # Arabic help requests
        if any(word in message_lower for word in ['مساعدة', 'ساعد', 'ممكن', 'عايز', 'محتاج']):
            return "بالتأكيد! سأساعدك بكل سرور 😊\n\nيمكنني:\n✨ البحث عن أي منتج في متجر BWW\n✨ إعطائك معلومات عن الأسعار والمقاسات\n✨ المساعدة في اختيار المنتج المناسب\n\nماذا تبحث عنه بالضبط؟"

        # English help requests
        if any(word in message_lower for word in ['help', 'assist', 'support', 'need', 'want']):
            return "Of course! I'd love to help! 😊\n\nI can:\n✨ Search for any product in BWW Store\n✨ Provide info about prices and sizes\n✨ Help you choose the right product\n\nWhat exactly are you looking for?"

        # Arabic product requests
        if any(word in message_lower for word in ['منتج', 'فستان', 'قميص', 'حذاء', 'ملابس', 'بنطلون', 'جاكيت']):
            return "رائع! 🎉 دعني أساعدك في العثور على ما تبحث عنه.\n\nأخبرني أكثر عن:\n📌 نوع المنتج\n📌 اللون المفضل\n📌 المقاس\n📌 الميزانية\n\nوسأجد لك أفضل الخيارات! 🛍️"

        # English product requests
        if any(word in message_lower for word in ['product', 'dress', 'shirt', 'shoes', 'clothes', 'fashion', 'pants', 'jacket']):
            return "Excellent! 🎉 Let me help you find what you're looking for.\n\nTell me more about:\n📌 Product type\n📌 Preferred color\n📌 Size\n📌 Budget\n\nAnd I'll find you the best options! 🛍️"

        # Price inquiries
        if any(word in message_lower for word in ['سعر', 'price', 'كام', 'كم', 'how much', 'cost', 'تكلفة']):
            return "أسعارنا تنافسية جداً! 💰\n\nأخبرني عن المنتج اللي عايز تعرف سعره، وهديك كل التفاصيل بما فيها:\n• السعر الحالي\n• أي عروض متاحة\n• خيارات التوصيل"

        # Thanks
        if any(word in message_lower for word in ['شكرا', 'thank', 'thanks', 'thx']):
            return "العفو! 🌟 أنا موجود دايماً لمساعدتك. لو احتجت أي حاجة تانية، ابعتلي!"

        # Default Arabic response
        if any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in message):
            return "أنا هنا لمساعدتك! 😊\n\nيمكنك أن تسألني عن:\n🔍 منتجات معينة\n💰 الأسعار\n📦 التوافر\n🚚 التوصيل\n\nاكتب لي اللي محتاجه وأنا هساعدك فوراً!"

        # Default English response
        return "I'm here to help! 😊\n\nYou can ask me about:\n🔍 Specific products\n💰 Prices\n📦 Availability\n🚚 Delivery\n\nJust tell me what you need!"

    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return gemini_available and any(model is not None for model in self.models.values())

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "service": "Gemini Multi-Model",
            "models": {
                "multimodal": {
                    "name": "gemini-2.5-flash",
                    "available": self.models['multimodal'] is not None,
                    "supports": ["text", "images", "audio"],
                    "use_case": "Images + Audio + Text → Text"
                },
                "text_fast": {
                    "name": "gemma-3-27b-it",
                    "available": self.models['text_fast'] is not None,
                    "supports": ["text"],
                    "use_case": "Fast text-only responses (أسرع وأرخص)"
                },
                "text_quality": {
                    "name": "gemini-2.5-pro",
                    "available": self.models['text_quality'] is not None,
                    "supports": ["text"],
                    "use_case": "High-quality text responses"
                }
            },
            "api_key_configured": bool(self.api_key),
            "package_installed": gemini_available,
            "strategy": "Smart routing: text-only → Gemma (fast), multimodal → Gemini Flash"
        }

    def _do_initialize(self) -> bool:
        """Initialize Gemini service"""
        try:
            self._initialize_models()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            return False

    def _generate_response_impl(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """AI-specific response generation"""
        try:
            # Extract media files if present in context
            media_files: Optional[List[Dict[str, Any]]] = context.get('media_files') if context else None
            use_quality: bool = context.get('use_quality_model', False) if context else False

            response = self.generate_response(
                message=query,
                context=context,
                media_files=media_files,
                use_quality_model=use_quality
            )

            # Determine which model was used
            model_used = "fallback"
            if media_files:
                model_used = "gemini-2.5-flash (multimodal)"
            elif use_quality and self.models['text_quality']:
                model_used = "gemini-2.5-pro"
            elif self.models['text_fast']:
                model_used = "gemma-3-27b-it"
            else:
                model_used = "gemini-2.5-flash"

            return {
                "response": response,
                "success": True,
                "model_used": model_used,
                "multimodal": bool(media_files)
            }
        except Exception as e:
            self.logger.error(f"Error generating Gemini response: {e}")
            return {
                "response": "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى.",
                "success": False,
                "error": str(e),
                "model_used": "fallback"
            }
