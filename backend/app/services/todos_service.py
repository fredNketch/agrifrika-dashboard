"""
Service pour récupérer les todos depuis Google Sheets
Migration depuis Basecamp vers Google Sheets
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.dashboard_models import TodoItem, TodosByCategory, TodosData
from app.services.google_sheets_service_iso import ISOGoogleSheetsService

logger = logging.getLogger(__name__)

class TodosService:
    """Service pour gérer les todos depuis Google Sheets"""
    
    def __init__(self):
        self.google_service = ISOGoogleSheetsService()
    
    async def get_todos_data(self) -> TodosData:
        """Récupère toutes les données de todos depuis le Google Sheet"""
        try:
            logger.info("Récupération des todos depuis Google Sheets")
            
            categories = []
            all_todos = []
            
            # Parcourir toutes les catégories/feuilles
            for sheet_name in settings.TODOS_SHEET_NAMES:
                try:
                    logger.info(f"Traitement de la catégorie: {sheet_name}")
                    todos_for_category = await self._get_todos_for_sheet(sheet_name)
                    
                    if todos_for_category:
                        # Statistiques par catégorie
                        total_count = len(todos_for_category)
                        pending_count = len([t for t in todos_for_category if t.status == "pending"])
                        completed_count = len([t for t in todos_for_category if t.status == "completed"])
                        
                        category_data = TodosByCategory(
                            category=sheet_name,
                            todos=todos_for_category,
                            total_count=total_count,
                            pending_count=pending_count,
                            completed_count=completed_count
                        )
                        categories.append(category_data)
                        all_todos.extend(todos_for_category)
                        
                        logger.info(f"Catégorie {sheet_name}: {total_count} todos ({pending_count} pending, {completed_count} completed)")
                
                except Exception as e:
                    logger.warning(f"Erreur lors du traitement de la catégorie {sheet_name}: {e}")
                    continue
            
            # Statistiques globales
            global_stats = self._calculate_global_stats(all_todos)
            
            # Identifier les todos urgents (échéance dans les 7 prochains jours)
            urgent_todos = self._identify_urgent_todos(all_todos)
            
            return TodosData(
                categories=categories,
                global_stats=global_stats,
                urgent_todos=urgent_todos,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des todos: {e}")
            # Retourner des données vides en cas d'erreur
            return TodosData(
                categories=[],
                global_stats={"total": 0, "pending": 0, "completed": 0, "in_progress": 0},
                urgent_todos=[],
                last_updated=datetime.now()
            )
    
    async def _get_todos_for_sheet(self, sheet_name: str) -> List[TodoItem]:
        """Récupère les todos pour une feuille donnée"""
        try:
            # Construire le range pour cette feuille
            range_name = settings.TODOS_RANGE_TEMPLATE.format(sheet_name=sheet_name)
            
            # Récupérer les données depuis Google Sheets
            result = self.google_service.service.spreadsheets().values().get(
                spreadsheetId=settings.TODOS_SHEET_ID,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                logger.warning(f"Aucune donnée trouvée pour la feuille {sheet_name}")
                return []
            
            todos = []
            # Ignorer la première ligne (headers)
            for i, row in enumerate(values[1:], start=2):
                try:
                    todo_item = self._parse_todo_row(row, sheet_name, i)
                    if todo_item:
                        todos.append(todo_item)
                except Exception as e:
                    logger.warning(f"Erreur lors du parsing de la ligne {i} dans {sheet_name}: {e}")
                    continue
            
            return todos
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des todos pour {sheet_name}: {e}")
            return []
    
    def _parse_todo_row(self, row: List[str], category: str, row_number: int) -> Optional[TodoItem]:
        """Parse une ligne de todo depuis le Google Sheet"""
        try:
            # Vérifier qu'on a au moins les colonnes essentielles
            if len(row) < 2:
                return None
                
            # Extraire les données (ID, Title, Status, Assigned_To, Due_Date)
            todo_id = row[0] if len(row) > 0 and row[0] else f"{category}_{row_number}"
            title = row[1] if len(row) > 1 and row[1] else ""
            status = row[2] if len(row) > 2 and row[2] else "pending"
            assigned_to = row[3] if len(row) > 3 and row[3] else None
            due_date = row[4] if len(row) > 4 and row[4] else None
            
            # Ignorer les lignes sans titre
            if not title or title.strip() == "":
                return None
            
            return TodoItem(
                id=todo_id,
                title=title.strip(),
                status=status.lower().strip(),
                assigned_to=assigned_to.strip() if assigned_to else None,
                due_date=due_date.strip() if due_date else None,
                category=category
            )
            
        except Exception as e:
            logger.warning(f"Erreur lors du parsing d'une ligne todo: {e}")
            return None
    
    def _calculate_global_stats(self, all_todos: List[TodoItem]) -> Dict[str, int]:
        """Calcule les statistiques globales"""
        total = len(all_todos)
        pending = len([t for t in all_todos if t.status == "pending"])
        completed = len([t for t in all_todos if t.status == "completed"])
        in_progress = len([t for t in all_todos if t.status == "in_progress"])
        
        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "in_progress": in_progress
        }
    
    def _identify_urgent_todos(self, all_todos: List[TodoItem]) -> List[TodoItem]:
        """Identifie les todos urgents (échéance dans les 7 prochains jours)"""
        urgent_todos = []
        current_date = datetime.now()
        urgent_threshold = current_date + timedelta(days=7)
        
        for todo in all_todos:
            if todo.status == "pending" and todo.due_date:
                try:
                    # Essayer de parser la date (différents formats possibles)
                    due_date = self._parse_date(todo.due_date)
                    if due_date and due_date <= urgent_threshold:
                        urgent_todos.append(todo)
                except Exception as e:
                    logger.warning(f"Erreur lors du parsing de la date {todo.due_date}: {e}")
                    continue
        
        # Trier par date d'échéance
        urgent_todos.sort(key=lambda t: self._parse_date(t.due_date) or datetime.max)
        
        return urgent_todos[:10]  # Limiter à 10 todos urgents
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date depuis différents formats possibles"""
        if not date_str or date_str.strip() == "":
            return None
            
        date_formats = [
            "%Y-%m-%d",      # 2024-08-23
            "%d/%m/%Y",      # 23/08/2024
            "%m/%d/%Y",      # 08/23/2024
            "%d-%m-%Y",      # 23-08-2024
            "%Y/%m/%d",      # 2024/08/23
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
                
        return None
    
    async def get_todos_by_category(self, category: str) -> Optional[TodosByCategory]:
        """Récupère les todos pour une catégorie spécifique"""
        try:
            if category not in settings.TODOS_SHEET_NAMES:
                logger.warning(f"Catégorie inconnue: {category}")
                return None
            
            todos = await self._get_todos_for_sheet(category)
            
            if not todos:
                return TodosByCategory(
                    category=category,
                    todos=[],
                    total_count=0,
                    pending_count=0,
                    completed_count=0
                )
            
            total_count = len(todos)
            pending_count = len([t for t in todos if t.status == "pending"])
            completed_count = len([t for t in todos if t.status == "completed"])
            
            return TodosByCategory(
                category=category,
                todos=todos,
                total_count=total_count,
                pending_count=pending_count,
                completed_count=completed_count
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des todos pour la catégorie {category}: {e}")
            return None
    
    async def get_urgent_todos(self) -> List[TodoItem]:
        """Récupère uniquement les todos urgents"""
        try:
            todos_data = await self.get_todos_data()
            return todos_data.urgent_todos
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des todos urgents: {e}")
            return []