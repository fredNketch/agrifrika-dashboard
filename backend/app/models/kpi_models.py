"""
Modèles Pydantic pour les KPI Dashboard 1 - AGRIFRIKA
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class EngagementStatusModel(BaseModel):
    """Modèle pour le statut d'engagement"""
    level: str
    color: str
    message: str

class EngagementDetailModel(BaseModel):
    """Modèle pour les détails d'une source d'engagement"""
    valeur_obtenue: int
    points_obtenus: int
    objectif: int
    progression_objectif: float

class PublicEngagementKPI(BaseModel):
    """Modèle pour le KPI Public Engagement"""
    score: float
    total_points_obtenus: int
    total_objectif: int
    details_par_source: Dict[str, EngagementDetailModel]
    status: EngagementStatusModel
    timestamp: str

class DefaultAliveStatusModel(BaseModel):
    """Modèle pour le statut Default Alive"""
    status: str
    color: str
    message: str

class DefaultAlivePratiqueModel(BaseModel):
    """Modèle pour Default Alive Pratique"""
    mois_restants: float
    status: DefaultAliveStatusModel
    trend_percentage: float

class DefaultAliveTheoriqueModel(BaseModel):
    """Modèle pour Default Alive Théorique"""
    mois_restants: float
    status: DefaultAliveStatusModel

class DefaultAliveBaseDataModel(BaseModel):
    """Modèle pour les données de base Default Alive"""
    cash_disponible: float
    charges_mensuelles: float
    fonds_promis: float

class DefaultAliveKPI(BaseModel):
    """Modèle pour le KPI Default Alive"""
    default_alive_pratique: DefaultAlivePratiqueModel
    default_alive_theorique: DefaultAliveTheoriqueModel
    donnees_base: DefaultAliveBaseDataModel
    timestamp: str

class FundraisingCategoryModel(BaseModel):
    """Modèle pour une catégorie de fundraising"""
    points_obtenus: int
    activites: Dict[str, int]

class FundraisingStatusModel(BaseModel):
    """Modèle pour le statut de fundraising"""
    level: str
    color: str
    message: str

class FundraisingKPI(BaseModel):
    """Modèle pour le KPI Fundraising Pipeline"""
    score: float
    total_points_obtenus: int
    objectif_total: int
    details_par_categorie: Dict[str, FundraisingCategoryModel]
    prochaines_echeances: List[Dict[str, Any]]
    status: FundraisingStatusModel
    timestamp: str

class Dashboard1KPIResponse(BaseModel):
    """Modèle de réponse pour tous les KPI Dashboard 1"""
    public_engagement: PublicEngagementKPI
    default_alive: DefaultAliveKPI
    fundraising_pipeline: FundraisingKPI
    calculation_timestamp: str
    success: bool
    error: Optional[str] = None

class KPICalculationRequest(BaseModel):
    """Modèle de requête pour le calcul des KPI"""
    engagement_data: Dict[str, int]
    financial_data: Dict[str, float]
    fundraising_data: Dict[str, Dict[str, int]]
    force_refresh: Optional[bool] = False

class KPIHistoryEntry(BaseModel):
    """Modèle pour une entrée d'historique KPI"""
    timestamp: datetime
    public_engagement_score: float
    default_alive_months: float
    fundraising_score: float
    
class KPITrendData(BaseModel):
    """Modèle pour les données de tendance KPI"""
    current_value: float
    previous_value: Optional[float]
    trend_percentage: float
    trend_direction: str  # "up", "down", "stable"