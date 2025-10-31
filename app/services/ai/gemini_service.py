import logging
from typing import Optional, Dict, Any
import json
from Server.config import settings
from app.services.core.base_service import AIService as BaseAIService

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)

class GeminiService(BaseAIService):
    """Gemini AI service for generating responses"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        self._initialize_model()
        # Initialize the service
        self.initialize()
    
    def _initialize_model(self):
        """Initialize the Gemini model"""
        if not GEMINI_AVAILABLE:
            # Suppress warning on first initialization only
            if not hasattr(self, '_warning_shown'):
                logger.info("Gemini AI service not available - using fallback responses")
                self._warning_shown = True
            self.model = None
            return
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    def generate_response(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response using Gemini
        
        Args:
            message: User message
            user_context: Additional context about the user
            
        Returns:
            Generated response
        """
        if not GEMINI_AVAILABLE or not self.model:
            logger.warning("Gemini not available, using fallback response")
            return self._fallback_response(message)
        
        try:
            # Build context for the AI
            context = self._build_context(user_context)
            
            # Create prompt optimized for Gemini 2.5 Flash
            prompt = f"""
You are Bww-Assistant-chatbot, an intelligent AI assistant for BWW Store, a leading fashion retailer in Egypt specializing in men's, women's, and kids' fashion.

User Context: {context}

User Message: {message}

Instructions:
- Respond in Arabic if the user wrote in Arabic, otherwise respond in English
- Keep responses concise, helpful, and engaging
- Use emojis appropriately to make responses more friendly
- If asked about products, mention our comprehensive catalog and ability to search
- If asked about prices or availability, explain our real-time product search capabilities
- Be conversational and build rapport with customers
- Always maintain a professional yet warm tone

Response:
"""
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Gemini response generated successfully")
                return response.text.strip()
            else:
                logger.warning("Gemini returned empty response")
                return self._fallback_response(message)
                
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return self._fallback_response(message)
    
    def _build_context(self, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Build context string for the AI"""
        if not user_context:
            return "No additional context available"
        
        context_parts = []
        
        if user_context.get('lead_stage'):
            context_parts.append(f"Lead stage: {user_context['lead_stage']}")
        
        if user_context.get('customer_type'):
            context_parts.append(f"Customer type: {user_context['customer_type']}")
        
        if user_context.get('customer_label'):
            context_parts.append(f"Customer label: {user_context['customer_label']}")
        
        if user_context.get('message_count', 0) > 0:
            context_parts.append(f"Previous messages: {user_context['message_count']}")
        
        return "; ".join(context_parts) if context_parts else "New customer"
    
    def _fallback_response(self, message: str) -> str:
        """Fallback response when Gemini is not available"""
        message_lower = message.lower()
        
        # Arabic greetings
        if any(word in message_lower for word in ['مرحبا', 'هلا', 'السلام', 'أهلا']):
            return "أهلاً وسهلاً! أنا مساعد BWW Store. كيف يمكنني مساعدتك اليوم؟"
        
        # English greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm BWW Store assistant. How can I help you today?"
        
        # Arabic help requests
        if any(word in message_lower for word in ['مساعدة', 'ساعد', 'ممكن', 'كيف']):
            return "بالطبع! يمكنني مساعدتك في العثور على المنتجات، الأسعار، والمعلومات عن متجر BWW. ماذا تبحث عنه؟"
        
        # English help requests
        if any(word in message_lower for word in ['help', 'assist', 'support']):
            return "Of course! I can help you find products, prices, and information about BWW Store. What are you looking for?"
        
        # Arabic product requests
        if any(word in message_lower for word in ['منتج', 'فستان', 'قميص', 'حذاء', 'ملابس']):
            return "ممتاز! يمكنني البحث عن المنتجات في متجر BWW. أخبرني ما تبحث عنه بالضبط."
        
        # English product requests
        if any(word in message_lower for word in ['product', 'dress', 'shirt', 'shoes', 'clothes', 'fashion']):
            return "Great! I can search for products in BWW Store. Tell me exactly what you're looking for."
        
        # Default Arabic response
        if any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in message):
            return "شكراً لك! أنا هنا لمساعدتك. هل تبحث عن منتج معين من متجر BWW؟"
        
        # Default English response
        return "Thank you! I'm here to help. Are you looking for a specific product from BWW Store?"
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return GEMINI_AVAILABLE and self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "service": "Gemini",
            "model": "gemini-2.5-flash",
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key),
            "package_installed": GEMINI_AVAILABLE
        }
    
    def _do_initialize(self):
        """Initialize Gemini service"""
        self._initialize_model()
    
    def _generate_response_impl(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """AI-specific response generation"""
        try:
            response = self.generate_response(query)
            return {
                "response": response,
                "success": True,
                "model_used": "gemini" if self.is_available() else "fallback"
            }
        except Exception as e:
            self.logger.error(f"Error generating Gemini response: {e}")
            return {
                "response": "عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى.",
                "success": False,
                "error": str(e),
                "model_used": "fallback"
            }
