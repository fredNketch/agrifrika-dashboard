"""
AGRIFRIKA Dashboard Backend API
Point d'entrée principal de l'application FastAPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

from app.core.config import settings
from app.api import dashboard_routes, health_routes, sync_routes
from app.utils.logger import setup_logging
from app.services.auto_sync_service import auto_sync_service

# Configuration des logs
setup_logging()
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="AGRIFRIKA Dashboard API",
    description="""
    API Backend pour les dashboards AGRIFRIKA - Récupération des données KPI

    ## Fonctionnalités principales

    * **Dashboard 1**: Métriques financières et KPIs de croissance
    * **Dashboard 2**: Données opérationnelles et disponibilité équipe
    * **Synchronisation**: Sync automatique Basecamp ↔ Google Sheets
    * **Monitoring**: Health checks et métriques système

    ## Authentification

    L'API utilise des tokens d'accès pour les services externes:
    - Google Sheets API pour les données de planification
    - Basecamp API pour les tâches et projets
    - Facebook API pour les métriques d'engagement

    ## Endpoints principaux

    * `/api/v1/dashboard1/*` - Données financières et KPIs
    * `/api/v1/dashboard2/*` - Données opérationnelles
    * `/api/v1/sync/*` - Synchronisation des données
    * `/health` - Monitoring et santé de l'API
    """,
    version="1.0.0",
    contact={
        "name": "AGRIFRIKA Tech Team",
        "url": "https://agrifrika.com",
        "email": "tech@agrifrika.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "health",
            "description": "Endpoints de monitoring et santé de l'API"
        },
        {
            "name": "dashboard",
            "description": "Endpoints pour les données des dashboards"
        },
        {
            "name": "synchronization",
            "description": "Endpoints de synchronisation des données"
        }
    ]
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Routes principales
app.include_router(health_routes.router, prefix="/health", tags=["health"])
app.include_router(dashboard_routes.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(sync_routes.router, prefix="/api/v1/sync", tags=["synchronization"])

@app.on_event("startup")
async def startup_event():
    """Actions à effectuer au démarrage de l'application"""
    logger.info("[STARTUP] AGRIFRIKA Dashboard API - Démarrage")
    logger.info(f"[DEBUG] Mode DEBUG: {settings.DEBUG}")
    logger.info(f"[CORS] Origins autorisées: {settings.CORS_ORIGINS}")
    
    # Démarrer la synchronisation automatique Basecamp → Google Sheets
    try:
        auto_sync_service.start_scheduler()
        logger.info("[SYNC] Service de synchronisation automatique démarré - toutes les heures")
    except Exception as e:
        logger.error(f"[SYNC] Erreur démarrage synchronisation automatique: {e}")
    
@app.on_event("shutdown") 
async def shutdown_event():
    """Actions à effectuer à l'arrêt de l'application"""
    logger.info("[SHUTDOWN] AGRIFRIKA Dashboard API - Arrêt")
    
    # Arrêter la synchronisation automatique
    try:
        auto_sync_service.stop_scheduler()
        logger.info("[SYNC] Service de synchronisation automatique arrêté")
    except Exception as e:
        logger.error(f"[SYNC] Erreur arrêt synchronisation automatique: {e}")

@app.get("/", summary="API Root", description="Informations générales sur l'API AGRIFRIKA Dashboard")
async def root():
    """
    Route racine - Information sur l'API

    Retourne les informations de base sur l'API:
    - Version actuelle
    - Statut de fonctionnement
    - Lien vers la documentation
    - Timestamp de la réponse

    Returns:
        Dict contenant les informations de base de l'API
    """
    return {
        "message": "AGRIFRIKA Dashboard API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health_check": "/health",
        "api_version": "/api/v1"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire global des erreurs HTTP"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire global des erreurs générales"""
    logger.error(f"Erreur inattendue: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )