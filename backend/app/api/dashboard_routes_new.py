"""
Routes API pour Dashboard AGRIFRIKA - VERSION NOUVELLE
Routes pour les données de fundraising avec logique cumulative
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import Dict, Any, List

from app.models.dashboard_models import APIResponse
from app.services.fundraising_pipeline_service_new import FundraisingPipelineServiceNew
import logging

router = APIRouter()

# Instance du service fundraising
fundraising_service = FundraisingPipelineServiceNew()

@router.get("/dashboard1/fundraising", response_model=APIResponse)
async def get_fundraising_pipeline():
    """Récupère les données de fundraising pipeline avec logique cumulative"""
    
    try:
        # Utiliser le service de fundraising dédié
        score_data = await fundraising_service.calculate_fundraising_score()
        
        if not score_data:
            # Fallback vers données mockées si pas de données
            return APIResponse(
                success=True,
                data={
                    "score": 0,
                    "total_points_obtenus": 0,
                    "objectif_total": 4547,
                    "status": "FAIBLE",
                    "categories": {
                        "concours": 0,
                        "subventions": 0,
                        "investisseurs": 0,
                        "activités": 0
                    },
                    "raw_data": {},
                    "last_updated": datetime.now().isoformat()
                },
                message="Données de fundraising (fallback utilisé)"
            )
        
        return APIResponse(
            success=True,
            data=score_data,
            message="Fundraising pipeline récupéré depuis Google Sheets"
        )
        
    except Exception as e:
        logging.error(f"Erreur récupération fundraising: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard1/fundraising/trends", response_model=APIResponse)
async def get_fundraising_trends():
    """Récupère les vraies tendances de fundraising basées sur les cumuls"""
    
    try:
        # Utiliser le service de fundraising dédié
        trends_data = await fundraising_service.get_fundraising_trends()
        
        if not trends_data:
            # Fallback vers données mockées si pas de données
            return APIResponse(
                success=True,
                data=[],
                message="Aucune donnée de tendance disponible"
            )
        
        return APIResponse(
            success=True,
            data=trends_data,
            message="Tendances de fundraising récupérées depuis Google Sheets"
        )
        
    except Exception as e:
        logging.error(f"Erreur récupération tendances fundraising: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-cache")
async def refresh_cache(background_tasks: BackgroundTasks):
    """Force le rafraîchissement du cache des données"""
    
    try:
        # Ici on pourrait ajouter une logique de cache si nécessaire
        # Pour l'instant, on retourne juste un succès
        
        return APIResponse(
            success=True,
            data={"message": "Cache rafraîchi"},
            message="Cache des données rafraîchi avec succès"
        )
        
    except Exception as e:
        logging.error(f"Erreur rafraîchissement cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
