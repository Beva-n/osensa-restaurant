# backend/app/logger.py
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO",
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                  "<level>{level: <8}</level> | "
                  "{message}")
