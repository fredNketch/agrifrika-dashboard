"""
Routes de santé et diagnostic pour AGRIFRIKA Dashboard API
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.dashboard_models import HealthResponse, APIResponse
from app.services import FacebookService, GoogleSheetsService, BasecampService, CashFlowService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Instances des services pour les tests de santé
facebook_service = FacebookService()
sheets_service = GoogleSheetsService()
basecamp_service = BasecampService()
cashflow_service = CashFlowService()

@router.get("/", response_model=HealthResponse, summary="Health Check", description="Vérification rapide de l'état de santé de l'API et des services externes")
async def health_check():
    """
    Endpoint de vérification de santé de l'API

    Retourne le statut de l'API et de tous les services connectés:
    - Facebook API pour les métriques d'engagement
    - Google Sheets API pour les données de planification
    - Basecamp API pour les tâches et projets
    - Service de cash flow interne

    Returns:
        HealthResponse: Statut global et détail par service
    """
    
    # Test de santé de chaque service
    apis_status = {
        "facebook": facebook_service.health_check(),
        "google_sheets": sheets_service.health_check(),
        "basecamp": basecamp_service.health_check(),
        "cash_flow": cashflow_service.health_check()
    }
    
    # Statut global
    all_healthy = all(apis_status.values())
    status = "healthy" if all_healthy else "degraded"
    
    logger.info(f"Health check: {status} - APIs: {apis_status}")
    
    return HealthResponse(
        status=status,
        version="1.0.0",
        uptime=0.0,  # Pourrait être calculé réellement
        apis_status=apis_status,
        timestamp=datetime.now()
    )

@router.get("/detailed", response_model=APIResponse, summary="Diagnostic détaillé", description="Diagnostic complet avec validation des credentials et informations système")
async def detailed_health_check():
    """
    Endpoint de vérification détaillée incluant la validation des credentials

    Effectue un diagnostic complet comprenant:
    - Test de connectivité de chaque service externe
    - Validation de la configuration des credentials
    - Informations système et configuration
    - Statut des chemins de fichiers de credentials

    Returns:
        APIResponse: Diagnostic complet avec détails techniques
    """
    
    try:
        # Validation des credentials
        credentials_validation = settings.validate_credentials()
        
        # Test de connectivité de chaque service
        service_tests = {
            "facebook": {
                "configured": credentials_validation["facebook"],
                "connected": facebook_service.health_check() if credentials_validation["facebook"] else False
            },
            "google_sheets": {
                "configured": credentials_validation["google_sheets"],
                "connected": sheets_service.health_check() if credentials_validation["google_sheets"] else False
            },
            "basecamp": {
                "configured": credentials_validation["basecamp"],
                "connected": basecamp_service.health_check() if credentials_validation["basecamp"] else False
            },
            "cash_flow": {
                "configured": True,  # Service interne
                "connected": cashflow_service.health_check()
            }
        }
        
        # Configuration système
        system_info = {
            "debug_mode": settings.DEBUG,
            "cors_origins": settings.CORS_ORIGINS,
            "cache_ttl": settings.CACHE_TTL_SECONDS,
            "credentials_paths": {
                "ga_credentials": settings.ga_credentials_full_path,
                "sheets_credentials": settings.sheets_credentials_full_path
            }
        }
        
        return APIResponse(
            success=True,
            data={
                "services": service_tests,
                "system": system_info,
                "credentials_validation": credentials_validation
            },
            message="Diagnostic complet effectué"
        )
        
    except Exception as e:
        logger.error(f"Erreur diagnostic détaillé: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credentials", response_model=APIResponse, summary="Vérification des credentials", description="Vérifie la présence et validité des credentials pour tous les services externes")
async def check_credentials():
    """
    Endpoint pour vérifier la configuration des credentials

    Vérifie la présence et la validité des fichiers de credentials pour:
    - Google Analytics API
    - Google Sheets API
    - Basecamp API tokens
    - Facebook API tokens

    Returns:
        APIResponse: Statut de validation pour chaque service
    """
    
    try:
        validation = settings.validate_credentials()
        
        missing_credentials = [
            api for api, valid in validation.items() 
            if not valid
        ]
        
        if missing_credentials:
            return APIResponse(
                success=False,
                data={
                    "validation": validation,
                    "missing": missing_credentials
                },
                message=f"Credentials manquants pour: {', '.join(missing_credentials)}"
            )
        else:
            return APIResponse(
                success=True,
                data={"validation": validation},
                message="Tous les credentials sont configurés"
            )
            
    except Exception as e:
        logger.error(f"Erreur vérification credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))