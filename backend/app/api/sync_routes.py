"""
Routes API pour la gestion de la synchronisation automatique Basecamp → Google Sheets
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.services.auto_sync_service import auto_sync_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/status", summary="Statut de la synchronisation", description="Obtient le statut du service de synchronisation automatique Basecamp ↔ Google Sheets")
async def get_sync_status() -> Dict[str, Any]:
    """
    Obtient le statut du service de synchronisation automatique

    Retourne des informations détaillées sur le service de synchronisation:
    - Statut actuel (actif/inactif)
    - Dernière synchronisation
    - Prochaine synchronisation programmée
    - Statistiques des synchronisations

    Returns:
        Dict contenant le statut et les métadonnées du service de sync
    """
    try:
        status = auto_sync_service.get_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Erreur récupération statut sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", summary="Synchronisation manuelle", description="Déclenche une synchronisation manuelle immédiate entre Basecamp et Google Sheets")
async def execute_manual_sync() -> Dict[str, Any]:
    """
    Exécute une synchronisation manuelle immédiate

    Lance une synchronisation complète entre Basecamp et Google Sheets:
    - Récupération des tâches Basecamp
    - Mise à jour des Google Sheets
    - Validation des données synchronisées
    - Rapport de synchronisation

    Returns:
        Dict contenant le résultat de la synchronisation et les statistiques
    """
    try:
        logger.info("Exécution synchronisation manuelle demandée via API")
        result = auto_sync_service.execute_sync()
        
        if result["success"]:
            return {
                "success": True,
                "message": "Synchronisation manuelle réussie",
                "data": result
            }
        else:
            return {
                "success": False,
                "message": "Échec de la synchronisation manuelle",
                "error": result.get("error", "Erreur inconnue"),
                "data": result
            }
            
    except Exception as e:
        logger.error(f"Erreur synchronisation manuelle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_auto_sync() -> Dict[str, Any]:
    """Démarre le service de synchronisation automatique"""
    try:
        if auto_sync_service.running:
            return {
                "success": True,
                "message": "Service de synchronisation déjà en cours"
            }
            
        auto_sync_service.start_scheduler()
        
        return {
            "success": True,
            "message": "Service de synchronisation automatique démarré"
        }
        
    except Exception as e:
        logger.error(f"Erreur démarrage service sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_auto_sync() -> Dict[str, Any]:
    """Arrête le service de synchronisation automatique"""
    try:
        if not auto_sync_service.running:
            return {
                "success": True,
                "message": "Service de synchronisation déjà arrêté"
            }
            
        auto_sync_service.stop_scheduler()
        
        return {
            "success": True,
            "message": "Service de synchronisation automatique arrêté"
        }
        
    except Exception as e:
        logger.error(f"Erreur arrêt service sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_sync_info() -> Dict[str, Any]:
    """Obtient les informations détaillées de synchronisation"""
    try:
        status = auto_sync_service.get_status()
        
        info = {
            "service_info": {
                "running": status["service_running"],
                "sync_count": status["sync_count"],
                "errors_count": status["errors_count"],
                "last_sync": status["last_sync"],
                "next_sync": status["next_sync"]
            },
            "configuration": {
                "script_path": status["script_path"],
                "script_exists": status["script_exists"],
                "frequency": "Every hour"
            }
        }
        
        return {
            "success": True,
            "data": info
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération infos sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))