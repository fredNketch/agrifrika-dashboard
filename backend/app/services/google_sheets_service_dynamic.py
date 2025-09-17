"""
Service Google Sheets DYNAMIQUE pour Dashboard 2
Version améliorée qui gère automatiquement les semaines courantes
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
from app.models.dashboard_models import TeamAvailabilityData, WeeklyPlanningData, TeamMember, WeeklyTask, DailySchedule, AvailabilityStatus, Priority

logger = logging.getLogger(__name__)

class DynamicGoogleSheetsService:
    """Service Google Sheets avec gestion dynamique des semaines"""
    
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
            logger.info("✅ Google Sheets API dynamique initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets API: {e}")
    
    def get_current_week_number(self) -> int:
        """Retourne le numéro de semaine courante (ISO)"""
        return datetime.now().isocalendar()[1]
    
    def get_availability_ranges_to_try(self) -> List[str]:
        """Génère la liste des ranges à essayer pour availability"""
        current_week = self.get_current_week_number()
        
        ranges = [
            f"W{current_week}!A3:O20",      # Semaine courante (ex: W34!A3:O20)
            f"W{current_week-1}!A3:O20",    # Semaine précédente (ex: W33!A3:O20)
            f"W{current_week+1}!A3:O20",    # Semaine suivante (préparation)
            "W33!A3:O20",                   # Fallback connu (données de test)
            "Availability!A3:O20",          # Nom générique
            "Team!A3:O20"                   # Autre nom possible
        ]
        
        logger.info(f"📅 Semaine courante: {current_week}, ranges à tester: {ranges[:3]}")
        return ranges
    
    def get_planning_ranges_to_try(self) -> List[str]:
        """Génère la liste des ranges à essayer pour planning"""
        current_week = self.get_current_week_number()
        
        ranges = [
            f"{current_week}!A2:G50",       # Semaine courante (ex: 34!A2:G50)
            f"{current_week-1}!A2:G50",     # Semaine précédente (ex: 33!A2:G50)
            f"{current_week+1}!A2:G50",     # Semaine suivante (préparation)
            "33!A2:G50",                    # Fallback connu (données de test)
            "Planning!A2:G50",              # Nom générique
            "Tasks!A2:G50"                  # Autre nom possible
        ]
        
        logger.info(f"📅 Semaine courante: {current_week}, ranges planning à tester: {ranges[:3]}")
        return ranges
    
    def try_get_sheet_data(self, sheet_id: str, ranges: List[str]) -> Optional[tuple]:
        """Essaie de récupérer les données en testant plusieurs ranges"""
        
        for range_name in ranges:
            try:
                logger.info(f"🔍 Test du range: {range_name}")
                
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                
                # Vérifie si on a des données valides
                if len(values) >= 3:  # Au moins header + 2 lignes de données
                    logger.info(f"✅ Données trouvées dans {range_name}: {len(values)} lignes")
                    return values, range_name
                else:
                    logger.warning(f"⚠️ Range {range_name} trouvé mais peu de données: {len(values)} lignes")
                    
            except Exception as e:
                logger.warning(f"❌ Échec range {range_name}: {e}")
                continue
        
        logger.error("💥 Aucun range fonctionnel trouvé")
        return None, None
    
    async def get_team_availability(self) -> Optional[TeamAvailabilityData]:
        """Récupère les données de disponibilité avec détection dynamique"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Génère les ranges à tester
            ranges_to_try = self.get_availability_ranges_to_try()
            
            # Essaie de récupérer les données
            values, used_range = self.try_get_sheet_data(
                settings.AVAILABILITY_SHEET_ID, 
                ranges_to_try
            )
            
            if not values:
                logger.error("❌ Aucune donnée de disponibilité trouvée")
                return None
            
            logger.info(f"✅ Utilisation du range: {used_range}")
            
            # Parse les données avec la méthode optimisée
            return self.parse_availability_data(values, used_range)
            
        except Exception as e:
            logger.error(f"💥 Erreur récupération disponibilité équipe: {e}")
            return None
    
    async def get_weekly_planning(self) -> Optional[WeeklyPlanningData]:
        """Récupère les données du planning avec détection dynamique"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Génère les ranges à tester
            ranges_to_try = self.get_planning_ranges_to_try()
            
            # Essaie de récupérer les données
            values, used_range = self.try_get_sheet_data(
                settings.PLANNING_SHEET_ID,
                ranges_to_try
            )
            
            if not values:
                logger.error("❌ Aucune donnée de planning trouvée")
                return None
                
            logger.info(f"✅ Utilisation du range planning: {used_range}")
            
            # Parse les données avec la méthode optimisée
            return self.parse_planning_data(values, used_range)
            
        except Exception as e:
            logger.error(f"💥 Erreur récupération planning hebdomadaire: {e}")
            return None
    
    def parse_availability_data(self, values, source_range: str) -> TeamAvailabilityData:
        """Parse optimisé pour les données d'availability"""
        team_members = []
        status_counts = {"available": 0, "occupied": 0, "unavailable": 0}
        
        # Détecte la semaine depuis le range
        week_info = self.extract_week_from_range(source_range)
        
        # Les vraies données commencent à la ligne 3 (index 2)
        for row_index, row in enumerate(values[2:], start=3):
            if len(row) > 0 and row[0].strip():
                name = row[0].strip()
                
                # Analyse tous les statuts de la semaine
                office_count = 0
                online_count = 0
                unavailable_count = 0
                
                # Parcourir toutes les colonnes de statut (B à O)
                for col_index in range(1, min(len(row), 15)):
                    cell_value = row[col_index].strip().lower() if row[col_index] else ""
                    
                    if "office" in cell_value:
                        office_count += 1
                    elif "online" in cell_value:
                        online_count += 1
                    elif "unavailable" in cell_value:
                        unavailable_count += 1
                
                # Détermine le statut principal basé sur la majorité
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
                    current_task = f"Disponible {availability_rate:.0f}% - {week_info}"
                
                team_members.append(TeamMember(
                    name=name,
                    status=status_enum,
                    current_task=current_task
                ))
        
        # Calcul du taux global
        total_members = len(team_members)
        available_members = status_counts["available"] + status_counts["occupied"]
        availability_rate = (available_members / total_members * 100) if total_members > 0 else 0
        
        return TeamAvailabilityData(
            summary=status_counts,
            team_members=team_members,
            upcoming_changes=[],
            weekly_availability_rate=round(availability_rate, 1),
            last_updated=datetime.now()
        )
    
    def parse_planning_data(self, values, source_range: str) -> WeeklyPlanningData:
        """Parse optimisé pour les données de planning"""
        tasks = []
        completed_tasks = 0
        total_tasks = 0
        
        # Détecte la semaine depuis le range
        week_info = self.extract_week_from_range(source_range)
        week_number = self.get_current_week_number()
        
        # Skip les headers (lignes 1-3) et commencer aux données (ligne 4+)
        for row_index, row in enumerate(values[3:], start=4):
            if len(row) >= 3:
                collaborateur = row[0].strip() if row[0] else ""
                objectif = row[1].strip() if len(row) > 1 and row[1] else ""
                tache = row[2].strip() if len(row) > 2 and row[2] else ""
                priorite = row[3].strip().lower() if len(row) > 3 and row[3] else "moyenne"
                date_limite = row[4].strip() if len(row) > 4 and row[4] else ""
                statut = row[5].strip().lower() if len(row) > 5 and row[5] else "à faire"
                
                if collaborateur and (tache or objectif):
                    # Normaliser la priorité
                    if "haute" in priorite or "élevé" in priorite or "high" in priorite:
                        priority_enum = Priority.HIGH
                    elif "basse" in priorite or "faible" in priorite or "low" in priorite:
                        priority_enum = Priority.LOW
                    else:
                        priority_enum = Priority.MEDIUM
                    
                    # Normaliser le statut
                    if "terminé" in statut or "fini" in statut:
                        completed_tasks += 1
                    
                    task = WeeklyTask(
                        title=tache or objectif,
                        description=f"{week_info} - {objectif if tache else ''}",
                        time=date_limite,
                        priority=priority_enum,
                        assigned_to=collaborateur
                    )
                    
                    tasks.append(task)
                    total_tasks += 1
        
        # Organiser les tâches par jour
        daily_schedule = {
            "monday": DailySchedule(tasks=tasks[:2] if len(tasks) >= 2 else tasks),
            "tuesday": DailySchedule(tasks=tasks[2:4] if len(tasks) >= 4 else []),
            "wednesday": DailySchedule(tasks=tasks[4:6] if len(tasks) >= 6 else []),
            "thursday": DailySchedule(tasks=[]),
            "friday": DailySchedule(tasks=[]),
            "saturday": DailySchedule(tasks=[]),
            "sunday": DailySchedule(tasks=[])
        }
        
        # Tâches prioritaires
        today_priorities = [task for task in tasks if task.priority == Priority.HIGH][:3]
        
        now = datetime.now()
        return WeeklyPlanningData(
            week_number=week_number,
            year=now.year,
            week_start=now.strftime("%Y-%m-%d"),
            week_end=(now + timedelta(days=6)).strftime("%Y-%m-%d"),
            daily_schedule=daily_schedule,
            today_priorities=today_priorities,
            weekly_meetings=[],
            weekly_milestone=None,
            completion_stats={"completed": completed_tasks, "total": total_tasks},
            last_updated=datetime.now()
        )
    
    def extract_week_from_range(self, range_name: str) -> str:
        """Extrait l'info de semaine depuis le nom du range"""
        if "W" in range_name:
            # Ex: "W34!A3:O20" -> "Semaine 34"
            week_num = range_name.split("!")[0].replace("W", "")
            return f"Semaine {week_num}"
        elif range_name.split("!")[0].isdigit():
            # Ex: "34!A2:G50" -> "Semaine 34"
            week_num = range_name.split("!")[0]
            return f"Semaine {week_num}"
        else:
            return f"Semaine {self.get_current_week_number()}"
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Google Sheets"""
        try:
            if not self.service:
                return False
            
            # Test simple avec les ranges dynamiques
            ranges = self.get_availability_ranges_to_try()
            values, _ = self.try_get_sheet_data(settings.AVAILABILITY_SHEET_ID, ranges[:1])
            
            return values is not None
            
        except Exception as e:
            logger.error(f"Google Sheets health check failed: {e}")
            return False
    
    def get_status_info(self) -> dict:
        """Retourne des infos sur l'état actuel du service"""
        current_week = self.get_current_week_number()
        return {
            "service_active": self.service is not None,
            "current_week": current_week,
            "availability_ranges": self.get_availability_ranges_to_try()[:3],
            "planning_ranges": self.get_planning_ranges_to_try()[:3],
            "last_check": datetime.now().isoformat()
        }