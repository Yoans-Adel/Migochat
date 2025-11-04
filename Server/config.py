"""
Server Configuration Settings
Property-based settings using ConfigurationManager
"""

from typing import List
from Server.config_manager import config_manager

class Settings:
    """Settings class with property-based configuration"""

    def __init__(self):
        self._config = config_manager
        if not self._config.is_loaded():
            self._config.load_configuration()

    # Facebook Configuration
    @property
    def FB_APP_ID(self) -> str:
        return self._config.get_config("facebook", "app_id")

    @property
    def FB_APP_SECRET(self) -> str:
        return self._config.get_config("facebook", "app_secret")

    @property
    def FB_PAGE_ACCESS_TOKEN(self) -> str:
        return self._config.get_config("facebook", "page_access_token")

    @property
    def FB_PAGE_ID(self) -> str:
        return self._config.get_config("facebook", "page_id")

    @property
    def FB_SYSTEM_USER_TOKEN(self) -> str:
        return self._config.get_config("facebook", "system_user_token")

    @property
    def FB_VERIFY_TOKEN(self) -> str:
        return self._config.get_config("facebook", "verify_token")

    @property
    def FB_LEADCENTER_VERIFY_TOKEN(self) -> str:
        return self._config.get_config("facebook", "leadcenter_verify_token")

    # WhatsApp Configuration
    @property
    def WHATSAPP_ACCESS_TOKEN(self) -> str:
        return self._config.get_config("whatsapp", "access_token")

    @property
    def WHATSAPP_PHONE_NUMBER_ID(self) -> str:
        return self._config.get_config("whatsapp", "phone_number_id")

    @property
    def WHATSAPP_VERIFY_TOKEN(self) -> str:
        return self._config.get_config("whatsapp", "verify_token")

    # Webhook Configuration
    @property
    def MESSENGER_WEBHOOK_URL(self) -> str:
        return self._config.get_config("webhooks", "messenger_url")

    @property
    def WHATSAPP_WEBHOOK_URL(self) -> str:
        return self._config.get_config("webhooks", "whatsapp_url")

    @property
    def LEADCENTER_WEBHOOK_URL(self) -> str:
        return self._config.get_config("webhooks", "leadcenter_url")

    # Database Configuration
    @property
    def DATABASE_URL(self) -> str:
        return self._config.get_config("database", "url")

    # Application Configuration
    @property
    def DEBUG(self) -> bool:
        return self._config.get_config("app", "debug")

    @property
    def ENVIRONMENT(self) -> str:
        return self._config.get_config("app", "environment")

    @property
    def LOG_LEVEL(self) -> str:
        return self._config.get_config("app", "log_level")

    @property
    def TIMEZONE(self) -> str:
        return self._config.get_config("app", "timezone")

    @property
    def HOST(self) -> str:
        return self._config.get_config("app", "host")

    @property
    def PORT(self) -> int:
        return self._config.get_config("app", "port")

    # AI Configuration
    @property
    def GEMINI_API_KEY(self) -> str:
        return self._config.get_config("ai", "gemini_api_key")

    @property
    def GEMINI_MODEL(self) -> str:
        """Get Gemini model name, default to gemini-2.5-flash"""
        return self._config.get_config("ai", "gemini_model", "gemini-2.5-flash")

    # BWW Store Configuration
    @property
    def BWW_STORE_SECRET_KEY(self) -> str:
        return self._config.get_config("bww_store", "secret_key")

    @property
    def BWW_STORE_BASE_URL(self) -> str:
        return self._config.get_config("bww_store", "base_url")

    # API Configuration
    @property
    def MESSENGER_API_URL(self) -> str:
        return self._config.get_config("api", "messenger_api_url")

    @property
    def WEBHOOK_URL(self) -> str:
        return self._config.get_config("api", "webhook_url")

    def validate_required_settings(self) -> List[str]:
        """Validate that all required settings are configured"""
        return self._config.validate_configuration()

    def update_webhook_urls(self, base_url: str):
        """Update webhook URLs with base URL"""
        self._config.update_webhook_urls(base_url)

settings = Settings()
