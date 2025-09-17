"""
Schémas OpenAPI pour la documentation Swagger
Définit les modèles de données pour l'API AGRIFRIKA Dashboard
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# === ENUMS POUR LES SCHEMAS ===

class HealthStatus(str, Enum):
    """Statut de santé des services"""
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"

class SyncStatus(str, Enum):
    """Statut de synchronisation"""
    active = "active"
    inactive = "inactive"
    running = "running"
    error = "error"

class TaskPriority(str, Enum):
    """Priorité des tâches"""
    high = "high"
    medium = "medium"
    low = "low"

class TaskStatus(str, Enum):
    """Statut des tâches"""
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    blocked = "blocked"

# === SCHEMAS DE REPONSE ===

class APIResponseBase(BaseModel):
    """Schéma de base pour toutes les réponses API"""
    success: bool = Field(..., description="Indique si la requête a réussi")
    message: str = Field(..., description="Message descriptif de la réponse")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la réponse")

class APIResponse(APIResponseBase):
    """Réponse API standard avec données"""
    data: Optional[Dict[str, Any]] = Field(None, description="Données de la réponse")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Métadonnées additionnelles")

class HealthResponse(APIResponseBase):
    """Réponse pour les endpoints de santé"""
    status: HealthStatus = Field(..., description="Statut global de santé")
    version: str = Field(..., description="Version de l'API")
    uptime: float = Field(..., description="Temps de fonctionnement en secondes")
    apis_status: Dict[str, bool] = Field(..., description="Statut de chaque service externe")

# === SCHEMAS POUR LES DONNEES DASHBOARD ===

class TeamMemberAvailability(BaseModel):
    """Disponibilité d'un membre d'équipe"""
    name: str = Field(..., description="Nom du membre d'équipe")
    status: str = Field(..., description="Statut de disponibilité (office/online/unavailable)")
    location: Optional[str] = Field(None, description="Localisation du membre")
    hours: Optional[str] = Field(None, description="Heures de travail")

class WeeklyPlanningItem(BaseModel):
    """Élément du planning hebdomadaire"""
    task: str = Field(..., description="Description de la tâche")
    assignee: str = Field(..., description="Personne assignée")
    deadline: Optional[datetime] = Field(None, description="Date limite")
    priority: TaskPriority = Field(..., description="Priorité de la tâche")
    status: TaskStatus = Field(..., description="Statut actuel")

class BasecampTask(BaseModel):
    """Tâche Basecamp"""
    id: int = Field(..., description="ID unique de la tâche")
    title: str = Field(..., description="Titre de la tâche")
    assignee: Optional[str] = Field(None, description="Personne assignée")
    due_date: Optional[datetime] = Field(None, description="Date d'échéance")
    completed: bool = Field(..., description="Tâche terminée")
    project_name: str = Field(..., description="Nom du projet parent")

class CashFlowData(BaseModel):
    """Données de cash flow"""
    current_balance: float = Field(..., description="Solde actuel")
    monthly_income: float = Field(..., description="Revenus mensuels")
    monthly_expenses: float = Field(..., description="Dépenses mensuelles")
    runway_months: Optional[float] = Field(None, description="Piste en mois")
    last_updated: datetime = Field(..., description="Dernière mise à jour")

class FacebookVideoMetrics(BaseModel):
    """Métriques vidéo Facebook"""
    video_id: str = Field(..., description="ID de la vidéo")
    title: str = Field(..., description="Titre de la vidéo")
    views: int = Field(..., description="Nombre de vues")
    likes: int = Field(..., description="Nombre de likes")
    shares: int = Field(..., description="Nombre de partages")
    comments: int = Field(..., description="Nombre de commentaires")
    duration: Optional[int] = Field(None, description="Durée en secondes")
    engagement_rate: Optional[float] = Field(None, description="Taux d'engagement")

# === SCHEMAS POUR LA SYNCHRONISATION ===

class SyncStatistics(BaseModel):
    """Statistiques de synchronisation"""
    total_syncs: int = Field(..., description="Nombre total de synchronisations")
    successful_syncs: int = Field(..., description="Synchronisations réussies")
    failed_syncs: int = Field(..., description="Synchronisations échouées")
    last_sync_duration: Optional[float] = Field(None, description="Durée de la dernière sync en secondes")
    average_duration: Optional[float] = Field(None, description="Durée moyenne en secondes")

class SyncStatusResponse(BaseModel):
    """Réponse pour le statut de synchronisation"""
    status: SyncStatus = Field(..., description="Statut actuel du service")
    is_running: bool = Field(..., description="Synchronisation en cours")
    last_sync: Optional[datetime] = Field(None, description="Dernière synchronisation")
    next_sync: Optional[datetime] = Field(None, description="Prochaine synchronisation")
    statistics: SyncStatistics = Field(..., description="Statistiques de synchronisation")

class SyncExecutionResult(BaseModel):
    """Résultat d'exécution de synchronisation"""
    started_at: datetime = Field(..., description="Début de la synchronisation")
    completed_at: Optional[datetime] = Field(None, description="Fin de la synchronisation")
    duration: Optional[float] = Field(None, description="Durée en secondes")
    tasks_processed: int = Field(..., description="Nombre de tâches traitées")
    tasks_updated: int = Field(..., description="Nombre de tâches mises à jour")
    errors: List[str] = Field(default_factory=list, description="Liste des erreurs rencontrées")

# === SCHEMAS POUR LES DASHBOARDS ===

class Dashboard2Data(BaseModel):
    """Données complètes du Dashboard 2"""
    team_availability: List[TeamMemberAvailability] = Field(..., description="Disponibilité de l'équipe")
    weekly_planning: List[WeeklyPlanningItem] = Field(..., description="Planning hebdomadaire")
    basecamp_tasks: List[BasecampTask] = Field(..., description="Tâches Basecamp")
    cash_flow: CashFlowData = Field(..., description="Données financières")
    facebook_videos: List[FacebookVideoMetrics] = Field(..., description="Métriques vidéos Facebook")

class KPIMetrics(BaseModel):
    """Métriques KPI générales"""
    revenue_growth: Optional[float] = Field(None, description="Croissance du chiffre d'affaires (%)")
    team_productivity: Optional[float] = Field(None, description="Productivité de l'équipe (%)")
    customer_satisfaction: Optional[float] = Field(None, description="Satisfaction client (%)")
    engagement_rate: Optional[float] = Field(None, description="Taux d'engagement (%)")

# === SCHEMAS D'ERREUR ===

class ErrorDetail(BaseModel):
    """Détail d'une erreur"""
    code: str = Field(..., description="Code d'erreur")
    message: str = Field(..., description="Message d'erreur")
    field: Optional[str] = Field(None, description="Champ concerné")

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error: str = Field(..., description="Message d'erreur principal")
    status_code: int = Field(..., description="Code de statut HTTP")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de l'erreur")
    details: Optional[List[ErrorDetail]] = Field(None, description="Détails supplémentaires")

# === SCHEMAS DE VALIDATION ===

class CredentialValidation(BaseModel):
    """Validation des credentials"""
    service_name: str = Field(..., description="Nom du service")
    is_configured: bool = Field(..., description="Service configuré")
    is_valid: bool = Field(..., description="Credentials valides")
    last_checked: datetime = Field(..., description="Dernière vérification")
    error_message: Optional[str] = Field(None, description="Message d'erreur si invalid")

class SystemInfo(BaseModel):
    """Informations système"""
    debug_mode: bool = Field(..., description="Mode debug activé")
    cors_origins: List[str] = Field(..., description="Origins CORS autorisées")
    cache_ttl: int = Field(..., description="TTL du cache en secondes")
    version: str = Field(..., description="Version de l'API")
    environment: str = Field(..., description="Environnement (dev/prod/staging)")