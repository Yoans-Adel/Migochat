"""
Settings Manager Service
Manages application settings stored in database (Admin editable)
Falls back to environment variables if not in database
"""

import logging
import os
from typing import Optional, Dict, List
from datetime import datetime, timezone

from database import AppSettings, get_db_session

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    Manages application settings with database storage
    Priority: Database > Environment Variables > Defaults
    """
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 300  # 5 minutes
        
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_time:
            return False
        age = (datetime.now(timezone.utc) - self._cache_time).total_seconds()
        return age < self._cache_ttl
    
    def _load_from_database(self) -> Dict[str, str]:
        """Load all settings from database"""
        try:
            with get_db_session() as session:
                settings = session.query(AppSettings).all()
                return {s.key: s.value for s in settings if s.value}
        except Exception as e:
            logger.error(f"Error loading settings from database: {e}")
            return {}
    
    def _refresh_cache(self):
        """Refresh settings cache from database"""
        self._cache = self._load_from_database()
        self._cache_time = datetime.now(timezone.utc)
        logger.debug(f"Settings cache refreshed with {len(self._cache)} entries")
    
    def get_setting(self, key: str, default: str = "") -> str:
        """
        Get setting value with priority: Database > Environment > Default
        
        Args:
            key: Setting key (e.g., 'GEMINI_API_KEY', 'WHATSAPP_ACCESS_TOKEN')
            default: Default value if not found
            
        Returns:
            Setting value
        """
        # Refresh cache if needed
        if not self._is_cache_valid():
            self._refresh_cache()
        
        # 1. Try database cache
        if key in self._cache:
            return self._cache[key]
        
        # 2. Try environment variable
        env_value = os.getenv(key, "")
        if env_value:
            return env_value
        
        # 3. Return default
        return default
    
    def set_setting(
        self,
        key: str,
        value: str,
        category: str = "system",
        is_sensitive: bool = False,
        description: str = "",
        updated_by: str = "admin"
    ) -> bool:
        """
        Set or update a setting in database
        
        Args:
            key: Setting key
            value: Setting value
            category: Category (facebook, whatsapp, ai, system)
            is_sensitive: Whether it's sensitive (API key/token)
            description: Human-readable description
            updated_by: Who updated it
            
        Returns:
            Success status
        """
        try:
            with get_db_session() as session:
                # Check if setting exists
                setting = session.query(AppSettings).filter(AppSettings.key == key).first()
                
                if setting:
                    # Update existing
                    setting.value = value
                    setting.updated_at = datetime.now(timezone.utc)
                    setting.updated_by = updated_by
                    logger.info(f"Updated setting: {key}")
                else:
                    # Create new
                    setting = AppSettings(
                        key=key,
                        value=value,
                        category=category,
                        is_sensitive=is_sensitive,
                        description=description,
                        updated_by=updated_by
                    )
                    session.add(setting)
                    logger.info(f"Created new setting: {key}")
                
                session.commit()
                
                # Invalidate cache
                self._cache_time = None
                
                return True
                
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False
    
    def get_all_settings(self, category: Optional[str] = None) -> List[Dict]:
        """
        Get all settings, optionally filtered by category
        
        Args:
            category: Filter by category (facebook, whatsapp, ai, system)
            
        Returns:
            List of settings as dictionaries
        """
        try:
            with get_db_session() as session:
                query = session.query(AppSettings)
                
                if category:
                    query = query.filter(AppSettings.category == category)
                
                settings = query.all()
                
                return [
                    {
                        "key": s.key,
                        "value": s.value if not s.is_sensitive else "***" + s.value[-4:] if len(s.value) > 4 else "***",
                        "value_full": s.value,  # For editing
                        "category": s.category,
                        "is_sensitive": s.is_sensitive,
                        "description": s.description,
                        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                        "updated_by": s.updated_by
                    }
                    for s in settings
                ]
                
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return []
    
    def delete_setting(self, key: str) -> bool:
        """Delete a setting from database"""
        try:
            with get_db_session() as session:
                setting = session.query(AppSettings).filter(AppSettings.key == key).first()
                
                if setting:
                    session.delete(setting)
                    session.commit()
                    logger.info(f"Deleted setting: {key}")
                    
                    # Invalidate cache
                    self._cache_time = None
                    
                    return True
                else:
                    logger.warning(f"Setting not found: {key}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting setting {key}: {e}")
            return False
    
    def initialize_default_settings(self):
        """Initialize default settings from environment variables"""
        default_settings = [
            # Facebook
            ("FB_PAGE_ACCESS_TOKEN", os.getenv("FB_PAGE_ACCESS_TOKEN", ""), "facebook", True, "Facebook Page Access Token"),
            ("FB_APP_ID", os.getenv("FB_APP_ID", ""), "facebook", False, "Facebook App ID"),
            ("FB_APP_SECRET", os.getenv("FB_APP_SECRET", ""), "facebook", True, "Facebook App Secret"),
            ("FB_PAGE_ID", os.getenv("FB_PAGE_ID", ""), "facebook", False, "Facebook Page ID"),
            ("FB_VERIFY_TOKEN", os.getenv("FB_VERIFY_TOKEN", ""), "facebook", True, "Facebook Webhook Verify Token"),
            
            # WhatsApp
            ("WHATSAPP_ACCESS_TOKEN", os.getenv("WHATSAPP_ACCESS_TOKEN", ""), "whatsapp", True, "WhatsApp Business API Access Token"),
            ("WHATSAPP_PHONE_NUMBER_ID", os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""), "whatsapp", False, "WhatsApp Phone Number ID"),
            ("WHATSAPP_VERIFY_TOKEN", os.getenv("WHATSAPP_VERIFY_TOKEN", ""), "whatsapp", True, "WhatsApp Webhook Verify Token"),
            
            # AI
            ("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""), "ai", True, "Google Gemini API Key"),
        ]
        
        for key, value, category, is_sensitive, description in default_settings:
            if value:  # Only set if has value from environment
                existing = self.get_setting(key)
                if not existing:  # Don't override existing DB settings
                    self.set_setting(
                        key=key,
                        value=value,
                        category=category,
                        is_sensitive=is_sensitive,
                        description=description,
                        updated_by="system"
                    )
        
        logger.info("Default settings initialized from environment")


# Global instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get or create global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
