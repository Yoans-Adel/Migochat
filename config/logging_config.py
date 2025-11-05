# Centralized Logging Configuration for Bww-AI-Assistant
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Setup centralized logging configuration"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Get current timestamp for log file naming
    timestamp = datetime.now().strftime("%Y%m%d")

    # Define log file paths
    log_files = {
        'app': logs_dir / f"app_{timestamp}.log",
        'error': logs_dir / f"error_{timestamp}.log",
        'debug': logs_dir / f"debug_{timestamp}.log",
        'access': logs_dir / f"access_{timestamp}.log",
        'ai': logs_dir / f"ai_{timestamp}.log",
        'database': logs_dir / f"database_{timestamp}.log",
        'webhook': logs_dir / f"webhook_{timestamp}.log",
        'messenger': logs_dir / f"messenger_{timestamp}.log",
        'whatsapp': logs_dir / f"whatsapp_{timestamp}.log"
    }

    # Create rotating file handlers for each log type
    handlers = {}

    # Main application log handler
    handlers['app'] = logging.handlers.RotatingFileHandler(
        log_files['app'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['app'].setLevel(logging.INFO)
    handlers['app'].setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Error log handler
    handlers['error'] = logging.handlers.RotatingFileHandler(
        log_files['error'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['error'].setLevel(logging.ERROR)
    handlers['error'].setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
    ))

    # Debug log handler
    handlers['debug'] = logging.handlers.RotatingFileHandler(
        log_files['debug'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['debug'].setLevel(logging.DEBUG)
    handlers['debug'].setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
    ))

    # Access log handler
    handlers['access'] = logging.handlers.RotatingFileHandler(
        log_files['access'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['access'].setLevel(logging.INFO)
    handlers['access'].setFormatter(logging.Formatter(
        '%(asctime)s - %(message)s'
    ))

    # AI service log handler
    handlers['ai'] = logging.handlers.RotatingFileHandler(
        log_files['ai'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['ai'].setLevel(logging.INFO)
    handlers['ai'].setFormatter(logging.Formatter(
        '%(asctime)s - AI_SERVICE - %(levelname)s - %(message)s'
    ))

    # Database log handler
    handlers['database'] = logging.handlers.RotatingFileHandler(
        log_files['database'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['database'].setLevel(logging.INFO)
    handlers['database'].setFormatter(logging.Formatter(
        '%(asctime)s - DATABASE - %(levelname)s - %(message)s'
    ))

    # Webhook log handler
    handlers['webhook'] = logging.handlers.RotatingFileHandler(
        log_files['webhook'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['webhook'].setLevel(logging.INFO)
    handlers['webhook'].setFormatter(logging.Formatter(
        '%(asctime)s - WEBHOOK - %(levelname)s - %(message)s'
    ))

    # Messenger log handler
    handlers['messenger'] = logging.handlers.RotatingFileHandler(
        log_files['messenger'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['messenger'].setLevel(logging.INFO)
    handlers['messenger'].setFormatter(logging.Formatter(
        '%(asctime)s - MESSENGER - %(levelname)s - %(message)s'
    ))

    # WhatsApp log handler
    handlers['whatsapp'] = logging.handlers.RotatingFileHandler(
        log_files['whatsapp'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handlers['whatsapp'].setLevel(logging.INFO)
    handlers['whatsapp'].setFormatter(logging.Formatter(
        '%(asctime)s - WHATSAPP - %(levelname)s - %(message)s'
    ))

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    # Add all handlers to root logger
    for handler in handlers.values():
        root_logger.addHandler(handler)
    root_logger.addHandler(console_handler)

    # Configure specific loggers for different components
    loggers_config = {
        'app.services.ai_service': ['ai'],
        'app.services.database_service': ['database'],
        'app.services.messenger_service': ['messenger'],
        'app.services.whatsapp_service': ['whatsapp'],
        'app.services.whatsapp_message_handler': ['whatsapp'],
        'app.routes.webhook': ['webhook'],
        'app.services.message_handler': ['messenger'],
        'app.services.facebook_lead_center_service': ['messenger'],
    }

    for logger_name, handler_names in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        for handler_name in handler_names:
            logger.addHandler(handlers[handler_name])
        logger.addHandler(console_handler)
        logger.propagate = False

    # Log the setup completion
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("🎯 Bww-AI-Assistant Logging System Initialized")
    logger.info("=" * 60)
    logger.info(f"📁 Logs directory: {logs_dir.absolute()}")
    logger.info("📋 Log files created:")
    for log_type, log_file in log_files.items():
        logger.info(f"   • {log_type}: {log_file.name}")
    logger.info("=" * 60)

    return handlers, log_files


def get_logger(name: str, log_type: str = 'app'):
    """Get a logger with specific configuration"""
    logger = logging.getLogger(name)

    # Add specific handler if log_type is specified
    if log_type != 'app':
        # This will be handled by the specific logger configuration above
        pass

    return logger


# Initialize logging when this module is imported
if __name__ != "__main__":
    setup_logging()
