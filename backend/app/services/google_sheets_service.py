"""
Service Google Sheets API pour AGRIFRIKA Dashboard
Récupération des données de planning et disponibilité équipe
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
from app.models.dashboard_models import TeamAvailabilityData, WeeklyPlanningData, TeamMember, WeeklyTask, DailySchedule, AvailabilityStatus, Priority

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service pour interagir avec l'API Google Sheets"""
    
    def __init__(self):
        self.service = None
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """Initialise la connexion à l'API Google Sheets"""
        try:
            credentials = Credentials.from_service_account_file(
                settings.sheets_credentials_full_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets API initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets API: {e}")
    
    async def get_team_availability(self) -> Optional[TeamAvailabilityData]:
        """Récupère les données de disponibilité de l'équipe"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Récupération des données du sheet de disponibilité
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.AVAILABILITY_SHEET_ID,
                range=settings.AVAILABILITY_FALLBACK_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if len(values) < 3:  # Header + au moins 1 ligne de données
                logger.warning("Pas assez de données dans le sheet de disponibilité")
                return None
            
            # Parse optimisé des données basé sur la structure réelle
            team_members = []
            status_counts = {"available": 0, "occupied": 0, "unavailable": 0}
            
            # Les vraies données commencent à la ligne 3 (index 2)
            for row_index, row in enumerate(values[2:], start=3):
                if len(row) > 0 and row[0].strip():  # Si le nom existe et n'est pas vide
                    name = row[0].strip()
                    
                    # Analyser tous les statuts de la semaine pour ce membre
                    office_count = 0
                    online_count = 0
                    unavailable_count = 0
                    
                    # Parcourir toutes les colonnes de statut (B à O)
                    for col_index in range(1, min(len(row), 15)):  # Colonnes B(1) à O(14)
                        cell_value = row[col_index].strip().lower() if row[col_index] else ""
                        
                        if "office" in cell_value:
                            office_count += 1
                        elif "online" in cell_value:
                            online_count += 1
                        elif "unavailable" in cell_value:
                            unavailable_count += 1
                    
                    # Déterminer le statut principal basé sur la majorité
                    if office_count >= online_count and office_count >= unavailable_count:
                        status_enum = AvailabilityStatus.OFFICE
                        status_counts["available"] += 1
                    elif online_count >= unavailable_count:
                        status_enum = AvailabilityStatus.ONLINE
                        status_counts["occupied"] += 1
                    else:
                        status_enum = AvailabilityStatus.UNAVAILABLE
                        status_counts["unavailable"] += 1
                    
                    # Calculer le taux de disponibilité pour ce membre
                    total_periods = office_count + online_count + unavailable_count
                    current_task = None
                    if total_periods > 0:
                        available_periods = office_count + online_count
                        availability_rate = (available_periods / total_periods) * 100
                        if availability_rate > 75:
                            current_task = f"Disponible {availability_rate:.0f}% de la semaine"
                        elif availability_rate > 50:
                            current_task = f"Partiellement disponible ({availability_rate:.0f}%)"
                        else:
                            current_task = f"Peu disponible ({availability_rate:.0f}%)"
                    
                    team_members.append(TeamMember(
                        name=name,
                        status=status_enum,
                        current_task=current_task
                    ))
            
            # Calcul du taux de disponibilité
            total_members = len(team_members)
            available_members = status_counts["available"] + status_counts["occupied"]
            availability_rate = (available_members / total_members * 100) if total_members > 0 else 0
            
            return TeamAvailabilityData(
                summary=status_counts,
                team_members=team_members,
                upcoming_changes=[],  # Pourrait être ajouté plus tard
                weekly_availability_rate=round(availability_rate, 1),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération disponibilité équipe: {e}")
            return None
    
    async def get_weekly_planning(self) -> Optional[WeeklyPlanningData]:
        """Récupère les données du planning hebdomadaire"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Récupération des données du sheet de planning
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PLANNING_SHEET_ID,
                range=settings.PLANNING_FALLBACK_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if len(values) < 2:  # Header + au moins 1 ligne
                logger.warning("Pas assez de données dans le sheet de planning")
                return None
            
            # Parse optimisé basé sur la structure réelle observée
            tasks = []
            completed_tasks = 0
            total_tasks = 0
            collaborateurs = set()
            priority_counts = {"haute": 0, "moyenne": 0, "basse": 0}
            status_counts = {"terminé": 0, "en_cours": 0, "a_faire": 0}
            
            # Skip les headers (lignes 1-3) et commencer aux données (ligne 4+)
            for row_index, row in enumerate(values[3:], start=4):
                if len(row) >= 3:  # Au minimum nom, objectif, tâche
                    collaborateur = row[0].strip() if row[0] else ""
                    objectif = row[1].strip() if len(row) > 1 and row[1] else ""
                    tache = row[2].strip() if len(row) > 2 and row[2] else ""
                    priorite = row[3].strip().lower() if len(row) > 3 and row[3] else "moyenne"
                    date_limite = row[4].strip() if len(row) > 4 and row[4] else ""
                    statut = row[5].strip().lower() if len(row) > 5 and row[5] else "à faire"
                    commentaires = row[6].strip() if len(row) > 6 and row[6] else ""
                    
                    # Ne traiter que les lignes avec au moins un collaborateur et une tâche
                    if collaborateur and (tache or objectif):
                        collaborateurs.add(collaborateur)
                        
                        # Normaliser la priorité
                        if "haute" in priorite or "élevé" in priorite or "high" in priorite:
                            priority_enum = Priority.HIGH
                            priority_counts["haute"] += 1
                        elif "basse" in priorite or "faible" in priorite or "low" in priorite:
                            priority_enum = Priority.LOW
                            priority_counts["basse"] += 1
                        else:
                            priority_enum = Priority.MEDIUM
                            priority_counts["moyenne"] += 1
                        
                        # Normaliser le statut
                        if "terminé" in statut or "fini" in statut or "accompli" in statut:
                            completed_tasks += 1
                            status_counts["terminé"] += 1
                        elif "cours" in statut or "progress" in statut:
                            status_counts["en_cours"] += 1
                        else:
                            status_counts["a_faire"] += 1
                        
                        task = WeeklyTask(
                            title=tache or objectif,
                            description=objectif if tache else commentaires,
                            time=date_limite,
                            priority=priority_enum,
                            assigned_to=collaborateur
                        )
                        
                        tasks.append(task)
                        total_tasks += 1
            
            # Organiser les tâches par jour (simulation)
            daily_schedule = {
                "monday": DailySchedule(tasks=tasks[:2] if len(tasks) >= 2 else tasks),
                "tuesday": DailySchedule(tasks=tasks[2:4] if len(tasks) >= 4 else []),
                "wednesday": DailySchedule(tasks=tasks[4:6] if len(tasks) >= 6 else []),
                "thursday": DailySchedule(tasks=[]),
                "friday": DailySchedule(tasks=[]),
                "saturday": DailySchedule(tasks=[]),
                "sunday": DailySchedule(tasks=[])
            }
            
            # Tâches prioritaires (celles avec priorité haute)
            today_priorities = [task for task in tasks if task.priority == Priority.HIGH][:3]
            
            # Obtenir la semaine actuelle
            now = datetime.now()
            week_number = now.isocalendar()[1]
            
            return WeeklyPlanningData(
                week_number=week_number,
                year=now.year,
                week_start=now.strftime("%Y-%m-%d"),
                week_end=(now + timedelta(days=6)).strftime("%Y-%m-%d"),
                daily_schedule=daily_schedule,
                today_priorities=today_priorities,
                weekly_meetings=[],  # Pourrait être ajouté plus tard
                weekly_milestone=None,  # Pourrait être ajouté plus tard
                completion_stats={"completed": completed_tasks, "total": total_tasks},
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération planning hebdomadaire: {e}")
            return None
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Google Sheets"""
        try:
            if not self.service:
                return False
            
            # Test simple de lecture
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PLANNING_SHEET_ID,
                range='A1:B2'
            ).execute()
            
            return 'values' in result
            
        except Exception as e:
            logger.error(f"Google Sheets health check failed: {e}")
            return False