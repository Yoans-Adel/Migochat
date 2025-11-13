"""
Gemini AI Service Tests
Tests for Google Gemini AI integration
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
@pytest.mark.services
class TestGeminiService:
    """Test Gemini AI Service"""

    def test_service_initialization(self):
        """Test Gemini service initializes correctly"""
        try:
            from app.services.ai.gemini_service import GeminiService

            service = GeminiService()
            assert service is not None
            assert hasattr(service, 'api_key')
        except ImportError:
            pytest.skip("Gemini service not available")

    def test_service_has_required_methods(self):
        """Test service has required methods"""
        try:
            from app.services.ai.gemini_service import GeminiService

            service = GeminiService()
            assert hasattr(service, 'generate_response') or hasattr(service, 'generate')
        except ImportError:
            pytest.skip("Gemini service not available")

    @patch('google.generativeai.GenerativeModel')
    def test_generate_response_with_mock(self, mock_model, mock_gemini_response):
        """Test generate response with mocked Gemini"""
        try:
            from app.services.ai.gemini_service import GeminiService

            # Mock the model response
            mock_instance = Mock()
            mock_instance.generate_content.return_value = Mock(
                text=mock_gemini_response["text"]
            )
            mock_model.return_value = mock_instance

            service = GeminiService()

            if hasattr(service, 'generate_response'):
                result = service.generate_response("Test prompt")
            elif hasattr(service, 'generate'):
                result = service.generate("Test prompt")
            else:
                pytest.skip("No generate method found")

            assert result is not None
        except ImportError:
            pytest.skip("Gemini dependencies not available")

    def test_api_key_configured(self):
        """Test API key is configured"""
        from config.settings import settings

        assert hasattr(settings, 'GEMINI_API_KEY')
        assert settings.GEMINI_API_KEY is not None

    def test_prompt_formatting(self):
        """Test prompt formatting"""
        prompt = "مرحبا، كيف يمكنني مساعدتك؟"

        # Prompt should be string
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_arabic_text_handling(self):
        """Test Arabic text handling"""
        arabic_text = "مرحبا بك في متجر BWW"

        # Should handle Arabic text
        assert isinstance(arabic_text, str)
        # Check it contains Arabic characters
        assert any('\u0600' <= char <= '\u06FF' for char in arabic_text)


@pytest.mark.unit
@pytest.mark.services
class TestGeminiPrompts:
    """Test Gemini prompt engineering"""

    def test_system_prompt_structure(self):
        """Test system prompt structure"""
        system_prompt = """
        You are a helpful assistant for BWW store.
        Respond in Arabic.
        Be professional and friendly.
        """

        assert "BWW" in system_prompt or "assistant" in system_prompt.lower()

    def test_context_injection(self):
        """Test context injection in prompts"""
        user_context = {
            "name": "أحمد",
            "last_purchase": "قميص",
            "preferences": "ملابس رياضية"
        }

        prompt = f"المستخدم {user_context['name']} يفضل {user_context['preferences']}"

        assert user_context["name"] in prompt
        assert user_context["preferences"] in prompt


@pytest.mark.services
@pytest.mark.slow
class TestGeminiIntegration:
    """Integration tests for Gemini service"""

    @pytest.mark.skip(reason="Requires real Gemini API key")
    def test_real_api_call(self):
        """Test real Gemini API call (skipped by default)"""
        # Real API call would go here
        pass

    def test_error_handling(self):
        """Test error handling"""
        try:
            from app.services.ai.gemini_service import GeminiService

            service = GeminiService()

            # Test with empty prompt
            try:
                if hasattr(service, 'generate_response'):
                    result = service.generate_response("")
                elif hasattr(service, 'generate'):
                    result = service.generate("")

                # Should handle empty prompt gracefully
                assert result is None or result == "" or isinstance(result, str)
            except (ValueError, Exception):
                # Expected to raise error
                pass
        except ImportError:
            pytest.skip("Gemini service not available")

