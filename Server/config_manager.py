"""
Configuration Manager for BWW Assistant Server
Centralized configuration management with validation
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ConfigurationManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self._loaded = False
        self._validated = False
        self.logger = logging.getLogger(__name__)
    
    def load_configuration(self) -> bool:
        """Load configuration from environment variables"""
        try:
            # Load .env file from config/ directory
            load_dotenv("config/.env")
            
            # Load configuration
            self.config = {
                # Facebook Configuration
                "facebook": {
                    "app_id": os.getenv("FB_APP_ID", ""),
                    "app_secret": os.getenv("FB_APP_SECRET", ""),
                    "page_access_token": os.getenv("FB_PAGE_ACCESS_TOKEN", ""),
                    "page_id": os.getenv("FB_PAGE_ID", ""),
                    "system_user_token": os.getenv("FB_SYSTEM_USER_TOKEN", ""),
                    "verify_token": os.getenv("FB_VERIFY_TOKEN", "BWW_MESSENGER_VERIFY_TOKEN_2025"),
                    "leadcenter_verify_token": os.getenv("FB_LEADCENTER_VERIFY_TOKEN", "BWW_LEADCENTER_VERIFY_TOKEN_2025"),
                },
                
                # WhatsApp Configuration
                "whatsapp": {
                    "access_token": os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
                    "phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
                    "verify_token": os.getenv("WHATSAPP_VERIFY_TOKEN", "BWW_WHATSAPP_VERIFY_TOKEN_2025"),
                },
                
                # Webhook Configuration
                "webhooks": {
                    "messenger_url": os.getenv("MESSENGER_WEBHOOK_URL", ""),
                    "whatsapp_url": os.getenv("WHATSAPP_WEBHOOK_URL", ""),
                    "leadcenter_url": os.getenv("LEADCENTER_WEBHOOK_URL", ""),
                },
                
                # Database Configuration
                "database": {
                    "url": os.getenv("DATABASE_URL", "sqlite:///database/bww_ai_assistant.db"),
                },
                
                # Application Configuration
                "app": {
                    "debug": os.getenv("DEBUG", "True").lower() == "true",
                    "environment": os.getenv("ENVIRONMENT", "development"),
                    "log_level": os.getenv("LOG_LEVEL", "INFO"),
                    "timezone": os.getenv("TIMEZONE", "Africa/Cairo"),
                    "host": os.getenv("HOST", "0.0.0.0"),
                    "port": int(os.getenv("PORT", "8000")),
                },
                
                # AI Configuration
                "ai": {
                    "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
                    "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                },
                
                # BWW Store Configuration
                "bww_store": {
                    "secret_key": os.getenv("BWW_STORE_SECRET_KEY", "BwwSecretKey2025"),
                    "base_url": os.getenv("BWW_STORE_BASE_URL", "https://api-v1.bww-store.com/api/v1"),
                },
                
                # API Configuration
                "api": {
                    "messenger_api_url": "https://graph.facebook.com/v24.0",
                    "webhook_url": "/webhook",
                }
            }
            
            self._loaded = True
            self.logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return missing required fields"""
        missing_fields = []
        
        if not self._loaded:
            missing_fields.append("Configuration not loaded")
            return missing_fields
        
        # Required Facebook fields
        required_facebook = ["app_id", "app_secret", "page_access_token", "page_id", "verify_token"]
        for field in required_facebook:
            if not self.config["facebook"][field]:
                missing_fields.append(f"facebook.{field}")
        
        # Required WhatsApp fields
        required_whatsapp = ["access_token", "phone_number_id", "verify_token"]
        for field in required_whatsapp:
            if not self.config["whatsapp"][field]:
                missing_fields.append(f"whatsapp.{field}")
        
        # Required AI fields
        if not self.config["ai"]["gemini_api_key"]:
            missing_fields.append("ai.gemini_api_key")
        
        self._validated = len(missing_fields) == 0
        return missing_fields
    
    def get_config(self, section: str = None, key: str = None, default: Any = None) -> Any:
        """Get configuration value with optional default
        
        Args:
            section: Configuration section (e.g., 'facebook', 'whatsapp', 'ai')
            key: Configuration key within section
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._loaded:
            self.load_configuration()
        
        if section is None:
            return self.config
        
        if key is None:
            return self.config.get(section, {})
        
        value = self.config.get(section, {}).get(key)
        
        # Return default if value is None or empty string
        if value is None or (isinstance(value, str) and value == ""):
            return default
            
        return value
    
    def get_facebook_config(self) -> Dict[str, str]:
        """Get Facebook configuration"""
        return self.get_config("facebook")
    
    def get_whatsapp_config(self) -> Dict[str, str]:
        """Get WhatsApp configuration"""
        return self.get_config("whatsapp")
    
    def get_webhook_config(self) -> Dict[str, str]:
        """Get webhook configuration"""
        return self.get_config("webhooks")
    
    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return self.get_config("database")
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.get_config("app")
    
    def get_ai_config(self) -> Dict[str, str]:
        """Get AI configuration"""
        return self.get_config("ai")
    
    def get_bww_store_config(self) -> Dict[str, str]:
        """Get BWW Store configuration"""
        return self.get_config("bww_store")
    
    def get_api_config(self) -> Dict[str, str]:
        """Get API configuration"""
        return self.get_config("api")
    
    def update_webhook_urls(self, base_url: str):
        """Update webhook URLs with base URL"""
        if not self._loaded:
            self.load_configuration()
        
        self.config["webhooks"]["messenger_url"] = f"{base_url}/webhook/messenger"
        self.config["webhooks"]["whatsapp_url"] = f"{base_url}/webhook/whatsapp"
        self.config["webhooks"]["leadcenter_url"] = f"{base_url}/webhook/leadgen"
        
        self.logger.info(f"Updated webhook URLs with base URL: {base_url}")
    
    def is_loaded(self) -> bool:
        """Check if configuration is loaded"""
        return self._loaded
    
    def is_validated(self) -> bool:
        """Check if configuration is validated"""
        return self._validated
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging"""
        if not self._loaded:
            return {"status": "not_loaded"}
        
        summary = {
            "status": "loaded",
            "validated": self._validated,
            "sections": {}
        }
        
        for section, config in self.config.items():
            summary["sections"][section] = {
                "keys": list(config.keys()),
                "has_values": {k: bool(v) for k, v in config.items()}
            }
        
        return summary

# Global configuration manager instance
config_manager = ConfigurationManager()

def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance"""
    return config_manager

def load_configuration() -> bool:
    """Load configuration"""
    return config_manager.load_configuration()

def validate_configuration() -> List[str]:
    """Validate configuration"""
    return config_manager.validate_configuration()

def get_config(section: str = None, key: str = None) -> Any:
    """Get configuration value"""
    return config_manager.get_config(section, key)
