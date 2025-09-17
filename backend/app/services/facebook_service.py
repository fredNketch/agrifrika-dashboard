"""
Service Facebook Graph API pour AGRIFRIKA Dashboard
Récupération des données d'engagement public et vidéos
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.dashboard_models import PublicEngagementData, FacebookVideoData

logger = logging.getLogger(__name__)

class FacebookService:
    """Service pour interagir avec l'API Facebook Graph"""
   
    def __init__(self):
        self.graph = None
    
    async def get_page_insights(self) -> Optional[PublicEngagementData]:
        """Récupère les insights de la page Facebook - DÉSACTIVÉ"""
        logger.warning("Facebook service désactivé")
        return None
    
    async def get_recent_videos(self, limit: int = 5) -> List[FacebookVideoData]:
        """Récupère les vidéos récentes de la page - DÉSACTIVÉ"""
        return []
    
    async def get_featured_video(self) -> Optional[FacebookVideoData]:
        """Récupère la vidéo la plus performante récente - DÉSACTIVÉ"""
        return None
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Facebook - DÉSACTIVÉ"""
        return False