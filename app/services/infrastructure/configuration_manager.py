"""
Service Configuration Management for BWW Assistant Chatbot
Professional configuration system with validation and hot-reloading
"""

import logging
import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime, timezone
import threading
# Note: watchdog is optional for hot-reload (install via: pip install -r tests/requirements-test.txt)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    WATCHDOG_AVAILABLE = False

from app.services.core.interfaces import ServiceConfig, ConfigurationServiceInterface

logger = logging.getLogger(__name__)

class ConfigFormat(Enum):
    """Configuration format enumeration"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    INI = "ini"

@dataclass
class ServiceConfiguration:
    """Service configuration with validation"""
    name: str
    enabled: bool = True
    timeout: int = 30
    retry_count: int = 3
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    environment: str = "development"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> List[str]:
        """Validate configuration"""
        errors = []

        if not self.name:
            errors.append("Service name is required")

        if self.timeout <= 0:
            errors.append("Timeout must be positive")

        if self.retry_count < 0:
            errors.append("Retry count cannot be negative")

        return errors

    def to_service_config(self) -> ServiceConfig:
        """Convert to ServiceConfig"""
        return ServiceConfig(
            name=self.name,
            enabled=self.enabled,
            timeout=self.timeout,
            retry_count=self.retry_count,
            dependencies=self.dependencies,
            config=self.config
        )

class ConfigurationValidator:
    """Configuration validation system"""

    def __init__(self):
        self._validators: Dict[str, callable] = {}
        self._logger = logging.getLogger(__name__)

    def register_validator(self, service_type: str, validator: callable) -> None:
        """Register service-specific validator"""
        self._validators[service_type] = validator
        self._logger.info(f"Registered validator for service type '{service_type}'")

    def validate_service_config(self, service_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate service configuration"""
        errors = []

        # Basic validation
        if not isinstance(config, dict):
            errors.append("Configuration must be a dictionary")
            return errors

        # Service-specific validation
        if service_type in self._validators:
            try:
                validator_errors = self._validators[service_type](config)
                if validator_errors:
                    errors.extend(validator_errors)
            except Exception as e:
                errors.append(f"Validation error: {e}")

        return errors

class ConfigurationLoader:
    """Configuration loading system"""

    def __init__(self):
        self._loaders: Dict[ConfigFormat, callable] = {
            ConfigFormat.JSON: self._load_json,
            ConfigFormat.YAML: self._load_yaml,
            ConfigFormat.ENV: self._load_env,
            ConfigFormat.INI: self._load_ini
        }
        self._logger = logging.getLogger(__name__)

    def load_config(self, file_path: Union[str, Path], format_type: ConfigFormat) -> Dict[str, Any]:
        """Load configuration from file"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        if format_type not in self._loaders:
            raise ValueError(f"Unsupported configuration format: {format_type}")

        try:
            loader = self._loaders[format_type]
            config = loader(file_path)
            self._logger.info(f"Loaded configuration from {file_path}")
            return config
        except Exception as e:
            self._logger.error(f"Failed to load configuration from {file_path}: {e}")
            raise

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON configuration"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_env(self, file_path: Path) -> Dict[str, Any]:
        """Load environment configuration"""
        config = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        return config

    def _load_ini(self, file_path: Path) -> Dict[str, Any]:
        """Load INI configuration"""
        import configparser
        config = configparser.ConfigParser()
        config.read(file_path)

        result = {}
        for section in config.sections():
            result[section] = dict(config[section])

        return result

class ConfigurationWatcher:
    """Configuration file watcher for hot-reloading (requires watchdog package)"""

    def __init__(self, config_manager: 'ConfigurationManager'):
        if not WATCHDOG_AVAILABLE or not FileSystemEventHandler:
            raise ImportError("watchdog package not installed. Install via: pip install -r tests/requirements-test.txt")

        # Dynamically create the event handler class
        class Handler(FileSystemEventHandler):
            def __init__(self, manager):
                self.config_manager = manager
                self.logger = logging.getLogger(__name__)

            def on_modified(self, event):
                """Handle file modification"""
                if not event.is_directory and event.src_path.endswith(('.json', '.yaml', '.yml', '.env', '.ini')):
                    self.logger.info(f"Configuration file modified: {event.src_path}")
                    try:
                        self.config_manager.reload_config()
                    except Exception as e:
                        self.logger.error(f"Failed to reload configuration: {e}")

        self.handler = Handler(config_manager)

    def get_handler(self):
        """Get the file system event handler"""
        return self.handler

class ConfigurationManager(ConfigurationServiceInterface):
    """Professional configuration management system"""

    def __init__(self, config_dir: Optional[str] = None):
        self._config_dir = Path(config_dir) if config_dir else Path("config")
        self._config_dir.mkdir(exist_ok=True)

        self._configurations: Dict[str, ServiceConfiguration] = {}
        self._global_config: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)

        self._loader = ConfigurationLoader()
        self._validator = ConfigurationValidator()
        self._observer = None
        self._watch_enabled = False

        # Load initial configuration
        self._load_all_configurations()

    def _load_all_configurations(self) -> None:
        """Load all configuration files"""
        try:
            # Load global configuration
            global_config_file = self._config_dir / "global.json"
            if global_config_file.exists():
                self._global_config = self._loader.load_config(global_config_file, ConfigFormat.JSON)

            # Load service configurations
            for config_file in self._config_dir.glob("services/*.json"):
                service_name = config_file.stem
                try:
                    config_data = self._loader.load_config(config_file, ConfigFormat.JSON)
                    service_config = ServiceConfiguration(
                        name=service_name,
                        **config_data
                    )

                    # Validate configuration
                    errors = service_config.validate()
                    if errors:
                        self._logger.error(f"Configuration validation errors for {service_name}: {errors}")
                        continue

                    self._configurations[service_name] = service_config
                    self._logger.info(f"Loaded configuration for service '{service_name}'")

                except Exception as e:
                    self._logger.error(f"Failed to load configuration for service '{service_name}': {e}")

        except Exception as e:
            self._logger.error(f"Failed to load configurations: {e}")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        with self._lock:
            # Check service-specific configuration first
            if '.' in key:
                service_name, config_key = key.split('.', 1)
                if service_name in self._configurations:
                    return self._configurations[service_name].config.get(config_key, default)

            # Check global configuration
            return self._global_config.get(key, default)

    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        with self._lock:
            try:
                if '.' in key:
                    service_name, config_key = key.split('.', 1)
                    if service_name not in self._configurations:
                        # Create new service configuration
                        self._configurations[service_name] = ServiceConfiguration(name=service_name)

                    self._configurations[service_name].config[config_key] = value
                    self._configurations[service_name].updated_at = datetime.now(timezone.utc)
                else:
                    self._global_config[key] = value

                self._logger.info(f"Set configuration '{key}' = '{value}'")
                return True

            except Exception as e:
                self._logger.error(f"Failed to set configuration '{key}': {e}")
                return False

    def reload_config(self) -> bool:
        """Reload all configurations"""
        with self._lock:
            try:
                self._load_all_configurations()
                self._logger.info("Configuration reloaded successfully")
                return True
            except Exception as e:
                self._logger.error(f"Failed to reload configuration: {e}")
                return False

    def get_service_config(self, service_name: str) -> Optional[ServiceConfiguration]:
        """Get service configuration"""
        with self._lock:
            return self._configurations.get(service_name)

    def set_service_config(self, service_name: str, config: ServiceConfiguration) -> bool:
        """Set service configuration"""
        with self._lock:
            try:
                # Validate configuration
                errors = config.validate()
                if errors:
                    self._logger.error(f"Configuration validation errors: {errors}")
                    return False

                config.updated_at = datetime.now(timezone.utc)
                self._configurations[service_name] = config

                # Save to file
                self._save_service_config(service_name, config)

                self._logger.info(f"Set configuration for service '{service_name}'")
                return True

            except Exception as e:
                self._logger.error(f"Failed to set service configuration '{service_name}': {e}")
                return False

    def _save_service_config(self, service_name: str, config: ServiceConfiguration) -> None:
        """Save service configuration to file"""
        services_dir = self._config_dir / "services"
        services_dir.mkdir(exist_ok=True)

        config_file = services_dir / f"{service_name}.json"

        config_data = {
            "enabled": config.enabled,
            "timeout": config.timeout,
            "retry_count": config.retry_count,
            "dependencies": config.dependencies,
            "config": config.config,
            "environment": config.environment,
            "version": config.version
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def enable_config_watching(self) -> None:
        """Enable configuration file watching (requires watchdog package)"""
        if self._watch_enabled:
            return

        if not WATCHDOG_AVAILABLE:
            self._logger.warning(
                "Configuration watching disabled - watchdog package not installed. "
                "Install via: pip install -r tests/requirements-test.txt"
            )
            return

        try:
            watcher = ConfigurationWatcher(self)
            self._observer = Observer()
            self._observer.schedule(watcher.get_handler(), str(self._config_dir), recursive=True)
            self._observer.start()
            self._watch_enabled = True
            self._logger.info("Configuration watching enabled")
        except Exception as e:
            self._logger.error(f"Failed to enable configuration watching: {e}")

    def disable_config_watching(self) -> None:
        """Disable configuration file watching"""
        if not self._watch_enabled or not self._observer:
            return

        try:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            self._watch_enabled = False
            self._logger.info("Configuration watching disabled")
        except Exception as e:
            self._logger.error(f"Failed to disable configuration watching: {e}")

    def get_all_configurations(self) -> Dict[str, ServiceConfiguration]:
        """Get all service configurations"""
        with self._lock:
            return self._configurations.copy()

    def register_validator(self, service_type: str, validator: callable) -> None:
        """Register service-specific validator"""
        self._validator.register_validator(service_type, validator)

    def validate_service_config(self, service_type: str, config: Dict[str, Any]) -> List[str]:
        """Validate service configuration"""
        return self._validator.validate_service_config(service_type, config)

    def initialize(self) -> bool:
        """Initialize configuration manager"""
        try:
            # Enable hot-reloading if watchdog is available
            self.enable_config_watching()

            status = "with hot-reload" if self._watch_enabled else "without hot-reload"
            self._logger.info(f"Configuration manager initialized successfully ({status})")
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize configuration manager: {e}")
            return False

    def shutdown(self) -> None:
        """Shutdown configuration manager"""
        self.disable_config_watching()
        self._logger.info("Configuration manager shutdown")

    def get_service_status(self) -> Dict[str, Any]:
        """Get configuration manager status"""
        with self._lock:
            return {
                "service_name": "ConfigurationManager",
                "initialized": True,
                "config_dir": str(self._config_dir),
                "watch_enabled": self._watch_enabled,
                "services_count": len(self._configurations),
                "global_config_keys": list(self._global_config.keys()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def health_check(self) -> Any:
        """Configuration manager health check"""
        try:
            return {
                "status": "healthy",
                "message": "Configuration manager is healthy",
                "timestamp": datetime.now(timezone.utc),
                "metrics": {
                    "services_count": len(self._configurations),
                    "watch_enabled": self._watch_enabled
                },
                "dependencies": []
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Configuration manager error: {e}",
                "timestamp": datetime.now(timezone.utc),
                "metrics": {},
                "dependencies": []
            }

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None
_config_lock = threading.Lock()

def get_config_manager(config_dir: Optional[str] = None) -> ConfigurationManager:
    """Get global configuration manager"""
    global _config_manager

    if _config_manager is None:
        with _config_lock:
            if _config_manager is None:
                _config_manager = ConfigurationManager(config_dir)

    return _config_manager

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value from global manager"""
    return get_config_manager().get_config(key, default)

def set_config(key: str, value: Any) -> bool:
    """Set configuration value in global manager"""
    return get_config_manager().set_config(key, value)

def get_service_config(service_name: str) -> Optional[ServiceConfiguration]:
    """Get service configuration from global manager"""
    return get_config_manager().get_service_config(service_name)

def shutdown_config_manager() -> None:
    """Shutdown global configuration manager"""
    global _config_manager
    if _config_manager:
        _config_manager.shutdown()
        _config_manager = None
