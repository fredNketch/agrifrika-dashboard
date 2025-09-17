#!/usr/bin/env python3
"""
Script pour récupérer tous les todos depuis Basecamp 3 API
Documentation complète de l'API Basecamp consultée
"""

import os
import requests
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('../../config/.env')

class BasecampTodoRetriever:
    def __init__(self):
        self.account_id = os.getenv('BASECAMP_ACCOUNT_ID')
        self.project_id = os.getenv('BASECAMP_PROJECT_ID')
        self.access_token = os.getenv('BASECAMP_ACCESS_TOKEN')
        self.base_url = f"https://3.basecampapi.com/{self.account_id}"
        
        # Headers requis selon la documentation
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Dashboards Todo Retriever (contact@example.com)',
            'Content-Type': 'application/json'
        }
        
    def get_project_details(self) -> Dict[str, Any]:
        """
        Récupère les détails du projet pour trouver les todosets
        """
        project_url = f"{self.base_url}/projects/{self.project_id}.json"
        print(f"Récupération des détails du projet depuis: {project_url}")
        
        response = requests.get(project_url, headers=self.headers)
        print(f"Status Code projet: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erreur lors de la récupération du projet: {response.text}")
            return {}
            
        return response.json()
    
    def get_todolists(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les todolists du projet
        Nouvelle approche: récupérer d'abord les détails du projet
        """
        # D'abord récupérer les détails du projet
        project = self.get_project_details()
        if not project:
            return []
        
        print(f"Project: {project.get('name', 'Unknown')}")
        
        # Chercher l'outil todoset dans le dock
        dock = project.get('dock', [])
        todoset_tool = None
        
        for tool in dock:
            if tool.get('name') == 'todoset':
                todoset_tool = tool
                break
        
        if not todoset_tool:
            print("Aucun outil todoset trouvé dans le projet")
            return []
        
        if not todoset_tool.get('enabled'):
            print("L'outil todoset n'est pas activé pour ce projet")
            return []
            
        # Utiliser l'URL du todoset depuis le dock
        todoset_url = todoset_tool.get('url')
        if not todoset_url:
            print("URL du todoset non trouvée")
            return []
        
        print(f"Récupération du todoset depuis: {todoset_url}")
        response = requests.get(todoset_url, headers=self.headers)
        print(f"Status Code todoset: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Erreur lors de la récupération du todoset: {response.text}")
            return []
            
        todoset = response.json()
        
        # Le todoset contient une liste de todolists
        todolists = todoset.get('todolists', [])
        print(f"Todolists trouvées: {len(todolists)}")
        
        # Debug: afficher la structure des todolists
        if todolists:
            print("Structure des todolists:")
            print(json.dumps(todolists[0], indent=2)[:500] + "...")
        
        return todolists
    
    def get_todos_from_todolist(self, todolist_id: str) -> List[Dict[str, Any]]:
        """
        Récupère tous les todos d'une todolist spécifique
        Endpoint: GET /buckets/{project_id}/todolists/{todolist_id}/todos.json
        """
        todos_url = f"{self.base_url}/buckets/{self.project_id}/todolists/{todolist_id}/todos.json"
        print(f"Récupération des todos depuis: {todos_url}")
        
        response = requests.get(todos_url, headers=self.headers)
        print(f"Status Code todos: {response.status_code}")
        
        if response.status_code == 200:
            todos = response.json()
            print(f"Todos trouvés dans todolist {todolist_id}: {len(todos)}")
            return todos
        else:
            print(f"Erreur lors de la récupération des todos: {response.text}")
            return []
    
    def get_all_todos(self) -> Dict[str, Any]:
        """
        Récupère tous les todos de tous les todolists du projet
        """
        print("=== RÉCUPÉRATION DE TOUS LES TODOS BASECAMP ===")
        print(f"Account ID: {self.account_id}")
        print(f"Project ID: {self.project_id}")
        print()
        
        # Récupérer toutes les todolists
        todolists = self.get_todolists()
        
        all_todos = {
            'project_id': self.project_id,
            'account_id': self.account_id,
            'todolists': []
        }
        
        for todolist in todolists:
            todolist_id = todolist['id']
            todolist_name = todolist.get('name', todolist.get('title', f'Todolist {todolist_id}'))
            
            print(f"\n--- Todolist: {todolist_name} (ID: {todolist_id}) ---")
            
            # Récupérer tous les todos de cette todolist
            todos = self.get_todos_from_todolist(todolist_id)
            
            todolist_data = {
                'id': todolist_id,
                'name': todolist_name,
                'description': todolist.get('description', ''),
                'todos_count': len(todos),
                'todos': todos
            }
            
            all_todos['todolists'].append(todolist_data)
            
            # Afficher un résumé des todos
            for todo in todos:
                status = "[X]" if todo.get('completed') else "[ ]"
                assignees = [assignee['name'] for assignee in todo.get('assignees', [])]
                assignee_names = ', '.join(assignees) if assignees else 'Non assigné'
                due_date = todo.get('due_on', 'Pas de date')
                
                try:
                    content_preview = todo['content'][:60] + ('...' if len(todo['content']) > 60 else '')
                    print(f"  {status} {content_preview}")
                    print(f"    Assigné à: {assignee_names} | Échéance: {due_date}")
                except UnicodeEncodeError:
                    print(f"  {status} [Contenu avec caractères spéciaux - ID: {todo['id']}]")
                    print(f"    Assigné à: {assignee_names} | Échéance: {due_date}")
        
        return all_todos
    
    def save_todos_to_file(self, todos: Dict[str, Any], filename: str = 'basecamp_todos.json'):
        """
        Sauvegarde les todos dans un fichier JSON
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(todos, f, indent=2, ensure_ascii=False)
        
        print(f"\nTodos sauvegardés dans: {filename}")
        
        # Statistiques
        total_todos = sum(len(todolist['todos']) for todolist in todos['todolists'])
        completed_todos = sum(
            sum(1 for todo in todolist['todos'] if todo.get('completed'))
            for todolist in todos['todolists']
        )
        
        print(f"Total todolists: {len(todos['todolists'])}")
        print(f"Total todos: {total_todos}")
        print(f"Todos complétés: {completed_todos}")
        print(f"Todos en cours: {total_todos - completed_todos}")

def main():
    """
    Fonction principale pour récupérer et sauvegarder tous les todos
    """
    try:
        retriever = BasecampTodoRetriever()
        
        # Vérifier que les credentials sont chargés
        if not all([retriever.account_id, retriever.project_id, retriever.access_token]):
            print("ERREUR: Credentials Basecamp manquants dans .env")
            print(f"Account ID: {retriever.account_id}")
            print(f"Project ID: {retriever.project_id}")  
            print(f"Access Token: {'***' if retriever.access_token else 'None'}")
            return
        
        # Récupérer tous les todos
        all_todos = retriever.get_all_todos()
        
        # Sauvegarder dans un fichier
        retriever.save_todos_to_file(all_todos)
        
        print("\n=== RÉCUPÉRATION TERMINÉE AVEC SUCCÈS ===")
        
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()