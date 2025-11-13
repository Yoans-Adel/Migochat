import requests
import json
import logging
from typing import Dict, List, Optional, Any
from config.settings import settings
from app.services.messaging.platform_messaging_service import PlatformMessagingService
from app.services.infrastructure.error_handler import api_error_handler, retry_on_error, circuit_breaker, RetryConfig, CircuitBreakerConfig

logger = logging.getLogger(__name__)


class MessengerService(PlatformMessagingService):
    def __init__(self) -> None:
        super().__init__()
        self.api_url = settings.MESSENGER_API_URL
        self.page_access_token = settings.FB_PAGE_ACCESS_TOKEN
        self.app_id = settings.FB_APP_ID
        self.base_url = self.api_url
        self.headers = {"Content-Type": "application/json"}
        # Initialize the service
        self.initialize()

    @api_error_handler
    @retry_on_error(RetryConfig(max_retries=3, delay=1.0))
    @circuit_breaker("messenger_service", CircuitBreakerConfig(failure_threshold=5))
    def send_message(self, recipient_id: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a text message to a user"""
        url = f"{self.api_url}/me/messages"

        payload: Dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "message": {"text": message}
        }

        params = {"access_token": self.page_access_token}

        logger.info(f"Sending message to {recipient_id}: payload={json.dumps(payload)}")
        try:
            response = requests.post(url, json=payload, params=params)
            logger.info(f"Facebook API Response Status: {response.status_code}")
            logger.info(f"Facebook API Response Body: {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                error_detail = f" - Status: {e.response.status_code}, Response: {e.response.text}"
            logger.error(f"Error sending message: {e}{error_detail}")
            raise

    def send_quick_reply(self, recipient_id: str, text: str, quick_replies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send a message with quick reply buttons"""
        url = f"{self.api_url}/me/messages"

        payload: Dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "message": {
                "text": text,
                "quick_replies": quick_replies
            }
        }

        params = {"access_token": self.page_access_token}

        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending quick reply: {e}")
            raise

    def send_typing_indicator(self, recipient_id: str) -> Dict[str, Any]:
        """Send typing indicator"""
        url = f"{self.api_url}/me/messages"

        payload: Dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "sender_action": "typing_on"
        }

        params = {"access_token": self.page_access_token}

        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending typing indicator: {e}")
            raise

    def get_user_profile(self, psid: str) -> Dict[str, Any]:
        """Get user profile information"""
        url = f"{self.api_url}/{psid}"

        params = {
            "access_token": self.page_access_token,
            "fields": "first_name,last_name,profile_pic"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user profile: {e}")
            raise

    def send_media(self, recipient_id: str, media_type: str, media_url: str) -> Dict[str, Any]:
        """Send media message (image, file, etc.)"""
        url = f"{self.api_url}/me/messages"

        payload: Dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": media_type,
                    "payload": {
                        "url": media_url
                    }
                }
            }
        }

        params = {"access_token": self.page_access_token}

        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending media: {e}")
            raise

    def mark_message_as_read(self, identifier: str, **kwargs: Any) -> Dict[str, Any]:
        """Mark messages as read"""
        # Accept both 'recipient_id' and 'identifier' for compatibility
        recipient_id = kwargs.get('recipient_id', identifier)
        
        url = f"{self.api_url}/me/messages"

        payload: Dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "sender_action": "mark_seen"
        }

        params = {"access_token": self.page_access_token}

        try:
            response = requests.post(url, json=payload, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error marking message as read: {e}")
            raise

    def verify_webhook(self, verify_token: str, challenge: str, expected_token: str = "") -> Optional[str]:
        """Verify webhook subscription"""
        # Use settings.FB_VERIFY_TOKEN if expected_token not provided
        token_to_check = expected_token or settings.FB_VERIFY_TOKEN
        return super().verify_webhook(verify_token, challenge, token_to_check)

    def _do_initialize(self) -> bool:
        """Initialize Messenger service"""
        # Test API connection
        try:
            # Simple test to verify API access
            test_url = f"{self.api_url}/me"
            params = {"access_token": self.page_access_token}
            response = requests.get(test_url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("Messenger API connection verified")
            return True
        except Exception as e:
            logger.warning(f"Messenger API connection test failed: {e}")
            # Don't raise exception, service can still work with limited functionality
            return False

