"""
Modèles Pydantic pour les données des dashboards AGRIFRIKA
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums pour les statuts
class TaskStatus(str, Enum):
    EN_COURS = "en_cours"
    A_FAIRE = "a_faire"
    TERMINE = "termine"
    EN_ATTENTE = "en_attente"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AvailabilityStatus(str, Enum):
    OFFICE = "office"
    ONLINE = "online"
    UNAVAILABLE = "unavailable"

# === DASHBOARD 1 MODELS ===

class DefaultAliveData(BaseModel):
    """Modèle pour les données Default Alive (Dashboard 1)"""
    current_runway_months: float
    burn_rate_monthly: float
    cash_position: float
    growth_rate_monthly: float
    last_updated: datetime

class PublicEngagementData(BaseModel):
    """Modèle pour l'engagement public (Dashboard 1)"""
    total_followers: int
    engagement_rate: float
    recent_posts_performance: List[Dict[str, Any]]
    platform_breakdown: Dict[str, int]
    last_updated: datetime

class FundraisingData(BaseModel):
    """Modèle pour le fundraising (Dashboard 1)"""
    target_amount: float
    current_raised: float
    investors_count: int
    pipeline_deals: List[Dict[str, Any]]
    last_updated: datetime

# === DASHBOARD 2 MODELS ===

class TeamMember(BaseModel):
    """Modèle pour un membre de l'équipe"""
    name: str
    role: Optional[str] = None
    status: AvailabilityStatus
    current_task: Optional[str] = None

class DayPeriod(BaseModel):
    """Modèle pour une période d'une journée (matin/soir)"""
    period: str  # "morning" ou "evening"
    status: Optional[AvailabilityStatus] = None

class DayAvailability(BaseModel):
    """Modèle pour la disponibilité d'une journée"""
    day: str  # "lundi", "mardi", etc.
    morning: Optional[AvailabilityStatus] = None
    evening: Optional[AvailabilityStatus] = None

class DetailedTeamMember(BaseModel):
    """Modèle détaillé pour un membre de l'équipe avec statuts individuels"""
    name: str
    role: Optional[str] = None
    weekly_schedule: List[DayAvailability] = []  # 7 jours avec matin/soir
    overall_status: AvailabilityStatus = AvailabilityStatus.OFFICE  # Status principal
    current_task: Optional[str] = None

class TeamAvailabilityData(BaseModel):
    """Modèle pour la disponibilité de l'équipe"""
    summary: Dict[str, int] = Field(description="Résumé des statuts (available, occupied, unavailable)")
    team_members: List[TeamMember]
    detailed_members: List[DetailedTeamMember] = []  # Membres avec détails par période
    upcoming_changes: List[Dict[str, Any]] = []
    weekly_availability_rate: float
    last_updated: datetime

class WeeklyTask(BaseModel):
    """Modèle pour une tâche hebdomadaire"""
    title: str
    description: Optional[str] = None
    time: str
    priority: Priority
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    objectives: Optional[str] = None  # Objectifs de la semaine
    comments: Optional[str] = None    # Commentaires/Notes
    priority_display: Optional[str] = None  # Priorité textuelle (Haute, Moyenne, Basse)

class DailySchedule(BaseModel):
    """Modèle pour le planning d'une journée"""
    tasks: List[WeeklyTask]

class WeeklyPlanningData(BaseModel):
    """Modèle pour le planning hebdomadaire"""
    week_number: int
    year: int
    week_start: str
    week_end: str
    daily_schedule: Dict[str, DailySchedule]
    today_priorities: List[WeeklyTask]
    weekly_meetings: List[Dict[str, Any]] = []
    weekly_milestone: Optional[Dict[str, Any]] = None
    completion_stats: Dict[str, int] = Field(description="completed/total")
    last_updated: datetime

class BasecampTodo(BaseModel):
    """Modèle pour un todo Basecamp"""
    id: str
    title: str
    status: TaskStatus
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    project: Optional[str] = None

class BasecampData(BaseModel):
    """Modèle pour les données Basecamp"""
    todos: List[BasecampTodo]
    projects_count: int
    completed_today: int
    last_updated: datetime

class ActionPlanItem(BaseModel):
    """Modèle pour un élément du plan d'action"""
    id: str
    title: str
    assigned_to: str
    due_date: Optional[datetime] = None
    priority: str
    status: str
    category: str = Field(description="today, this_week, etc.")

class CashFlowTransaction(BaseModel):
    """Modèle pour une transaction cash flow"""
    type: str = Field(description="income, expense, transfer")
    description: str
    amount: float
    date: datetime
    category: Optional[str] = None

class CashFlowData(BaseModel):
    """Modèle pour les données de cash flow"""
    current_balance: float
    balance_date: datetime
    weekly_summary: Dict[str, float] = Field(description="total_income, total_expenses, net_change")
    daily_evolution: List[Dict[str, Any]]
    recent_transactions: List[CashFlowTransaction]
    upcoming_payments: List[Dict[str, Any]] = []
    thirty_day_projection: float
    last_updated: datetime
    
    # Champs additionnels de l'API Agrifrika
    monthly_burn_rate: Optional[float] = None
    runway_days: Optional[str] = None
    runway_months: Optional[str] = None
    runway_end_date: Optional[str] = None
    historical_income: Optional[float] = None
    total_spent: Optional[float] = None

class FacebookVideoData(BaseModel):
    """Modèle pour les données vidéo Facebook"""
    id: str
    title: str
    thumbnail_url: Optional[str] = None
    video_url: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    published_date: datetime
    duration: Optional[int] = None  # en secondes

class TodoItem(BaseModel):
    """Modèle pour un élément todo"""
    id: str
    title: str
    status: str  # "pending", "completed", "in_progress"
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None  # Date au format string comme dans le Google Sheet
    category: str = Field(description="Catégorie/Feuille du todo")
    
class TodosByCategory(BaseModel):
    """Modèle pour les todos regroupés par catégorie"""
    category: str
    todos: List[TodoItem]
    total_count: int
    pending_count: int 
    completed_count: int

class TodosData(BaseModel):
    """Modèle pour l'ensemble des données todos"""
    categories: List[TodosByCategory]
    global_stats: Dict[str, int] = Field(description="total, pending, completed, in_progress")
    urgent_todos: List[TodoItem] = Field(description="Todos urgents (échéance proche)")
    last_updated: datetime

# === RESPONSES MODELS ===

class APIResponse(BaseModel):
    """Modèle de réponse standard de l'API"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    """Modèle pour la réponse de santé de l'API"""
    status: str
    version: str
    uptime: float
    apis_status: Dict[str, bool]
    timestamp: datetime

class Dashboard1Response(BaseModel):
    """Modèle pour la réponse complète du Dashboard 1"""
    default_alive: Optional[DefaultAliveData] = None
    public_engagement: Optional[PublicEngagementData] = None
    fundraising: Optional[FundraisingData] = None
    last_updated: datetime

class Dashboard2Response(BaseModel):
    """Modèle pour la réponse complète du Dashboard 2"""
    team_availability: Optional[TeamAvailabilityData] = None
    weekly_planning: Optional[WeeklyPlanningData] = None
    basecamp_data: Optional[BasecampData] = None
    action_plan: Optional[List[ActionPlanItem]] = None
    cash_flow: Optional[CashFlowData] = None
    facebook_video: Optional[FacebookVideoData] = None
    last_updated: datetime