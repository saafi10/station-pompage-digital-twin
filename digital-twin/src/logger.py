# digital-twin/src/logger.py
"""Configuration centralisée du logging - fichier avec rotation + console."""

import logging
import os
from logging.handlers import RotatingFileHandler

from src.config import settings


def setup_logging() -> logging.Logger:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    # Console
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    # Fichier avec rotation (5 Mo x 3 fichiers), best-effort si /app/data indisponible
    try:
        os.makedirs(settings.log_dir, exist_ok=True)
        file_path = os.path.join(settings.log_dir, settings.log_file)
        file_handler = RotatingFileHandler(file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except OSError as e:
        root.warning(f"Impossible d'écrire les logs sur disque ({e}) — console uniquement")

    return logging.getLogger("digital-twin")