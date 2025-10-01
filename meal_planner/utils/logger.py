"""
Configuration du système de logging
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "meal_planner",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configure et retourne un logger pour l'application.

    Args:
        name: Nom du logger
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin du fichier de log (optionnel)
        format_string: Format personnalisé des messages de log

    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)

    # Éviter la duplication des handlers si le logger existe déjà
    if logger.handlers:
        return logger

    # Définir le niveau de log
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Format par défaut
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)

    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler pour le fichier (si spécifié)
    if log_file:
        try:
            # Créer le répertoire parent si nécessaire
            log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Impossible de créer le fichier de log {log_file}: {e}")

    return logger


def get_logger(name: str = "meal_planner") -> logging.Logger:
    """
    Retourne un logger existant ou en crée un nouveau.

    Args:
        name: Nom du logger

    Returns:
        Logger
    """
    return logging.getLogger(name)
