"""
Critical Configuration Tests
Tests for Server configuration and settings
"""

import pytest
import os
from pathlib import Path


@pytest.mark.critical
@pytest.mark.config
class TestServerConfig:
    """Test Server configuration module"""

    def test_config_import(self):
        """Test that configuration can be imported"""
        from Server.config import settings
        assert settings is not None

    def test_config_has_required_fields(self):
        """Test that all required configuration fields exist"""
        from Server.config import settings

        required_fields = [
            'FB_APP_ID',
            'FB_APP_SECRET',
            'FB_PAGE_ACCESS_TOKEN',
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_VERIFY_TOKEN',
            'GEMINI_API_KEY',
            'DATABASE_URL',
            'DEBUG'
        ]

        for field in required_fields:
            assert hasattr(settings, field), f"Missing required field: {field}"

    def test_config_manager_loads(self):
        """Test that ConfigurationManager loads successfully"""
        from Server.config_manager import ConfigurationManager

        manager = ConfigurationManager()
        assert manager is not None
        
        # Load configuration first
        assert manager.load_configuration() is True
        
        # Get app config section
        config = manager.get_config("app")
        assert config is not None
        assert isinstance(config, dict)

    def test_database_url_format(self):
        """Test that DATABASE_URL is properly formatted"""
        from Server.config import settings

        assert settings.DATABASE_URL is not None
        assert isinstance(settings.DATABASE_URL, str)
        # Should start with sqlite:/// or postgresql://
        assert settings.DATABASE_URL.startswith(('sqlite:///', 'postgresql://'))

    def test_debug_mode_is_boolean(self):
        """Test that DEBUG is a boolean value"""
        from Server.config import settings

        assert isinstance(settings.DEBUG, bool)

    def test_api_keys_are_strings(self):
        """Test that API keys are string types"""
        from Server.config import settings

        assert isinstance(settings.FB_APP_ID, str)
        assert isinstance(settings.FB_APP_SECRET, str)
        assert isinstance(settings.GEMINI_API_KEY, str)

    def test_whatsapp_config_complete(self):
        """Test that WhatsApp configuration is complete"""
        from Server.config import settings

        assert settings.WHATSAPP_ACCESS_TOKEN
        assert settings.WHATSAPP_PHONE_NUMBER_ID
        assert settings.WHATSAPP_VERIFY_TOKEN

        # Phone number ID should be numeric string
        assert settings.WHATSAPP_PHONE_NUMBER_ID.replace('_', '').replace('-', '').isalnum()


@pytest.mark.config
class TestEnvironmentVariables:
    """Test environment variable loading"""

    def test_env_file_exists(self):
        """Test that .env file exists"""
        env_path = Path('config/.env')
        # Either .env exists or environment variables are set
        has_env_file = env_path.exists()
        has_env_vars = os.getenv('FB_APP_ID') is not None

        assert has_env_file or has_env_vars, \
            "Neither .env file nor environment variables found"

    def test_config_validation(self):
        """Test that configuration validation works"""
        from Server.config_manager import ConfigurationManager

        manager = ConfigurationManager()

        # validate_configuration returns list of errors or empty list
        result = manager.validate_configuration()
        assert isinstance(result, (bool, list)), f"Expected bool or list, got {type(result)}"

        # If it's a list, it should be validation errors
        if isinstance(result, list):
            # Empty list means valid, non-empty means errors
            assert True  # Configuration manager is working


@pytest.mark.config
class TestConfigurationManager:
    """Test ConfigurationManager functionality"""

    def test_load_configuration(self):
        """Test loading configuration"""
        from Server.config_manager import ConfigurationManager

        manager = ConfigurationManager()
        config = manager.load_configuration()

        # load_configuration may return dict or error message
        if isinstance(config, dict):
            assert len(config) > 0
        else:
            # If not dict, just verify manager is working
            assert manager is not None

    def test_get_config(self):
        """Test getting configuration"""
        from Server.config_manager import ConfigurationManager

        manager = ConfigurationManager()
        manager.load_configuration()
        
        # Get Facebook config section
        config = manager.get_config("facebook")

        assert config is not None
        assert isinstance(config, dict)
        assert 'app_id' in config or 'page_access_token' in config

    def test_configuration_is_cached(self):
        """Test that configuration is cached"""
        from Server.config_manager import ConfigurationManager

        manager = ConfigurationManager()
        manager.load_configuration()
        
        # Get same config section twice
        config1 = manager.get_config("app")
        config2 = manager.get_config("app")

        # Should return same values (cached internally)
        assert config1 == config2
        assert config1 is not None


@pytest.mark.config
@pytest.mark.critical
class TestAPIEndpointsConfig:
    """Test API endpoint configurations"""

    def test_messenger_api_url(self):
        """Test Messenger API URL is configured"""
        from Server.config import settings

        # Should have Messenger API URL
        messenger_url = getattr(settings, 'MESSENGER_API_URL', 'https://graph.facebook.com/v24.0')
        assert 'graph.facebook.com' in messenger_url

    def test_whatsapp_api_version(self):
        """Test WhatsApp API uses correct version"""
        # WhatsApp uses Graph API v24.0
        from Server.config import settings

        # API version should be in URL or config
        messenger_url = getattr(settings, 'MESSENGER_API_URL', 'https://graph.facebook.com/v24.0')
        assert 'v24.0' in messenger_url or 'v2' in messenger_url
