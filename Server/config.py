"""
Server Configuration Settings
Property-based settings using ConfigurationManager with full type safety
"""

from typing import List
from Server.config_manager import config_manager, ConfigurationManager


class Settings:
    """Settings class with property-based configuration and type safety"""

    def __init__(self) -> None:
        self._config: ConfigurationManager = config_manager
        if not self._config.is_loaded():
            self._config.load_configuration()

    def _get_str(self, section: str, key: str, default: str = "") -> str:
        """Type-safe string getter"""
        value = self._config.get_config(section, key, default)
        return str(value) if value is not None else default

    def _get_int(self, section: str, key: str, default: int = 0) -> int:
        """Type-safe integer getter"""
        value = self._config.get_config(section, key, default)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return default

    def _get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """Type-safe boolean getter"""
        value = self._config.get_config(section, key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return default

    # Facebook Configuration
    @property
    def FB_APP_ID(self) -> str:
        return self._get_str("facebook", "app_id")

    @property
    def FB_APP_SECRET(self) -> str:
        return self._get_str("facebook", "app_secret")

    @property
    def FB_PAGE_ACCESS_TOKEN(self) -> str:
        return self._get_str("facebook", "page_access_token")

    @property
    def FB_PAGE_ID(self) -> str:
        return self._get_str("facebook", "page_id")

    @property
    def FB_SYSTEM_USER_TOKEN(self) -> str:
        return self._get_str("facebook", "system_user_token")

    @property
    def FB_VERIFY_TOKEN(self) -> str:
        return self._get_str("facebook", "verify_token")

    @property
    def FB_LEADCENTER_VERIFY_TOKEN(self) -> str:
        return self._get_str("facebook", "leadcenter_verify_token")

    # WhatsApp Configuration
    @property
    def WHATSAPP_ACCESS_TOKEN(self) -> str:
        return self._get_str("whatsapp", "access_token")

    @property
    def WHATSAPP_PHONE_NUMBER_ID(self) -> str:
        return self._get_str("whatsapp", "phone_number_id")

    @property
    def WHATSAPP_VERIFY_TOKEN(self) -> str:
        return self._get_str("whatsapp", "verify_token")

    # Webhook Configuration
    @property
    def MESSENGER_WEBHOOK_URL(self) -> str:
        return self._get_str("webhooks", "messenger_url")

    @property
    def WHATSAPP_WEBHOOK_URL(self) -> str:
        return self._get_str("webhooks", "whatsapp_url")

    @property
    def LEADCENTER_WEBHOOK_URL(self) -> str:
        return self._get_str("webhooks", "leadcenter_url")

    # Database Configuration
    @property
    def DATABASE_URL(self) -> str:
        return self._get_str("database", "url")

    # Application Configuration
    @property
    def DEBUG(self) -> bool:
        return self._get_bool("app", "debug")

    @property
    def ENVIRONMENT(self) -> str:
        return self._get_str("app", "environment")

    @property
    def LOG_LEVEL(self) -> str:
        return self._get_str("app", "log_level")

    @property
    def TIMEZONE(self) -> str:
        return self._get_str("app", "timezone")

    @property
    def HOST(self) -> str:
        return self._get_str("app", "host")

    @property
    def PORT(self) -> int:
        return self._get_int("app", "port")

    # AI Configuration
    @property
    def GEMINI_API_KEY(self) -> str:
        return self._get_str("ai", "gemini_api_key")

    @property
    def GEMINI_MODEL(self) -> str:
        """Get Gemini model name, default to gemini-2.5-flash"""
        return self._get_str("ai", "gemini_model") or "gemini-2.5-flash"

    # BWW Store Configuration
    @property
    def BWW_STORE_SECRET_KEY(self) -> str:
        return self._get_str("bww_store", "secret_key")

    @property
    def BWW_STORE_BASE_URL(self) -> str:
        return self._get_str("bww_store", "base_url")

    # API Configuration
    @property
    def MESSENGER_API_URL(self) -> str:
        return self._get_str("api", "messenger_api_url")

    @property
    def WEBHOOK_URL(self) -> str:
        return self._get_str("api", "webhook_url")

    def validate_required_settings(self) -> List[str]:
        """Validate that all required settings are configured"""
        return self._config.validate_configuration()

    def update_webhook_urls(self, base_url: str):
        """Update webhook URLs with base URL"""
        self._config.update_webhook_urls(base_url)


settings = Settings()
