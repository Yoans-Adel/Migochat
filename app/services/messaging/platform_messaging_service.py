"""
Base class for platform messaging services (Messenger, WhatsApp)
Eliminates code duplication and provides common functionality
"""
import logging
import requests
from typing import Dict, Optional, Any
from abc import abstractmethod
from app.services.core.base_service import APIService

logger = logging.getLogger(__name__)


class PlatformMessagingService(APIService):
    """
    Base class for messaging platform services
    
    Provides common functionality:
    - HTTP request handling
    - Webhook verification
    - Error logging
    - Service initialization/shutdown
    
    Platform-specific implementations (Messenger, WhatsApp) should:
    1. Call super().__init__() in their __init__
    2. Set platform-specific attributes (api_url, tokens, etc.)
    3. Implement abstract methods for platform-specific behavior
    """
    
    def __init__(self) -> None:
        super().__init__()
        # Common attributes - subclasses should set these
        self.api_url: str = ""
        self.base_url: str = ""
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
    
    def make_request(
        self, 
        method: str, 
        url: str, 
        log_errors: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with consistent error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            log_errors: Whether to log errors
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            JSON response as dict
            
        Raises:
            requests.exceptions.RequestException: On HTTP errors
        """
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if log_errors:
                error_detail = ""
                if hasattr(e, 'response') and e.response is not None:
                    error_detail = f" - Status: {e.response.status_code}, Response: {e.response.text}"
                logger.error(f"{self.__class__.__name__} request failed: {e}{error_detail}")
            raise
    
    def verify_webhook(self, verify_token: str, challenge: str, expected_token: str) -> Optional[str]:
        """
        Verify webhook subscription with platform
        
        Args:
            verify_token: Token received from platform
            challenge: Challenge string from platform
            expected_token: Our configured verify token
            
        Returns:
            Challenge string if verification succeeds, None otherwise
        """
        if verify_token == expected_token:
            logger.info(f"{self.__class__.__name__} webhook verified successfully")
            return challenge
        logger.warning(f"{self.__class__.__name__} webhook verification failed")
        return None
    
    def _log_request(self, recipient_id: str, action: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Log outgoing request for debugging
        
        Args:
            recipient_id: Target user/phone
            action: Description of action (e.g., "sending message")
            payload: Request payload (optional)
        """
        log_msg = f"{self.__class__.__name__} {action} to {recipient_id}"
        if payload:
            import json
            log_msg += f": payload={json.dumps(payload)}"
        logger.info(log_msg)
    
    def _log_response(self, status_code: int, response_text: str) -> None:
        """
        Log API response for debugging
        
        Args:
            status_code: HTTP status code
            response_text: Response body
        """
        logger.info(f"{self.__class__.__name__} API Response Status: {status_code}")
        logger.info(f"{self.__class__.__name__} API Response Body: {response_text}")
    
    def _handle_request_error(self, action: str, error: Exception) -> None:
        """
        Handle and log request errors consistently
        
        Args:
            action: Description of failed action
            error: Exception that occurred
        """
        error_detail = ""
        if hasattr(error, 'response') and error.response is not None:
            error_detail = f" - Status: {error.response.status_code}, Response: {error.response.text}"
        logger.error(f"{self.__class__.__name__} error {action}: {error}{error_detail}")
    
    @abstractmethod
    def send_message(self, recipient_id: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send a text message
        
        Args:
            recipient_id: Target user ID or phone number
            message: Message text
            message_type: Type of message (default: "text")
            
        Returns:
            API response as dict
        """
        pass
    
    @abstractmethod
    def mark_message_as_read(self, identifier: str) -> Dict[str, Any]:
        """
        Mark message as read
        
        Args:
            identifier: Message ID or recipient ID (platform-specific)
            
        Returns:
            API response as dict
        """
        pass
    
    def _do_shutdown(self) -> None:
        """Common shutdown logic"""
        logger.info(f"{self.__class__.__name__} shutdown")
