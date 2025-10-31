import os, sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

from config.logging_config import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

logger.info("Starting BWW Assistant Server")

import uvicorn
from app.config import settings

uvicorn.run(
    "app.main:app",
    host=settings.HOST,
    port=settings.PORT,
    reload=settings.DEBUG
)
