"""
Service Basecamp API pour AGRIFRIKA Dashboard
Récupération des todos et projets
"""

import logging
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.models.dashboard_models import BasecampData, BasecampTodo, ActionPlanItem, TaskStatus

logger = logging.getLogger(__name__)

class BasecampService:
    """Service pour interagir avec l'API Basecamp"""
    
    def __init__(self):
        self.base_url = f"https://3.basecampapi.com/{settings.BASECAMP_ACCOUNT_ID}"
        self.headers = {
            'Authorization': f'Bearer {settings.BASECAMP_ACCESS_TOKEN}',
            'User-Agent': 'AGRIFRIKA Dashboard (contact@agrifrika.com)',
            'Content-Type': 'application/json'
        }
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Récupère la liste des projets Basecamp"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/projects.json",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Erreur récupération projets Basecamp: {e}")
            return []
    
    async def get_project_todos(self, project_id: str) -> List[Dict[str, Any]]:
        """Récupère les todos d'un projet spécifique"""
        try:
            async with httpx.AsyncClient() as client:
                # Récupérer les todosets du projet
                response = await client.get(
                    f"{self.base_url}/projects/{project_id}/todosets.json",
                    headers=self.headers
                )
                response.raise_for_status()
                todosets = response.json()
                
                all_todos = []
                for todoset in todosets:
                    # Récupérer les todos de chaque todoset
                    todos_response = await client.get(
                        f"{self.base_url}/projects/{project_id}/todosets/{todoset['id']}/todos.json",
                        headers=self.headers
                    )
                    todos_response.raise_for_status()
                    todos = todos_response.json()
                    all_todos.extend(todos)
                
                return all_todos
                
        except Exception as e:
            logger.error(f"Erreur récupération todos projet {project_id}: {e}")
            return []
    
    async def get_all_todos(self) -> Optional[BasecampData]:
        """Récupère tous les todos de tous les projets"""
        try:
            projects = await self.get_projects()
            
            all_todos = []
            completed_today = 0
            today = datetime.now().date()
            
            for project in projects:
                project_todos = await self.get_project_todos(project['id'])
                
                for todo in project_todos:
                    # Parser le statut
                    status = TaskStatus.A_FAIRE  # Par défaut
                    if todo.get('completed'):
                        status = TaskStatus.TERMINE
                        # Vérifier si complété aujourd'hui
                        if todo.get('completed_at'):
                            completed_date = datetime.fromisoformat(
                                todo['completed_at'].replace('Z', '+00:00')
                            ).date()
                            if completed_date == today:
                                completed_today += 1
                    elif todo.get('assignees'):
                        status = TaskStatus.EN_COURS
                    
                    # Déterminer la date d'échéance
                    due_date = None
                    if todo.get('due_on'):
                        due_date = datetime.fromisoformat(todo['due_on'])
                    
                    # Assigné à
                    assigned_to = None
                    if todo.get('assignees'):
                        assigned_to = ', '.join([assignee['name'] for assignee in todo['assignees']])
                    
                    basecamp_todo = BasecampTodo(
                        id=str(todo['id']),
                        title=todo.get('content', 'Todo sans titre'),
                        status=status,
                        assigned_to=assigned_to,
                        due_date=due_date,
                        project=project.get('name', 'Projet sans nom')
                    )
                    
                    all_todos.append(basecamp_todo)
            
            return BasecampData(
                todos=all_todos,
                projects_count=len(projects),
                completed_today=completed_today,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération tous les todos Basecamp: {e}")
            return None
    
    async def get_action_plan_items(self) -> List[ActionPlanItem]:
        """Récupère les éléments du plan d'action depuis Basecamp"""
        basecamp_data = await self.get_all_todos()
        
        if not basecamp_data:
            return []
        
        action_items = []
        
        # Convertir les todos Basecamp en éléments de plan d'action
        for todo in basecamp_data.todos:
            # Déterminer la catégorie basée sur la date d'échéance
            category = "this_week"  # Par défaut
            if todo.due_date:
                days_until_due = (todo.due_date.date() - datetime.now().date()).days
                if days_until_due <= 1:
                    category = "today"
                elif days_until_due <= 7:
                    category = "this_week"
                else:
                    category = "later"
            
            # Déterminer la priorité
            priority = "moyenne"
            if todo.status == TaskStatus.TERMINE:
                priority = "basse"
            elif category == "today":
                priority = "haute"
            
            action_item = ActionPlanItem(
                id=todo.id,
                title=todo.title,
                assigned_to=todo.assigned_to or "Non assigné",
                due_date=todo.due_date,
                priority=priority,
                status=todo.status.value,
                category=category
            )
            
            action_items.append(action_item)
        
        return action_items
    
    async def get_dashboard_data(self) -> Optional[BasecampData]:
        """Alias pour get_all_todos - cohérence avec les autres services"""
        return await self.get_all_todos()
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Basecamp"""
        try:
            import requests  # Synchrone pour le health check
            response = requests.get(
                f"{self.base_url}/projects.json",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Basecamp health check failed: {e}")
            return False