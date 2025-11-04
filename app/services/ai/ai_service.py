"""
AI Service Implementation for BWW Assistant Chatbot
AI service with multiple providers support and fallback mechanisms
"""

import logging
from typing import Optional, Dict, Any

from app.services.core.base_service import AIService as BaseAIService
from app.services.core.interfaces import ServiceConfig
from app.services.ai.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class AIService(BaseAIService):
    """
    AI service with provider management and fallback

    Currently uses Gemini as primary provider with built-in fallback responses
    Can be extended to support multiple AI providers (OpenAI, Anthropic, etc.)
    """

    def __init__(self, config: Optional[ServiceConfig] = None):
        super().__init__(config)

        # AI provider configuration
        self.primary_provider = "gemini"
        self.fallback_enabled = True

        # Provider instances
        self._gemini_service: Optional[GeminiService] = None

        # Performance tracking
        self._request_count = 0
        self._fallback_count = 0
        self._error_count = 0

    def _do_initialize(self) -> bool:
        """Initialize AI service with providers"""
        try:
            # Initialize Gemini service
            self._gemini_service = GeminiService()

            if self._gemini_service.is_available():
                self.model_loaded = True
                self.model = self._gemini_service.model
                logger.info("AI Service initialized with Gemini provider")
            else:
                self.model_loaded = False
                self.model = None
                logger.warning("AI Service initialized with fallback mode only")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            self.model_loaded = False
            return False

    def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response with automatic provider selection

        Args:
            message: User message
            context: Additional context (user data, conversation history, etc.)

        Returns:
            Generated response string
        """
        self._request_count += 1

        try:
            if self._gemini_service and self._gemini_service.is_available():
                response = self._gemini_service.generate_response(message, context)
                logger.debug(f"Generated response using Gemini: {response[:50]}...")
                return response
            else:
                self._fallback_count += 1
                response = self._generate_fallback_response(message, context)
                logger.debug(f"Generated fallback response: {response[:50]}...")
                return response

        except Exception as e:
            self._error_count += 1
            logger.error(f"Error generating AI response: {e}")
            return self._generate_error_response(message)

    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect user intent from message

        Args:
            message: User message

        Returns:
            Dictionary with intent classification
        """
        message_lower = message.lower()

        # Greeting detection
        if any(word in message_lower for word in ['مرحبا', 'هلا', 'السلام', 'أهلا', 'hello', 'hi', 'hey']):
            return {
                "intent": "greeting",
                "confidence": 0.9,
                "entities": {}
            }

        # Product search intent
        if any(word in message_lower for word in ['منتج', 'فستان', 'قميص', 'حذاء', 'product', 'dress', 'shirt']):
            return {
                "intent": "product_search",
                "confidence": 0.85,
                "entities": self._extract_product_entities(message)
            }

        # Price inquiry
        if any(word in message_lower for word in ['سعر', 'price', 'كم', 'how much', 'cost']):
            return {
                "intent": "price_inquiry",
                "confidence": 0.8,
                "entities": {}
            }

        # Help request
        if any(word in message_lower for word in ['مساعدة', 'ساعد', 'help', 'assist']):
            return {
                "intent": "help_request",
                "confidence": 0.75,
                "entities": {}
            }

        # Default - conversational
        return {
            "intent": "conversational",
            "confidence": 0.5,
            "entities": {}
        }

    def extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extract entities from message

        Args:
            message: User message

        Returns:
            Dictionary of extracted entities
        """
        entities: Dict[str, list[str]] = {
            "products": [],
            "colors": [],
            "sizes": [],
            "brands": [],
            "locations": []
        }

        # Extract product types
        product_keywords = {
            "dress": ["فستان", "dress", "فساتين", "dresses"],
            "shirt": ["قميص", "shirt", "قمصان", "shirts"],
            "shoes": ["حذاء", "shoes", "أحذية", "shoe"],
            "pants": ["بنطلون", "pants", "بناطيل", "trousers"]
        }

        message_lower = message.lower()
        for product_type, keywords in product_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                entities["products"].append(product_type)

        # Extract colors (basic)
        color_keywords = ["أحمر", "أزرق", "أخضر", "أسود", "أبيض", "red", "blue", "green", "black", "white"]
        for color in color_keywords:
            if color in message_lower:
                entities["colors"].append(color)

        return entities

    def _extract_product_entities(self, message: str) -> Dict[str, Any]:
        """Helper to extract product-related entities"""
        return self.extract_entities(message)

    def _generate_fallback_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate fallback response when AI providers are unavailable"""
        if self._gemini_service:
            return self._gemini_service.generate_fallback_response(message)

        # Ultimate fallback
        return "شكراً لرسالتك. أنا مساعد BWW Store وأنا هنا لمساعدتك!"

    def _generate_error_response(self, message: str) -> str:
        """Generate error response"""
        # Detect language
        is_arabic = any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in message)

        if is_arabic:
            return "عذراً، حدث خطأ مؤقت. يرجى المحاولة مرة أخرى."
        else:
            return "Sorry, a temporary error occurred. Please try again."

    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive AI service status"""
        status = super().get_service_status()

        status.update({
            "primary_provider": self.primary_provider,
            "gemini_available": self._gemini_service.is_available() if self._gemini_service else False,
            "fallback_enabled": self.fallback_enabled,
            "request_count": self._request_count,
            "fallback_count": self._fallback_count,
            "error_count": self._error_count,
            "fallback_rate": self._fallback_count / max(self._request_count, 1),
            "error_rate": self._error_count / max(self._request_count, 1),
            "model_info": self._gemini_service.get_model_info() if self._gemini_service else {}
        })

        return status

    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self._gemini_service is not None

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers"""
        return {
            "primary": self.primary_provider,
            "providers": {
                "gemini": {
                    "available": self._gemini_service.is_available() if self._gemini_service else False,
                    "model": "gemini-2.5-flash"
                }
            },
            "fallback_enabled": self.fallback_enabled
        }

    def _do_shutdown(self) -> None:
        """Shutdown AI service"""
        try:
            if self._gemini_service and hasattr(self._gemini_service, 'shutdown'):
                self._gemini_service.shutdown()

            logger.info("AI Service shutdown completed")
        except Exception as e:
            logger.error(f"Error during AI service shutdown: {e}")

# Convenience function for quick access
def get_ai_service() -> AIService:
    """Get AI service instance"""
    from app.services.infrastructure.di_container import get_service
    service = get_service("ai_service")
    if service and isinstance(service, AIService):
        return service

    # Create new instance if not registered
    new_service = AIService()
    new_service.initialize()
    return new_service
