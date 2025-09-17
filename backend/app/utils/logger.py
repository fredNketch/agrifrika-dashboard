"""
Configuration du système de logs pour AGRIFRIKA Dashboard
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(log_level: str = "INFO") -> None:
    """Configure le système de logging de l'application"""
    
    # Créer le dossier logs s'il n'existe pas
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configuration du format des logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configuration du logger racine
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(
                log_dir / f"agrifrika_dashboard_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
        ]
    )
    
    # Réduire le niveau de log des bibliothèques externes
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    
    # Logger principal de l'application
    logger = logging.getLogger("agrifrika_dashboard")
    logger.info("[INIT] Système de logging initialisé")
    
    return logger