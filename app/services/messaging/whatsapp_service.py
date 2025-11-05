import logging
import requests
from typing import Dict, Optional, List, Any
from Server.config import settings
from app.services.messaging.platform_messaging_service import PlatformMessagingService

logger = logging.getLogger(__name__)


class WhatsAppService(PlatformMessagingService):
    """Service for integrating with WhatsApp Business API"""

    def __init__(self) -> None:
        super().__init__()
        self.api_url = "https://graph.facebook.com/v24.0"
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN
        self.base_url = self.api_url
        self.headers = {"Content-Type": "application/json"}
        # Initialize the service
        self.initialize()

    def send_message(self, to: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """Send a text message via WhatsApp Business API"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        # Format phone number (remove + and ensure it's numeric)
        formatted_to = to.replace("+", "").replace("-", "").replace(" ", "")

        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_to,
            "type": message_type,
            "text": {"body": message}
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            raise

    def send_template_message(self, to: str, template_name: str, template_params: List[str] = None) -> Dict[str, Any]:
        """Send a template message via WhatsApp Business API"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        # Format phone number
        formatted_to = to.replace("+", "").replace("-", "").replace(" ", "")

        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "ar"},
                "components": []
            }
        }

        # Add parameters if provided
        if template_params:
            payload["template"]["components"] = [{
                "type": "body",
                "parameters": [{"type": "text", "text": param} for param in template_params]
            }]

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp template: {e}")
            raise

    def send_interactive_message(self, to: str, header_text: str, body_text: str,
                                 footer_text: Optional[str] = None, buttons: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Send an interactive message with buttons"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        interactive_data = {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "action": {"buttons": buttons or []}
            }
        }

        if footer_text:
            interactive_data["interactive"]["footer"] = {"text": footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            **interactive_data
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp interactive message: {e}")
            raise

    def send_list_message(self, to: str, header_text: str, body_text: str,
                          button_text: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send a list message"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp list message: {e}")
            raise

    def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error marking WhatsApp message as read: {e}")
            raise

    def get_media_url(self, media_id: str) -> Optional[str]:
        """Get media URL from media ID"""
        url = f"{self.api_url}/{media_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("url")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting WhatsApp media URL: {e}")
            return None

    def download_media(self, media_url: str) -> Optional[bytes]:
        """Download media from WhatsApp"""
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(media_url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading WhatsApp media: {e}")
            return None

    def verify_webhook(self, verify_token: str, challenge: str) -> Optional[str]:
        """Verify WhatsApp webhook subscription"""
        return super().verify_webhook(verify_token, challenge, self.verify_token)
