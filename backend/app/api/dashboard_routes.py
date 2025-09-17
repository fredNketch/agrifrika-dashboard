"""
Routes principales pour les données des dashboards AGRIFRIKA
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List, Dict, Any
from app.models.dashboard_models import (
    APIResponse, Dashboard2Response, TeamAvailabilityData, 
    WeeklyPlanningData, BasecampData, CashFlowData, FacebookVideoData,
    TodosData, TodosByCategory
)
from app.services import FacebookService, BasecampService, CashFlowService
from app.services.google_sheets_service_iso import ISOGoogleSheetsService
from app.services.kpi_calculator import Dashboard1KPIService
from app.services.todos_service import TodosService
from app.services.fundraising_pipeline_service import FundraisingPipelineService
from app.services.public_engagement_service import PublicEngagementService

logger = logging.getLogger(__name__)
router = APIRouter()

# Instances des services
facebook_service = FacebookService()
sheets_service = ISOGoogleSheetsService()
basecamp_service = BasecampService()
cashflow_service = CashFlowService()
kpi_service = Dashboard1KPIService()
todos_service = TodosService()
fundraising_service = FundraisingPipelineService()
engagement_service = PublicEngagementService()

@router.get("/dashboard2/complete", response_model=APIResponse, summary="Dashboard 2 - Données complètes", description="Récupère toutes les données opérationnelles pour le Dashboard 2 en une seule requête optimisée")
async def get_dashboard2_complete():
    """
    Récupère toutes les données pour le Dashboard 2 (Opérationnel)

    Collecte en parallèle toutes les métriques opérationnelles:
    - Disponibilité de l'équipe (Google Sheets)
    - Planning hebdomadaire (Google Sheets)
    - Données Basecamp (tâches et projets)
    - Plan d'action (Google Sheets)
    - Cash flow et métriques financières
    - Données vidéos Facebook

    Returns:
        APIResponse: Toutes les données du dashboard avec métadonnées de performance
    """
    
    try:
        logger.info("[API] Récupération complète Dashboard 2...")
        
        # Récupération RÉELLEMENT en parallèle de toutes les données avec asyncio.gather
        import asyncio
        (
            team_availability,
            weekly_planning,
            basecamp_data,
            action_plan,
            cash_flow,
            facebook_video
        ) = await asyncio.gather(
            sheets_service.get_team_availability(),
            sheets_service.get_weekly_planning(),
            todos_service.get_todos_data(),  # Remplacer Basecamp par Google Sheets todos
            basecamp_service.get_action_plan_items(),
            cashflow_service.get_current_cash_flow(),
            sheets_service.get_featured_video(),
            return_exceptions=True
        )
        
        # Gestion des erreurs pour chaque service
        if isinstance(team_availability, Exception):
            logger.warning(f"Erreur team_availability: {team_availability}")
            team_availability = None
        if isinstance(weekly_planning, Exception):
            logger.warning(f"Erreur weekly_planning: {weekly_planning}")
            weekly_planning = None
        if isinstance(basecamp_data, Exception):
            logger.warning(f"Erreur todos_data: {basecamp_data}")
            todos_data = None
        else:
            # Convertir TodosData en BasecampData compatible
            todos_data = basecamp_data
            all_todos = []
            for category in todos_data.categories:
                all_todos.extend(category.todos)
            
            from app.models.dashboard_models import BasecampData, BasecampTodo
            # Conversion des dates
            def parse_date(date_str):
                if not date_str:
                    return None
                try:
                    from datetime import datetime
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    return None

            basecamp_data = BasecampData(
                todos=[
                    BasecampTodo(
                        id=todo.id,
                        title=todo.title,
                        status=todo.status,
                        assigned_to=todo.assigned_to or "Non assigné",
                        due_date=parse_date(todo.due_date),
                        project=todo.category
                    )
                    for todo in all_todos[:50]  # Limiter pour la performance
                ],
                projects_count=len(todos_data.categories),
                completed_today=todos_data.global_stats.get("completed", 0),
                last_updated=datetime.now()
            )
        if isinstance(action_plan, Exception):
            logger.warning(f"Erreur action_plan: {action_plan}")
            action_plan = []
        if isinstance(cash_flow, Exception):
            logger.warning(f"Erreur cash_flow: {cash_flow}")
            cash_flow = None
        if isinstance(facebook_video, Exception):
            logger.warning(f"Erreur facebook_video: {facebook_video}")
            facebook_video = None
        
        data = Dashboard2Response(
            team_availability=team_availability,
            weekly_planning=weekly_planning,
            basecamp_data=basecamp_data,
            action_plan=action_plan,
            cash_flow=cash_flow,
            facebook_video=facebook_video,
            last_updated=datetime.now()
        )
        
        response = APIResponse(
            success=True,
            data=data.dict(),
            message="Dashboard 2 complet récupéré"
        )
        
        logger.info("[SUCCESS] Dashboard 2 complet récupéré")
        return response
        
    except Exception as e:
        logger.error(f"[ERROR] Erreur récupération Dashboard 2: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération données: {str(e)}")

@router.get("/dashboard2/team-availability", response_model=APIResponse)
async def get_team_availability():
    """Récupère les données de disponibilité de l'équipe"""
    
    try:
        data = await sheets_service.get_team_availability()
        
        if data is None:
            raise HTTPException(status_code=404, detail="Données de disponibilité non trouvées")
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message="Disponibilité équipe récupérée"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération disponibilité équipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/team-availability-detailed", response_model=APIResponse)
async def get_team_availability_detailed():
    """Récupère les données détaillées de disponibilité par jour/période"""
    
    try:
        # Récupérer les données brutes du Google Sheet
        iso_ranges = sheets_service.get_iso_availability_ranges()
        values, used_range = sheets_service.try_get_sheet_data_iso(
            sheets_service.settings.AVAILABILITY_SHEET_ID if hasattr(sheets_service, 'settings') else "1zFGz7zY8XSYB_0P1R3_7HBnhI6-4NHqp3OvAWqaBcd0",
            iso_ranges
        )
        
        if not values:
            raise HTTPException(status_code=404, detail="Données détaillées de disponibilité non trouvées")
        
        # Parser les données détaillées
        detailed_data = []
        day_labels = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        for row in values:
            if len(row) > 0 and row[0].strip():
                name = row[0].strip()
                
                # Structure pour chaque membre avec ses disponibilités par jour/période
                member_data = {
                    "name": name,
                    "availability": {}
                }
                
                # Parser les 14 colonnes (7 jours x 2 périodes)
                for day_idx in range(7):  # 7 jours
                    day_name = day_labels[day_idx]
                    
                    # Colonnes Matin et Soir pour ce jour
                    morning_col = (day_idx * 2) + 1  # B, D, F, H, J, L, N
                    evening_col = (day_idx * 2) + 2  # C, E, G, I, K, M, O
                    
                    morning_status = ""
                    evening_status = ""
                    
                    if morning_col < len(row):
                        morning_status = row[morning_col].strip() if row[morning_col] else ""
                    
                    if evening_col < len(row):
                        evening_status = row[evening_col].strip() if row[evening_col] else ""
                    
                    member_data["availability"][day_name] = {
                        "morning": morning_status,
                        "evening": evening_status
                    }
                
                detailed_data.append(member_data)
        
        return APIResponse(
            success=True,
            data={
                "members": detailed_data,
                "range_used": used_range,
                "total_members": len(detailed_data)
            },
            message="Données détaillées de disponibilité récupérées"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération disponibilité détaillée: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/weekly-planning", response_model=APIResponse)
async def get_weekly_planning():
    """Récupère les données du planning hebdomadaire"""
    
    try:
        data = await sheets_service.get_weekly_planning()
        
        if data is None:
            raise HTTPException(status_code=404, detail="Données de planning non trouvées")
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message="Planning hebdomadaire récupéré"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération planning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/basecamp-todos", response_model=APIResponse)
async def get_basecamp_todos():
    """Récupère les todos Basecamp"""
    
    try:
        data = await basecamp_service.get_all_todos()
        
        if data is None:
            raise HTTPException(status_code=404, detail="Données Basecamp non trouvées")
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message="Todos Basecamp récupérés"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération Basecamp: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/action-plan", response_model=APIResponse)
async def get_action_plan():
    """Récupère le plan d'action"""
    
    try:
        data = await basecamp_service.get_action_plan_items()
        
        return APIResponse(
            success=True,
            data=[item.dict() for item in data],
            message="Plan d'action récupéré"
        )
        
    except Exception as e:
        logger.error(f"Erreur récupération plan d'action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/cash-flow", response_model=APIResponse)
async def get_cash_flow():
    """Récupère les données de cash flow"""
    
    try:
        data = await cashflow_service.get_current_cash_flow()
        
        if data is None:
            raise HTTPException(status_code=404, detail="Données cash flow non trouvées")
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message="Cash flow récupéré"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération cash flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/facebook-video", response_model=APIResponse)
async def get_facebook_video():
    """Récupère la vidéo Facebook featured"""
    
    try:
        data = await sheets_service.get_featured_video()
        
        if data is None:
            # Retourner une vidéo par défaut plutôt qu'une erreur
            return APIResponse(
                success=True,
                data=None,
                message="Aucune vidéo Facebook disponible"
            )
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message="Vidéo Facebook récupérée"
        )
        
    except Exception as e:
        logger.error(f"Erreur récupération vidéo Facebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard1/kpis", response_model=APIResponse)
async def get_dashboard1_kpis():
    """Récupère tous les KPI calculés pour Dashboard 1"""
    
    try:
        logger.info("🔄 Calcul des KPI Dashboard 1...")
        
        # Collecte des données depuis toutes les APIs
        engagement_raw = await facebook_service.get_page_insights()
        financial_raw = await cashflow_service.get_current_cash_flow()
        
        # Construction du dictionnaire de données pour les calculs
        data = {
            "engagement_data": {
                "vues": engagement_raw.impressions if engagement_raw else 0,
                "likes_reactions": engagement_raw.likes if engagement_raw else 0,
                "partages": engagement_raw.shares if engagement_raw else 0,
                "commentaires": engagement_raw.comments if engagement_raw else 0,
                "nouveaux_abonnes": engagement_raw.new_followers if engagement_raw else 0,
                "telechargement_app": 0,  # À connecter avec Google Analytics
                "visites_uniques_site": 0,  # À connecter avec Google Analytics
                "mention_medias": 0,  # À saisir manuellement
                "newsletter": 0,  # À connecter avec service email
                "evenement_50plus_participants": 0,  # À saisir manuellement
                "apparition_recherches": 0,  # À connecter avec Google Search Console
                "impressions_linkedin": 0  # À connecter avec LinkedIn API
            },
            "financial_data": {
                "cash_disponible": financial_raw.current_balance if financial_raw else 0,
                "charges_mensuelles": financial_raw.monthly_burn_rate if (financial_raw and financial_raw.monthly_burn_rate) else 3268,
                "fonds_promis": 0,  # À saisir manuellement via admin panel
                "previous_default_alive": None  # À implémenter avec historique
            },
            "fundraising_data": {
                "concours": {
                    "participation": 0,
                    "participation_plus_100k": 0,
                    "finaliste": 0,
                    "finaliste_plus_100k": 0
                },
                "subventions": {
                    "demande": 0,
                    "demande_plus_100k": 0,
                    "entretien": 0,
                    "acceptation": 0
                },
                "investisseurs": {
                    "contact": 0,
                    "reponse_positive": 0,
                    "meeting": 0,
                    "due_diligence": 0,
                    "engagement_ferme_10k": 0,
                    "chaque_10k_supplementaire": 0
                },
                "objectif_total": 100
            }
        }
        
        # Calcul des KPI avec les vrais algorithmes
        kpis = await kpi_service.calculate_all_kpis(data)
        
        return APIResponse(
            success=True,
            data=kpis,
            message="KPI Dashboard 1 calculés avec succès"
        )
        
    except Exception as e:
        logger.error(f"Erreur calcul KPI Dashboard 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard1/engagement", response_model=APIResponse)
async def get_public_engagement():
    """Récupère les données d'engagement public pour Dashboard 1"""
    
    try:
        # Utiliser le service d'engagement dédié
        score_data = await engagement_service.calculate_engagement_score()
        
        if score_data is None:
            # Fallback vers données mockées
            return APIResponse(
                success=True,
                data={
                    "score": 72,
                    "total_points": 7200,
                    "max_points": 10000,
                    "sources": {
                        "facebook": 2800,
                        "linkedin": 1500,
                        "website": 1200,
                        "newsletter": 900,
                        "events": 700
                    },
                    "top_content": [
                        {"title": "Vues Facebook", "vues": 11795, "platform": "Facebook"},
                        {"title": "Impressions LinkedIn", "vues": 5959, "platform": "LinkedIn"}
                    ],
                    "monthly_trend": [
                        {"month": "Oct", "score": 65},
                        {"month": "Nov", "score": 68},
                        {"month": "Déc", "score": 72}
                    ],
                    "last_updated": datetime.now().isoformat()
                },
                message="Données d'engagement (fallback utilisé)"
            )
        
        return APIResponse(
            success=True,
            data=score_data,
            message="Engagement public récupéré depuis Google Sheets"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération engagement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard1/fundraising", response_model=APIResponse)
async def get_fundraising_pipeline():
    """Récupère les données de fundraising pipeline pour Dashboard 1"""
    
    try:
        # Utiliser le service de fundraising dédié
        score_data = await fundraising_service.calculate_fundraising_score()
        
        if score_data is None:
            # Fallback vers données mockées
            return APIResponse(
                success=True,
                data={
                    "score": 65,
                    "total_points": 65,
                    "max_points": 100,
                    "categories": {
                        "concours": 15,
                        "subventions": 22,
                        "investisseurs": 18,
                        "activités": 10
                    },
                    "upcoming_deadlines": [
                        {"title": "Concours innovation agricole", "date": datetime.now().isoformat(), "type": "concours"},
                        {"title": "Subvention développement rural", "date": datetime.now().isoformat(), "type": "subvention"}
                    ],
                    "progress_chart": [
                        {"month": "Oct", "amount": 15000},
                        {"month": "Nov", "amount": 22000},
                        {"month": "Déc", "amount": 28000}
                    ],
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
        logger.error(f"Erreur récupération fundraising: {e}")
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
        logger.error(f"Erreur récupération tendances fundraising: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-cache")
async def refresh_cache(background_tasks: BackgroundTasks):
    """Force le rafraîchissement du cache des données"""
    
    try:
        # Cette fonction pourrait déclencher un rafraîchissement en arrière-plan
        # Pour l'instant, on retourne simplement un succès
        
        background_tasks.add_task(refresh_all_data)
        
        return APIResponse(
            success=True,
            message="Rafraîchissement du cache lancé en arrière-plan"
        )
        
    except Exception as e:
        logger.error(f"Erreur rafraîchissement cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/iso-status", response_model=APIResponse)
async def get_iso_status():
    """Diagnostic du système ISO - Semaines automatiques"""
    
    try:
        status_info = sheets_service.get_iso_status_info()
        
        return APIResponse(
            success=True,
            data=status_info,
            message="Status ISO récupéré"
        )
        
    except Exception as e:
        logger.error(f"Erreur récupération status ISO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def refresh_all_data():
    """Fonction de rafraîchissement de toutes les données en arrière-plan"""
    logger.info("🔄 Rafraîchissement des données en cours...")
    
    try:
        # Appeler tous les services pour rafraîchir les données
        await sheets_service.get_team_availability()
        await sheets_service.get_weekly_planning()
        await basecamp_service.get_all_todos()
        await cashflow_service.get_current_cash_flow()
        await facebook_service.get_page_insights()
        await todos_service.get_todos_data()
        
        # Recalculer les KPI Dashboard 1
        await kpi_service.calculate_all_kpis({})
        
        logger.info("✅ Rafraîchissement terminé")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du rafraîchissement: {e}")

# === ENDPOINTS TODOS ===

@router.get("/dashboard2/todos", response_model=APIResponse)
async def get_todos():
    """Récupère toutes les données de todos depuis Google Sheets"""
    
    try:
        logger.info("🔄 Récupération des todos depuis Google Sheets...")
        
        data = await todos_service.get_todos_data()
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message=f"Todos récupérés: {data.global_stats['total']} todos dans {len(data.categories)} catégories"
        )
        
    except Exception as e:
        logger.error(f"Erreur récupération todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/todos/category/{category}", response_model=APIResponse)
async def get_todos_by_category(category: str):
    """Récupère les todos d'une catégorie spécifique"""
    
    try:
        logger.info(f"🔄 Récupération des todos pour la catégorie: {category}")
        
        data = await todos_service.get_todos_by_category(category)
        
        if data is None:
            raise HTTPException(status_code=404, detail=f"Catégorie '{category}' non trouvée")
        
        return APIResponse(
            success=True,
            data=data.dict(),
            message=f"Todos de la catégorie '{category}' récupérés: {data.total_count} todos"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération todos catégorie {category}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/todos/urgent", response_model=APIResponse)
async def get_urgent_todos():
    """Récupère uniquement les todos urgents (échéance dans les 7 prochains jours)"""
    
    try:
        logger.info("🔄 Récupération des todos urgents...")
        
        data = await todos_service.get_urgent_todos()
        
        return APIResponse(
            success=True,
            data=data,
            message=f"Todos urgents récupérés: {len(data)} todos"
        )
        
    except Exception as e:
        logger.error(f"Erreur récupération todos urgents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard2/todos/stats", response_model=APIResponse)
async def get_todos_stats():
    """Récupère uniquement les statistiques globales des todos"""
    
    try:
        logger.info("🔄 Calcul des statistiques des todos...")
        
        todos_data = await todos_service.get_todos_data()
        
        stats = {
            "global_stats": todos_data.global_stats,
            "categories_count": len(todos_data.categories),
            "urgent_count": len(todos_data.urgent_todos),
            "categories_breakdown": [
                {
                    "category": cat.category,
                    "total": cat.total_count,
                    "pending": cat.pending_count,
                    "completed": cat.completed_count
                }
                for cat in todos_data.categories
            ],
            "last_updated": todos_data.last_updated
        }
        
        return APIResponse(
            success=True,
            data=stats,
            message="Statistiques des todos calculées"
        )
        
    except Exception as e:
        logger.error(f"Erreur calcul statistiques todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Nouvelles routes Public Engagement avec tendances mensuelles indépendantes
@router.get("/dashboard1/public-engagement/trends")
async def get_public_engagement_trends() -> List[Dict[str, Any]]:
    """Récupère les tendances mensuelles d'engagement public"""
    try:
        logger.info("Récupération des tendances d'engagement public")
        
        # Récupérer les tendances mensuelles
        trends = await engagement_service.get_monthly_trends()
        
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
        entries = await engagement_service.get_all_engagement_entries()
        
        if not entries:
            logger.warning("Aucune donnée historique d'engagement trouvée")
            return []
        
        logger.info(f"✅ {len(entries)} entrées historiques d'engagement récupérées")
        return entries
        
    except Exception as e:
        logger.error(f"Erreur récupération données historiques d'engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération données historiques d'engagement: {str(e)}")
