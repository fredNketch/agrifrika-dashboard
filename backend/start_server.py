#!/usr/bin/env python3
"""
Script de démarrage du serveur AGRIFRIKA Dashboard API
"""

import uvicorn
import logging
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    # Configuration des logs
    log_level = "debug" if settings.DEBUG else "info"
    
    print("AGRIFRIKA Dashboard API")
    print(f"Mode: {'Development' if settings.DEBUG else 'Production'}")
    print(f"Host: {settings.HOST}:{settings.PORT}")
    print(f"CORS: {settings.CORS_ORIGINS}")
    print("=" * 50)
    
    # Démarrage du serveur
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=log_level,
        access_log=settings.DEBUG,
        reload_dirs=["app"] if settings.DEBUG else None
    )