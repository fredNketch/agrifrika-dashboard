"""
Service Google Sheets BASÉ SUR ISO 8601
Utilise le système de semaines ISO standard pour la gestion dynamique
"""

import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
from app.models.dashboard_models import TeamAvailabilityData, WeeklyPlanningData, TeamMember, WeeklyTask, DailySchedule, AvailabilityStatus, Priority, FacebookVideoData, DayAvailability, DetailedTeamMember

logger = logging.getLogger(__name__)

class ISOGoogleSheetsService:
    """Service Google Sheets avec référence ISO 8601 pour les semaines"""
    
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
            logger.info("✅ Google Sheets API ISO initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets API: {e}")
    
    def get_iso_week_info(self, date: datetime = None) -> Tuple[int, int, int]:
        """
        Retourne les infos ISO de la semaine pour une date donnée
        Returns: (année_iso, semaine_iso, jour_semaine)
        """
        if date is None:
            date = datetime.now()
        
        year, week, weekday = date.isocalendar()
        return year, week, weekday
    
    def get_current_iso_week(self) -> int:
        """Retourne le numéro de semaine ISO courante"""
        _, week, _ = self.get_iso_week_info()
        return week
    
    def get_iso_week_boundaries(self, date: datetime = None) -> Tuple[datetime, datetime]:
        """
        Retourne le lundi et dimanche de la semaine ISO pour une date donnée
        """
        if date is None:
            date = datetime.now()
        
        year, week, weekday = date.isocalendar()
        
        # Trouver le lundi de cette semaine ISO
        monday = date - timedelta(days=weekday - 1)
        sunday = monday + timedelta(days=6)
        
        return monday, sunday
    
    def format_iso_week_label(self, date: datetime = None) -> str:
        """
        Génère un label lisible pour la semaine ISO
        Ex: "S34 2025 (19-25 Août)"
        """
        if date is None:
            date = datetime.now()
        
        year, week, _ = date.isocalendar()
        monday, sunday = self.get_iso_week_boundaries(date)
        
        # Formatage français des mois
        months_fr = [
            '', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
            'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'
        ]
        
        monday_str = f"{monday.day} {months_fr[monday.month]}"
        sunday_str = f"{sunday.day} {months_fr[sunday.month]}"
        
        return f"S{week} {year} ({monday_str}-{sunday_str})"
    
    def get_iso_availability_ranges(self, weeks_back: int = 2, weeks_forward: int = 1) -> List[str]:
        """
        Génère les ranges de disponibilité basés sur les semaines ISO
        
        Args:
            weeks_back: Nombre de semaines précédentes à inclure
            weeks_forward: Nombre de semaines futures à inclure
        """
        ranges = []
        current_date = datetime.now()
        
        # Obtenir la semaine ISO courante (logique identique au planning)
        _, current_week, _ = current_date.isocalendar()
        
        # PRIORITÉ 1: Semaine courante avec calcul dynamique
        ranges.append(f"W{current_week}!A1:O20")  # Range complet avec headers
        ranges.append(f"W{current_week}!A3:O20")  # Range données seulement
        
        # Génère les ranges pour plusieurs semaines
        for week_offset in range(-weeks_back, weeks_forward + 1):
            target_date = current_date + timedelta(weeks=week_offset)
            _, week_number, _ = target_date.isocalendar()
            
            # Format standard: W{semaine}!A1:O20 (pour avoir headers)
            range_name = f"W{week_number}!A1:O20"
            ranges.append(range_name)
            
            # Format alternatif sans headers
            range_name_alt = f"W{week_number}!A3:O20"
            ranges.append(range_name_alt)
        
        # Ajout des fallbacks génériques
        ranges.extend([
            "W33!A1:O20",
            "W33!A3:O20",
            "Availability!A3:O20",
            "Team!A3:O20",
            "Current!A3:O20"
        ])
        
        # Supprime les doublons en gardant l'ordre
        unique_ranges = []
        seen = set()
        for range_name in ranges:
            if range_name not in seen:
                unique_ranges.append(range_name)
                seen.add(range_name)
        
        logger.info(f"📅 Ranges ISO availability générés: {unique_ranges[:5]}")
        return unique_ranges
    
    def get_iso_planning_ranges(self, weeks_back: int = 2, weeks_forward: int = 1) -> List[str]:
        """
        Génère les ranges de planning basés sur les semaines ISO courantes
        """
        ranges = []
        current_date = datetime.now()
        
        # Obtenir la semaine ISO courante
        _, current_week, _ = current_date.isocalendar()
        
        # PRIORITÉ 1: Semaine courante (34 pour août 2024)
        ranges.append(f"{current_week}!A2:G50")
        ranges.append(f"S{current_week}!A2:G50")  # Format alternatif avec S
        
        # PRIORITÉ 2: Semaines adjacentes (au cas où)
        for offset in [-1, 1, -2, 2]:  # Semaines voisines
            week_num = current_week + offset
            if week_num > 0 and week_num <= 52:  # Validation des semaines valides
                ranges.append(f"{week_num}!A2:G50")
                ranges.append(f"S{week_num}!A2:G50")
        
        # Génère les ranges pour plusieurs semaines
        for week_offset in range(-weeks_back, weeks_forward + 1):
            target_date = current_date + timedelta(weeks=week_offset)
            _, week_number, _ = target_date.isocalendar()
            
            # Format standard: {semaine}!A2:G50
            range_name = f"{week_number}!A2:G50"
            ranges.append(range_name)
            
            # Format alternatif: S{semaine}!A2:G50
            alt_range = f"S{week_number}!A2:G50"
            ranges.append(alt_range)
        
        # Ajout des fallbacks génériques
        ranges.extend([
            "Planning!A2:G50",
            "Tasks!A2:G50",
            "Current!A2:G50",
            "33!A2:G50"  # Fallback historique
        ])
        
        # Supprime les doublons
        unique_ranges = []
        seen = set()
        for range_name in ranges:
            if range_name not in seen:
                unique_ranges.append(range_name)
                seen.add(range_name)
        
        logger.info(f"📅 Ranges ISO planning générés: {unique_ranges[:5]}")
        return unique_ranges
    
    def try_get_sheet_data_iso(self, sheet_id: str, ranges: List[str]) -> Optional[Tuple]:
        """
        Essaie de récupérer les données en testant plusieurs ranges ISO
        Retourne les données ET le range utilisé
        """
        for range_name in ranges:
            try:
                logger.info(f"🔍 Test ISO range: {range_name}")
                
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=sheet_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                
                # Validation des données
                if len(values) >= 3:  # Header + données minimum
                    # Vérification que ce n'est pas que des headers vides
                    data_rows = [row for row in values[2:] if len(row) > 0 and any(cell.strip() for cell in row if cell)]
                    
                    if len(data_rows) >= 1:
                        logger.info(f"✅ Données ISO trouvées dans {range_name}: {len(values)} lignes, {len(data_rows)} avec données")
                        return values, range_name
                    else:
                        logger.warning(f"⚠️ Range {range_name} trouvé mais sans données valides")
                else:
                    logger.warning(f"⚠️ Range {range_name} insuffisant: {len(values)} lignes")
                    
            except Exception as e:
                logger.warning(f"❌ Échec ISO range {range_name}: {e}")
                continue
        
        logger.error("💥 Aucun range ISO fonctionnel trouvé")
        return None, None
    
    async def get_team_availability(self) -> Optional[TeamAvailabilityData]:
        """Récupère les données de disponibilité avec référence ISO"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Génère les ranges basés sur ISO
            iso_ranges = self.get_iso_availability_ranges()
            
            # Récupère les données
            values, used_range = self.try_get_sheet_data_iso(
                settings.AVAILABILITY_SHEET_ID,
                iso_ranges
            )
            
            if not values:
                logger.error("❌ Aucune donnée de disponibilité ISO trouvée")
                return None
            
            logger.info(f"✅ Utilisation du range ISO: {used_range}")
            
            # Parse avec informations ISO
            return self.parse_availability_data_iso(values, used_range)
            
        except Exception as e:
            logger.error(f"💥 Erreur récupération disponibilité ISO: {e}")
            return None
    
    async def get_weekly_planning(self) -> Optional[WeeklyPlanningData]:
        """Récupère les données du planning avec référence ISO"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Génère les ranges basés sur ISO
            iso_ranges = self.get_iso_planning_ranges()
            
            # Récupère les données
            values, used_range = self.try_get_sheet_data_iso(
                settings.PLANNING_SHEET_ID,
                iso_ranges
            )
            
            if not values:
                logger.error("❌ Aucune donnée de planning ISO trouvée")
                return None
                
            logger.info(f"✅ Utilisation du range planning ISO: {used_range}")
            
            # Parse avec informations ISO
            return self.parse_planning_data_iso(values, used_range)
            
        except Exception as e:
            logger.error(f"💥 Erreur récupération planning ISO: {e}")
            return None
    
    def parse_availability_data_iso(self, values, source_range: str) -> TeamAvailabilityData:
        """Parse optimisé avec informations ISO et données détaillées par période"""
        team_members = []
        detailed_members = []
        status_counts = {"available": 0, "occupied": 0, "unavailable": 0}
        
        # Mappings pour les statuts
        status_mappings = {
            'office': AvailabilityStatus.OFFICE,
            'online': AvailabilityStatus.ONLINE,
            'unavailable': AvailabilityStatus.UNAVAILABLE,
        }

        # Structure des périodes (colonnes B-O correspondent aux jours/périodes)
        periods_mapping = [
            ("lundi", "morning"),    # Col B (index 1)
            ("lundi", "evening"),    # Col C (index 2)
            ("mardi", "morning"),    # Col D (index 3)
            ("mardi", "evening"),    # Col E (index 4)
            ("mercredi", "morning"), # Col F (index 5)
            ("mercredi", "evening"), # Col G (index 6)
            ("jeudi", "morning"),    # Col H (index 7)
            ("jeudi", "evening"),    # Col I (index 8)
            ("vendredi", "morning"), # Col J (index 9)
            ("vendredi", "evening"), # Col K (index 10)
            ("samedi", "morning"),   # Col L (index 11)
            ("samedi", "evening"),   # Col M (index 12)
            ("dimanche", "morning"), # Col N (index 13)
            ("dimanche", "evening")  # Col O (index 14)
        ]
        
        # Extraction des infos ISO depuis le range
        iso_info = self.extract_iso_info_from_range(source_range)
        current_week_label = self.format_iso_week_label()
        
        # CORRECTION: Détecter automatiquement où commencent les données
        data_start_index = 2  # Par défaut ligne 3 (index 2)
        
        # Si on a un range A1:O20, chercher la première ligne avec des noms
        if "A1:" in source_range:
            for i, row in enumerate(values):
                if (len(row) > 0 and row[0] and row[0].strip() 
                    and not row[0].strip().lower().startswith('staff') 
                    and not row[0].strip().lower().startswith('team')):
                    # Vérifier que c'est bien une ligne de données (pas header)
                    if i > 0 and len(row) > 1:  # Au moins 2 colonnes et pas première ligne
                        data_start_index = i
                        break
        
        logger.info(f"🔍 Données commencent à l'index {data_start_index} (ligne {data_start_index + 1})")
        
        for row_index, row in enumerate(values[data_start_index:], start=data_start_index + 1):
            if len(row) > 0 and row[0] and row[0].strip():
                name = row[0].strip()
                logger.info(f"👤 Processing member {len(team_members) + 1}: {name}")
                
                # Analyser les statuts par période
                weekly_schedule = []
                office_count = online_count = unavailable_count = 0
                current_task = None
                
                # Organiser les statuts par jour
                days_data = {}
                
                for col_index in range(1, min(len(row), 15)):  # Colonnes B à O
                    if col_index - 1 < len(periods_mapping):
                        day, period = periods_mapping[col_index - 1]
                        
                        # Récupérer la valeur de la cellule
                        cell_value = row[col_index].strip().lower() if col_index < len(row) and row[col_index] else ""
                        mapped_status = None
                        
                        if cell_value:
                            # Mapping du statut
                            for keyword, status in status_mappings.items():
                                if keyword in cell_value:
                                    mapped_status = status
                                    break
                            
                            # Comptage pour le statut global
                            if mapped_status == AvailabilityStatus.OFFICE:
                                office_count += 1
                            elif mapped_status == AvailabilityStatus.ONLINE:
                                online_count += 1
                            elif mapped_status == AvailabilityStatus.UNAVAILABLE:
                                unavailable_count += 1
                        
                        # Organiser par jour
                        if day not in days_data:
                            days_data[day] = {}
                        days_data[day][period] = mapped_status

                # Construire le planning hebdomadaire détaillé
                for day in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]:
                    day_availability = DayAvailability(
                        day=day,
                        morning=days_data.get(day, {}).get("morning"),
                        evening=days_data.get(day, {}).get("evening")
                    )
                    weekly_schedule.append(day_availability)
                
                # Déterminer le statut principal (majorité)
                if office_count >= online_count and office_count >= unavailable_count:
                    status_enum = AvailabilityStatus.OFFICE
                    status_counts["available"] += 1
                elif online_count >= unavailable_count:
                    status_enum = AvailabilityStatus.ONLINE
                    status_counts["occupied"] += 1
                else:
                    status_enum = AvailabilityStatus.UNAVAILABLE
                    status_counts["unavailable"] += 1
                
                # Tâche avec info ISO
                total_periods = office_count + online_count + unavailable_count
                if total_periods > 0:
                    available_periods = office_count + online_count
                    availability_rate = (available_periods / total_periods) * 100
                    current_task = f"Disponible {availability_rate:.0f}% - {iso_info}"
                
                # Créer le membre d'équipe simple
                team_members.append(TeamMember(
                    name=name,
                    status=status_enum,
                    current_task=current_task
                ))
                
                # Créer le membre détaillé
                detailed_member = DetailedTeamMember(
                    name=name,
                    role=None,
                    weekly_schedule=weekly_schedule,
                    overall_status=status_enum,
                    current_task=current_task
                )
                detailed_members.append(detailed_member)
                
                logger.info(f"✅ Added {name} with status {status_enum.value} and detailed schedule")
        
        # Calcul global
        total_members = len(team_members)
        available_members = status_counts["available"] + status_counts["occupied"]
        availability_rate = (available_members / total_members * 100) if total_members > 0 else 0
        
        return TeamAvailabilityData(
            summary=status_counts,
            team_members=team_members,
            detailed_members=detailed_members,
            upcoming_changes=[],
            weekly_availability_rate=round(availability_rate, 1),
            last_updated=datetime.now()
        )
    
    def parse_planning_data_iso(self, values, source_range: str) -> WeeklyPlanningData:
        """Parse optimisé avec informations ISO"""
        tasks = []
        completed_tasks = total_tasks = 0
        
        # Infos ISO
        iso_info = self.extract_iso_info_from_range(source_range)
        year, week_number, _ = self.get_iso_week_info()
        monday, sunday = self.get_iso_week_boundaries()
        
        # Parse amélioré des tâches - captures toutes les tâches même sans collaborateur explicite
        current_collaborateur = ""  # Garde le dernier collaborateur vu
        
        for row_index, row in enumerate(values[2:], start=3):  # Commence à la ligne 3 (après headers)
            if len(row) >= 3:
                collaborateur = row[0].strip() if row[0] else ""
                objectif = row[1].strip() if len(row) > 1 and row[1] else ""
                tache = row[2].strip() if len(row) > 2 and row[2] else ""
                
                # Logique simplifiée - GARDER LES VRAIES VALEURS du Google Sheet (sans défaut)
                priorite_display = ""  # Pas de valeur par défaut - respecter les cellules vides
                date_limite = ""
                statut_display = ""  # Pas de valeur par défaut - respecter les cellules vides
                
                # Chercher la priorité dans les colonnes D, E, F - GARDER LES VALEURS EXACTES
                for col_idx in [3, 4, 5]:
                    if col_idx < len(row) and row[col_idx]:
                        cell_value = row[col_idx].strip()
                        if cell_value in ['Haute', 'Moyenne', 'Basse']:
                            priorite_display = cell_value  # Garder la valeur exacte
                            break
                
                # Chercher la date (format XX/XX/XXXX) dans les colonnes E, F
                for col_idx in [4, 5]:
                    if col_idx < len(row) and row[col_idx]:
                        cell_value = row[col_idx].strip()
                        if '/' in cell_value and len(cell_value) >= 8:  # Format date
                            date_limite = cell_value
                            break
                
                # Chercher le statut dans les colonnes F, G - GARDER LES VALEURS EXACTES
                for col_idx in [5, 6]:
                    if col_idx < len(row) and row[col_idx]:
                        cell_value = row[col_idx].strip()
                        if cell_value in ['À faire', 'En cours', 'Terminé']:
                            statut_display = cell_value  # Garder la valeur exacte
                            break
                
                # Si pas de collaborateur dans cette ligne, utiliser le dernier vu
                if collaborateur:
                    current_collaborateur = collaborateur
                elif not collaborateur and current_collaborateur:
                    collaborateur = current_collaborateur
                
                # NOUVEAU: Accepter TOUTES les lignes avec un collaborateur, même si elles sont vides
                if collaborateur or current_collaborateur:
                    # Mapper les priorités pour l'enum interne (SEULEMENT si une priorité est définie)
                    priority_enum = {
                        'Haute': Priority.HIGH,
                        'Moyenne': Priority.MEDIUM,
                        'Basse': Priority.LOW
                    }.get(priorite_display, Priority.MEDIUM) if priorite_display else Priority.MEDIUM
                    
                    # Statuts - compter les terminées pour les stats
                    if statut_display == "Terminé":
                        completed_tasks += 1
                    
                    # Titre de la tâche - utiliser la tâche ou mettre vide si pas de tâche
                    task_title = tache if tache else ""
                    
                    # Récupérer les commentaires de la colonne G (index 6)
                    commentaires = row[6].strip() if len(row) > 6 and row[6] else ""
                    
                    task = WeeklyTask(
                        title=task_title,
                        description=f"{objectif[:200]}..." if len(objectif) > 200 else objectif,
                        time=date_limite,
                        priority=priority_enum,
                        assigned_to=collaborateur or current_collaborateur or "Non assigné",
                        status=statut_display,  # Valeur exacte du Google Sheet
                        objectives=objectif,
                        comments=commentaires,
                        priority_display=priorite_display  # Valeur exacte du Google Sheet
                    )
                    
                    tasks.append(task)
                    total_tasks += 1
                    
                    logger.info(f"📋 Tâche ajoutée: {task_title[:50]}... -> {collaborateur or 'Non assigné'}")
        
        logger.info(f"✅ Total tâches parsées: {total_tasks}, Terminées: {completed_tasks}")
        
        # PRÉSERVER L'ORDRE ORIGINAL DU GOOGLE SHEET - pas de tri
        # Les tâches doivent apparaître dans le même ordre que les lignes du Google Sheet
        sorted_tasks = tasks  # Garder l'ordre original
        
        # Répartition équilibrée sur la semaine (pour la structure interne)
        tasks_per_day = max(1, len(sorted_tasks) // 5)  # Répartir sur 5 jours ouvrables
        
        daily_schedule = {}
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        for i, day in enumerate(days):
            if i < 5:  # Jours ouvrables
                start_idx = i * tasks_per_day
                end_idx = start_idx + tasks_per_day
                if i == 4:  # Vendredi, prendre le reste
                    end_idx = len(sorted_tasks)
                day_tasks = sorted_tasks[start_idx:end_idx]
            else:  # Weekend
                day_tasks = []
            
            daily_schedule[day] = DailySchedule(tasks=day_tasks)
        
        # Priorités du jour = tâches HIGH priority
        today_priorities = [task for task in tasks if task.priority == Priority.HIGH][:5]
        
        return WeeklyPlanningData(
            week_number=week_number,
            year=year,
            week_start=monday.strftime("%Y-%m-%d"),
            week_end=sunday.strftime("%Y-%m-%d"),
            daily_schedule=daily_schedule,
            today_priorities=today_priorities,
            weekly_meetings=[],
            weekly_milestone=None,
            completion_stats={"completed": completed_tasks, "total": total_tasks},
            last_updated=datetime.now()
        )
    
    def extract_iso_info_from_range(self, range_name: str) -> str:
        """Extrait les infos ISO depuis le nom du range"""
        if "W" in range_name and "!" in range_name:
            # Ex: "W34!A3:O20"
            week_part = range_name.split("!")[0]
            if week_part.replace("W", "").isdigit():
                week_num = int(week_part.replace("W", ""))
                return f"Semaine ISO {week_num}"
        
        elif range_name.split("!")[0].isdigit():
            # Ex: "34!A2:G50"
            week_num = int(range_name.split("!")[0])
            return f"Semaine ISO {week_num}"
        
        # Default: semaine courante
        return self.format_iso_week_label()
    
    def get_iso_status_info(self) -> dict:
        """Retourne des infos détaillées sur l'état ISO"""
        year, week, weekday = self.get_iso_week_info()
        monday, sunday = self.get_iso_week_boundaries()
        
        # Jours de la semaine en français
        days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        return {
            "service_active": self.service is not None,
            "iso_year": year,
            "iso_week": week,
            "iso_weekday": weekday,
            "current_day": days_fr[weekday - 1],
            "week_label": self.format_iso_week_label(),
            "week_start": monday.strftime("%Y-%m-%d"),
            "week_end": sunday.strftime("%Y-%m-%d"),
            "availability_ranges": self.get_iso_availability_ranges()[:3],
            "planning_ranges": self.get_iso_planning_ranges()[:3],
            "last_check": datetime.now().isoformat()
        }
    
    async def get_featured_video(self) -> Optional[FacebookVideoData]:
        """Récupère la vidéo avec statut 'latest' depuis Google Sheets Public Engagement"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Récupère les données de la page Videos
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PUBLIC_ENGAGEMENT_SHEET_ID,
                range=settings.VIDEOS_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("Aucune donnée vidéo trouvée dans Google Sheets")
                return None
            
            # Chercher d'abord la vidéo avec statut "latest"
            for row in values:
                if len(row) >= 9:  # Assurer qu'on a assez de colonnes pour inclure le statut
                    try:
                        status = row[8] if len(row) > 8 else ""  # Colonne statut
                        
                        if status.lower() == "latest":
                            # Structure réelle détectée: Date, Titre, URL, Auteur, Vues, Likes, Comments, Shares, Statut
                            # Colonne 0: Date (format DD/MM/YYYY)
                            # Colonne 1: Titre/Auteur
                            # Colonne 2: URL Facebook
                            # Colonne 3: Auteur
                            # Colonne 4: Vues
                            # Colonne 5: Likes
                            # Colonne 6: Comments
                            # Colonne 7: Shares
                            # Colonne 8: Statut
                            
                            # Parser la date (format DD/MM/YYYY)
                            date_str = row[0] if len(row) > 0 else ""
                            try:
                                if date_str and "/" in date_str:
                                    day, month, year = date_str.split("/")
                                    published_date = datetime(int(year), int(month), int(day))
                                else:
                                    published_date = datetime.now()
                            except:
                                published_date = datetime.now()
                            
                            # Créer une URL thumbnail par défaut
                            thumbnail_url = "https://via.placeholder.com/500x300/3b82f6/ffffff?text=Vidéo+Facebook"
                            
                            video_data = FacebookVideoData(
                                id=f"video_latest",
                                title=row[1] if len(row) > 1 else "Vidéo Facebook",
                                thumbnail_url=thumbnail_url,
                                video_url=row[2] if len(row) > 2 else "",
                                views=int(row[4]) if len(row) > 4 and row[4].isdigit() else 0,
                                likes=int(row[5]) if len(row) > 5 and row[5].isdigit() else 0,
                                comments=int(row[6]) if len(row) > 6 and row[6].isdigit() else 0,
                                engagement_rate=0.0,  # Calculé après
                                published_date=published_date,
                                duration=180  # Durée par défaut
                            )
                            
                            # Calcul du taux d'engagement
                            if video_data.views > 0:
                                total_engagement = video_data.likes + video_data.comments
                                video_data.engagement_rate = (total_engagement / video_data.views) * 100
                            
                            logger.info(f"✅ Vidéo 'latest' récupérée: {video_data.title} ({video_data.views} vues)")
                            return video_data
                        
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Ligne vidéo ignorée: {e}")
                        continue
            
            # Fallback: si pas de vidéo "latest", prendre la première disponible
            logger.info("Aucune vidéo avec statut 'latest' trouvée, recherche de la première disponible...")
            for row in values:
                if len(row) >= 3:  # Au minimum Date, Titre, URL
                    try:
                        # Parser la date (format DD/MM/YYYY)
                        date_str = row[0] if len(row) > 0 else ""
                        try:
                            if date_str and "/" in date_str:
                                day, month, year = date_str.split("/")
                                published_date = datetime(int(year), int(month), int(day))
                            else:
                                published_date = datetime.now()
                        except:
                            published_date = datetime.now()
                        
                        # Créer une URL thumbnail par défaut
                        thumbnail_url = "https://via.placeholder.com/500x300/3b82f6/ffffff?text=Vidéo+Facebook"
                        
                        video_data = FacebookVideoData(
                            id=f"video_fallback",
                            title=row[1] if len(row) > 1 else "Vidéo Facebook",
                            thumbnail_url=thumbnail_url,
                            video_url=row[2] if len(row) > 2 else "",
                            views=int(row[4]) if len(row) > 4 and row[4].isdigit() else 0,
                            likes=int(row[5]) if len(row) > 5 and row[5].isdigit() else 0,
                            comments=int(row[6]) if len(row) > 6 and row[6].isdigit() else 0,
                            engagement_rate=0.0,  # Calculé après
                            published_date=published_date,
                            duration=180  # Durée par défaut
                        )
                        
                        # Calcul du taux d'engagement
                        if video_data.views > 0:
                            total_engagement = video_data.likes + video_data.comments
                            video_data.engagement_rate = (total_engagement / video_data.views) * 100
                        
                        logger.info(f"✅ Vidéo fallback récupérée: {video_data.title} ({video_data.views} vues)")
                        return video_data
                        
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Ligne vidéo ignorée: {e}")
                        continue
            
                logger.warning("Aucune vidéo valide trouvée")
                return None
            
        except Exception as e:
            logger.error(f"Erreur récupération vidéo depuis Google Sheets: {e}")
            return None
    
    def health_check(self) -> bool:
        """Health check avec vérification ISO"""
        try:
            if not self.service:
                return False
            
            # Test avec les ranges ISO
            iso_ranges = self.get_iso_availability_ranges()
            values, _ = self.try_get_sheet_data_iso(settings.AVAILABILITY_SHEET_ID, iso_ranges[:2])
            
            return values is not None
            
        except Exception as e:
            logger.error(f"Google Sheets ISO health check failed: {e}")
            return False