import logging
from app.config.config import get_settings

# Configuración global del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ThreadFit")

settings = get_settings()