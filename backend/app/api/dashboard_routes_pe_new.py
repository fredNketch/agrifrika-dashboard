"""
Routes API pour le dashboard avec nouveau service Public Engagement
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List
from app.services.public_engagement_service_new import PublicEngagementServiceNew

logger = logging.getLogger(__name__)
router = APIRouter()

# Instance du service
pe_service = PublicEngagementServiceNew()

@router.get("/dashboard1/public-engagement")
async def get_public_engagement_data() -> Optional[Dict[str, Any]]:
    """Récupère les données d'engagement public avec le nouveau service"""
    try:
        logger.info("Récupération des données d'engagement public (nouveau service)")
        
        # Récupérer les données d'engagement
        engagement_data = await pe_service.get_engagement_data()
        if not engagement_data:
            logger.warning("Aucune donnée d'engagement trouvée")
            return None
        
        # Récupérer le score calculé
        score_result = await pe_service.calculate_engagement_score()
        if not score_result:
            logger.warning("Impossible de calculer le score d'engagement")
            return None
        
        logger.info(f"✅ Données d'engagement récupérées: {engagement_data['date']}")
        return score_result
        
    except Exception as e:
        logger.error(f"Erreur récupération données d'engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération données d'engagement: {str(e)}")

@router.get("/dashboard1/public-engagement/trends")
async def get_public_engagement_trends() -> List[Dict[str, Any]]:
    """Récupère les tendances mensuelles d'engagement public"""
    try:
        logger.info("Récupération des tendances d'engagement public")
        
        # Récupérer les tendances mensuelles
        trends = await pe_service.get_monthly_trends()
        
        if not trends:
            logger.warning("Aucune tendance d'engagement trouvée")
            return []
        
        logger.info(f"✅ {len(trends)} tendances d'engagement récupérées")
        return trends
        
    except Exception as e:
        logger.error(f"Erreur récupération tendances d'engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération tendances d'engagement: {str(e)}")

@router.get("/dashboard1/public-engagement/historical")
async def get_public_engagement_historical() -> List[Dict[str, Any]]:
    """Récupère toutes les données historiques d'engagement public"""
    try:
        logger.info("Récupération des données historiques d'engagement public")
        
        # Récupérer toutes les entrées historiques
        entries = await pe_service.get_all_engagement_entries()
        
        if not entries:
            logger.warning("Aucune donnée historique d'engagement trouvée")
            return []
        
        logger.info(f"✅ {len(entries)} entrées historiques d'engagement récupérées")
        return entries
        
    except Exception as e:
        logger.error(f"Erreur récupération données historiques d'engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération données historiques d'engagement: {str(e)}")

@router.get("/dashboard1/public-engagement/health")
async def health_check_public_engagement() -> Dict[str, Any]:
    """Vérifie la santé du service Public Engagement"""
    try:
        logger.info("Vérification de la santé du service Public Engagement")
        
        # Test de santé
        is_healthy = pe_service.health_check()
        
        # Test des données
        engagement_data = await pe_service.get_engagement_data()
        trends = await pe_service.get_monthly_trends()
        
        health_status = {
            "service_healthy": is_healthy,
            "has_engagement_data": engagement_data is not None,
            "has_trends": len(trends) > 0,
            "trends_count": len(trends),
            "latest_date": engagement_data.get('date') if engagement_data else None,
            "latest_score": engagement_data.get('score') if engagement_data else None
        }
        
        logger.info(f"✅ Health check Public Engagement: {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"Erreur health check Public Engagement: {e}")
        return {
            "service_healthy": False,
            "error": str(e)
        }
