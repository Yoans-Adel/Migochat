"""Type stubs for google.generativeai package"""

from typing import Any

class GenerativeModel:
    """Gemini AI generative model"""
    def __init__(self, model_name: str) -> None: ...
    def generate_content(self, prompt: str) -> Any: ...

def configure(api_key: str) -> None:
    """Configure the API key"""
    ...
