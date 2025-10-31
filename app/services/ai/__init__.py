"""
AI Services Module
==================
Artificial Intelligence and Natural Language Processing services.

This module provides:
- Gemini AI integration (Google Generative AI)
- Professional AI service wrapper with intent detection
- Entity extraction and fallback responses

Enables intelligent conversation handling and AI-powered features.
"""

from typing import TYPE_CHECKING

# Lazy imports for better performance
if TYPE_CHECKING:
    from .gemini_service import GeminiService
    from .ai_service import AIService

__all__ = [
    "GeminiService",
    "AIService",
]


def __getattr__(name: str):
    """Lazy import mechanism for better performance."""
    if name == "GeminiService":
        from .gemini_service import GeminiService
        return GeminiService
    
    if name == "AIService":
        from .ai_service import AIService
        return AIService
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
