#!/usr/bin/env python3
"""
Script avancé pour récupérer les todos Basecamp par groupe/todolist
Permet de cibler des groupes spécifiques ou tous les groupes
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from datetime import datetime
import argparse

# Charger les variables d'environnement
load_dotenv('../../config/.env')

class BasecampTodoGroupRetriever:
    def __init__(self):
        self.account_id = os.getenv('BASECAMP_ACCOUNT_ID')
        self.project_id = os.getenv('BASECAMP_PROJECT_ID')
        self.access_token = os.getenv('BASECAMP_ACCESS_TOKEN')
        self.base_url = f"https://3.basecampapi.com/{self.account_id}"
        
        # Headers requis selon la documentation
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Agrifrika Todo Group Retriever (contact@agrifrika.com)',
            'Content-Type': 'application/json'
        }
        
        # Cache pour éviter les requêtes répétées
        self._project_cache = None
        self._todolists_cache = None
        
    def get_project_details(self) -> Dict[str, Any]:
        """Récupère les détails du projet avec cache"""
        if self._project_cache is None:
            project_url = f"{self.base_url}/projects/{self.project_id}.json"
            response = requests.get(project_url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Erreur récupération projet: {response.text}")
                
            self._project_cache = response.json()
            
        return self._project_cache
    
    def get_all_todolists(self) -> List[Dict[str, Any]]:
        """Récupère toutes les todolists avec cache"""
        if self._todolists_cache is None:
            project = self.get_project_details()
            dock = project.get('dock', [])
            
            todoset_tool = next((tool for tool in dock if tool.get('name') == 'todoset'), None)
            if not todoset_tool or not todoset_tool.get('enabled'):
                raise Exception("Todoset non disponible dans ce projet")
            
            todoset_url = todoset_tool.get('url')
            response = requests.get(todoset_url, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Erreur récupération todoset: {response.text}")
                
            todoset = response.json()
            self._todolists_cache = todoset.get('todolists', [])
            
        return self._todolists_cache
    
    def get_todolist_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Trouve une todolist par son nom"""
        todolists = self.get_all_todolists()
        
        for todolist in todolists:
            todolist_name = todolist.get('title', todolist.get('name', ''))
            if todolist_name.lower() == name.lower():
                return todolist
                
        return None
    
    def get_todolist_by_id(self, todolist_id: int) -> Optional[Dict[str, Any]]:
        """Trouve une todolist par son ID"""
        todolists = self.get_all_todolists()
        return next((tl for tl in todolists if tl['id'] == todolist_id), None)
    
    def get_paginated_todos(self, url: str, params: dict = None) -> List[Dict[str, Any]]:
        """
        Récupère tous les todos en suivant la pagination Basecamp
        
        Args:
            url: URL de base pour les todos
            params: Paramètres de la requête (status, completed, etc.)
        """
        all_todos = []
        current_url = url
        page_count = 0
        
        while current_url:
            page_count += 1
            try:
                response = requests.get(current_url, headers=self.headers, params=params if page_count == 1 else None)
                
                if response.status_code != 200:
                    print(f"     >> Erreur page {page_count}: {response.status_code}")
                    break
                
                todos_page = response.json()
                all_todos.extend(todos_page)
                
                # Vérifier s'il y a une page suivante via le header Link
                link_header = response.headers.get('Link', '')
                next_url = None
                
                if link_header:
                    # Parser le header Link pour trouver rel="next"
                    for link in link_header.split(','):
                        if 'rel="next"' in link:
                            # Extraire l'URL entre < et >
                            next_url = link.split('<')[1].split('>')[0].strip()
                            break
                
                current_url = next_url
                
                # Debug: afficher l'info de pagination
                if page_count == 1 and len(todos_page) > 0:
                    total_count = response.headers.get('X-Total-Count', 'unknown')
                    print(f"     >> Page {page_count}: {len(todos_page)} items (Total collection: {total_count})")
                elif page_count > 1:
                    print(f"     >> Page {page_count}: {len(todos_page)} items")
                
            except Exception as e:
                print(f"     >> Erreur page {page_count}: {e}")
                break
        
        return all_todos

    def get_todos_from_todolist(self, todolist_id: int, include_completed: bool = True, include_archived: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère TOUS les todos d'une todolist spécifique dans tous les statuts avec pagination
        
        Args:
            todolist_id: ID de la todolist
            include_completed: Inclure les todos complétés (défaut: True)
            include_archived: Inclure les todos archivés (défaut: True)
        """
        all_todos = []
        existing_ids = set()
        
        base_url = f"{self.base_url}/buckets/{self.project_id}/todolists/{todolist_id}/todos.json"
        
        # 1. Todos actifs/en cours (défaut) - AVEC PAGINATION
        try:
            pending_todos = self.get_paginated_todos(base_url)
            all_todos.extend(pending_todos)
            existing_ids.update(todo['id'] for todo in pending_todos)
            print(f"     >> Todos en cours: {len(pending_todos)}")
        except Exception as e:
            print(f"     >> Erreur todos en cours: {e}")
        
        # 2. Todos complétés (completed=true) - AVEC PAGINATION
        if include_completed:
            try:
                params = {'completed': 'true'}
                completed_todos = self.get_paginated_todos(base_url, params)
                new_completed = [todo for todo in completed_todos if todo['id'] not in existing_ids]
                all_todos.extend(new_completed)
                existing_ids.update(todo['id'] for todo in new_completed)
                print(f"     >> Todos complétés: {len(new_completed)}")
            except Exception as e:
                print(f"     >> Erreur todos complétés: {e}")
        
        # 3. Todos archivés actifs (status=archived) - AVEC PAGINATION
        if include_archived:
            try:
                params = {'status': 'archived'}
                archived_todos = self.get_paginated_todos(base_url, params)
                new_archived = [todo for todo in archived_todos if todo['id'] not in existing_ids]
                all_todos.extend(new_archived)
                existing_ids.update(todo['id'] for todo in new_archived)
                print(f"     >> Todos archivés actifs: {len(new_archived)}")
            except Exception as e:
                print(f"     >> Erreur todos archivés: {e}")
        
        # 4. Todos archivés ET complétés (status=archived&completed=true) - AVEC PAGINATION
        if include_completed and include_archived:
            try:
                params = {'status': 'archived', 'completed': 'true'}
                archived_completed_todos = self.get_paginated_todos(base_url, params)
                new_arch_comp = [todo for todo in archived_completed_todos if todo['id'] not in existing_ids]
                all_todos.extend(new_arch_comp)
                existing_ids.update(todo['id'] for todo in new_arch_comp)
                print(f"     >> Todos archivés complétés: {len(new_arch_comp)}")
            except Exception as e:
                print(f"     >> Erreur todos archivés complétés: {e}")
        
        # 5. Todos dans la corbeille (status=trashed) - AVEC PAGINATION
        try:
            params = {'status': 'trashed'}
            trashed_todos = self.get_paginated_todos(base_url, params)
            new_trashed = [todo for todo in trashed_todos if todo['id'] not in existing_ids]
            all_todos.extend(new_trashed)
            existing_ids.update(todo['id'] for todo in new_trashed)
            print(f"     >> Todos dans la corbeille: {len(new_trashed)}")
        except Exception as e:
            print(f"     >> Erreur todos corbeille: {e}")
        
        print(f"     >> TOTAL RÉCUPÉRÉ: {len(all_todos)} todos")
        
        # Filtrage final si nécessaire
        if not include_completed:
            all_todos = [todo for todo in all_todos if not todo.get('completed', False)]
        
        if not include_archived:
            all_todos = [todo for todo in all_todos if todo.get('status') != 'archived']
            
        return all_todos
    
    def get_todos_for_groups(self, group_names: List[str] = None, include_completed: bool = True) -> Dict[str, Any]:
        """
        Récupère les todos pour des groupes spécifiques
        
        Args:
            group_names: Liste des noms de groupes (None = tous les groupes)
            include_completed: Inclure les todos complétés
        """
        todolists = self.get_all_todolists()
        
        # Filtrer les todolists si des noms spécifiques sont demandés
        if group_names:
            filtered_todolists = []
            for group_name in group_names:
                todolist = self.get_todolist_by_name(group_name)
                if todolist:
                    filtered_todolists.append(todolist)
                else:
                    print(f"⚠️  Groupe '{group_name}' non trouvé")
            todolists = filtered_todolists
        
        project = self.get_project_details()
        result = {
            'project': {
                'id': self.project_id,
                'name': project.get('name', 'Unknown'),
                'account_id': self.account_id
            },
            'retrieved_at': datetime.now().isoformat(),
            'include_completed': include_completed,
            'groups': []
        }
        
        for todolist in todolists:
            todolist_id = todolist['id']
            todolist_name = todolist.get('title', todolist.get('name', f'Todolist {todolist_id}'))
            
            print(f"\n>> Récupération du groupe: {todolist_name}")
            
            try:
                todos = self.get_todos_from_todolist(todolist_id, include_completed)
                
                # Statistiques
                total_todos = len(todos)
                completed_todos = sum(1 for todo in todos if todo.get('completed', False))
                pending_todos = total_todos - completed_todos
                
                group_data = {
                    'id': todolist_id,
                    'name': todolist_name,
                    'description': todolist.get('description', ''),
                    'url': todolist.get('url', ''),
                    'app_url': todolist.get('app_url', ''),
                    'statistics': {
                        'total_todos': total_todos,
                        'completed_todos': completed_todos,
                        'pending_todos': pending_todos,
                        'completion_percentage': round((completed_todos / total_todos * 100) if total_todos > 0 else 0, 1)
                    },
                    'todos': todos
                }
                
                result['groups'].append(group_data)
                
                # Affichage console
                print(f"   >> {completed_todos} complétés, {pending_todos} en cours (Total: {total_todos})")
                
                # Afficher quelques todos d'exemple
                for i, todo in enumerate(todos[:3]):  # Afficher seulement les 3 premiers
                    status = "[X]" if todo.get('completed') else "[ ]"
                    assignees = [assignee.get('name', '') for assignee in todo.get('assignees', [])]
                    assignee_text = f" ({', '.join(assignees)})" if assignees else ""
                    due_date = todo.get('due_on', '')
                    due_text = f" Due:{due_date}" if due_date else ""
                    
                    content_preview = todo.get('content', '')[:50]
                    if len(todo.get('content', '')) > 50:
                        content_preview += "..."
                        
                    print(f"   {status} {content_preview}{assignee_text}{due_text}")
                    
                if len(todos) > 3:
                    print(f"   ... et {len(todos) - 3} autres todos")
                    
            except Exception as e:
                print(f"   >> Erreur: {str(e)}")
                group_data = {
                    'id': todolist_id,
                    'name': todolist_name,
                    'error': str(e),
                    'todos': []
                }
                result['groups'].append(group_data)
        
        return result
    
    def list_available_groups(self) -> None:
        """Affiche la liste des groupes disponibles"""
        print("\n>> GROUPES/TODOLISTS DISPONIBLES:")
        print("=" * 50)
        
        todolists = self.get_all_todolists()
        
        for i, todolist in enumerate(todolists, 1):
            todolist_id = todolist['id']
            todolist_name = todolist.get('title', todolist.get('name', f'Todolist {todolist_id}'))
            description = todolist.get('description', 'Pas de description')
            
            # Nettoyer la description HTML
            import re
            description = re.sub(r'<[^>]+>', '', description)[:100]
            if len(description) > 100:
                description += "..."
            
            print(f"{i:2d}. >> {todolist_name}")
            print(f"     ID: {todolist_id}")
            print(f"     Description: {description}")
            print()
    
    def get_available_groups_data(self) -> List[Dict[str, Any]]:
        """Retourne la liste des groupes disponibles sous forme de données"""
        todolists = self.get_all_todolists()
        groups_data = []
        
        for todolist in todolists:
            todolist_id = todolist['id']
            todolist_name = todolist.get('title', todolist.get('name', f'Todolist {todolist_id}'))
            description = todolist.get('description', 'Pas de description')
            
            # Nettoyer la description HTML
            import re
            description = re.sub(r'<[^>]+>', '', description)
            
            groups_data.append({
                'id': todolist_id,
                'name': todolist_name,
                'description': description,
                'url': todolist.get('url', ''),
                'app_url': todolist.get('app_url', '')
            })
        
        return groups_data
    
    def save_to_file(self, data: Dict[str, Any], filename: str = None) -> str:
        """Sauvegarde les données dans un fichier JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"basecamp_todos_groups_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n>> Données sauvegardées dans: {filename}")
        return filename
    
    def generate_summary_report(self, data: Dict[str, Any]) -> str:
        """Génère un rapport de synthèse"""
        report = []
        report.append("=" * 60)
        report.append("RAPPORT DE SYNTHÈSE - TODOS PAR GROUPE")
        report.append("=" * 60)
        report.append(f"Projet: {data['project']['name']}")
        report.append(f"Date de récupération: {data['retrieved_at']}")
        report.append(f"Nombre de groupes: {len(data['groups'])}")
        report.append("")
        
        # Statistiques globales
        total_all = sum(group['statistics']['total_todos'] for group in data['groups'] if 'statistics' in group)
        completed_all = sum(group['statistics']['completed_todos'] for group in data['groups'] if 'statistics' in group)
        pending_all = total_all - completed_all
        
        report.append("STATISTIQUES GLOBALES:")
        report.append(f"   Total todos: {total_all}")
        report.append(f"   Complétés: {completed_all}")
        report.append(f"   En cours: {pending_all}")
        report.append(f"   Pourcentage de completion: {(completed_all/total_all*100):.1f}%" if total_all > 0 else "   Pourcentage de completion: 0%")
        report.append("")
        
        # Détail par groupe
        report.append("DÉTAIL PAR GROUPE:")
        for group in data['groups']:
            if 'statistics' in group:
                stats = group['statistics']
                report.append(f"   >> {group['name']}")
                report.append(f"      Total: {stats['total_todos']} | Complétés: {stats['completed_todos']} | En cours: {stats['pending_todos']}")
                report.append(f"      Completion: {stats['completion_percentage']}%")
                report.append("")
        
        # Top des groupes les plus actifs
        active_groups = sorted(
            [g for g in data['groups'] if 'statistics' in g],
            key=lambda x: x['statistics']['total_todos'],
            reverse=True
        )[:5]
        
        report.append("TOP 5 GROUPES LES PLUS ACTIFS:")
        for i, group in enumerate(active_groups, 1):
            stats = group['statistics']
            report.append(f"   {i}. {group['name']} - {stats['total_todos']} todos")
        
        return "\n".join(report)

def main():
    """Fonction principale avec arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description='Récupération des todos Basecamp par groupe')
    parser.add_argument('--groups', '-g', nargs='*', help='Noms des groupes à récupérer (défaut: tous)')
    parser.add_argument('--list', '-l', action='store_true', help='Lister les groupes disponibles')
    parser.add_argument('--no-completed', '-nc', action='store_true', help='Exclure les todos complétés')
    parser.add_argument('--output', '-o', help='Nom du fichier de sortie JSON')
    parser.add_argument('--report', '-r', action='store_true', help='Afficher le rapport de synthèse')
    
    args = parser.parse_args()
    
    try:
        retriever = BasecampTodoGroupRetriever()
        
        # Vérifier les credentials
        if not all([retriever.account_id, retriever.project_id, retriever.access_token]):
            print("ERREUR: Credentials Basecamp manquants dans .env")
            return
        
        print(f">> Connexion à Basecamp - Projet: {retriever.get_project_details().get('name', 'Unknown')}")
        
        # Lister les groupes disponibles
        if args.list:
            retriever.list_available_groups()
            return
        
        # Récupérer les todos
        include_completed = not args.no_completed
        data = retriever.get_todos_for_groups(args.groups, include_completed)
        
        # Sauvegarder
        filename = retriever.save_to_file(data, args.output)
        
        # Afficher le rapport
        if args.report:
            report = retriever.generate_summary_report(data)
            print(f"\n{report}")
        
        print(f"\n>> Récupération terminée avec succès!")
        print(f">> Fichier généré: {filename}")
        
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()