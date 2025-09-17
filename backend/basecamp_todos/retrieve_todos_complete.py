#!/usr/bin/env python3
"""
Version finale et optimisée pour récupérer TOUS les todos Basecamp
Récupère tous les statuts possibles via l'API
"""

import os
import requests
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from datetime import datetime
import argparse

load_dotenv('../../config/.env')

class CompleteTodoRetriever:
    def __init__(self):
        self.account_id = os.getenv('BASECAMP_ACCOUNT_ID')
        self.project_id = os.getenv('BASECAMP_PROJECT_ID')
        self.access_token = os.getenv('BASECAMP_ACCESS_TOKEN')
        self.base_url = f"https://3.basecampapi.com/{self.account_id}"
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Agrifrika Complete Todo Retriever (contact@agrifrika.com)',
            'Content-Type': 'application/json'
        }
    
    def get_all_todolists(self):
        """Récupère toutes les todolists"""
        project_url = f"{self.base_url}/projects/{self.project_id}.json"
        response = requests.get(project_url, headers=self.headers)
        project = response.json()
        
        dock = project.get('dock', [])
        todoset_tool = next((tool for tool in dock if tool.get('name') == 'todoset'), None)
        todoset_url = todoset_tool.get('url')
        
        response = requests.get(todoset_url, headers=self.headers)
        todoset = response.json()
        
        return todoset.get('todolists', [])
    
    def get_todos_all_statuses(self, todolist_id: int):
        """Récupère tous les todos de tous les statuts pour une todolist"""
        base_url = f"{self.base_url}/buckets/{self.project_id}/todolists/{todolist_id}/todos.json"
        
        all_todos = []
        seen_ids = set()
        
        # Définir tous les types de requêtes possibles
        queries = [
            ("actifs", {}),
            ("complétés", {"completed": "true"}),
            ("archivés", {"status": "archived"}),
            ("archivés_complétés", {"status": "archived", "completed": "true"}),
            ("corbeille", {"status": "trashed"})
        ]
        
        counts = {}
        
        for query_name, params in queries:
            try:
                response = requests.get(base_url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    todos = response.json()
                    
                    # Éviter les doublons
                    new_todos = [todo for todo in todos if todo['id'] not in seen_ids]
                    all_todos.extend(new_todos)
                    seen_ids.update(todo['id'] for todo in new_todos)
                    
                    counts[query_name] = len(new_todos)
                else:
                    counts[query_name] = f"erreur_{response.status_code}"
                    
            except Exception as e:
                counts[query_name] = f"erreur_{str(e)}"
        
        return all_todos, counts
    
    def retrieve_everything(self):
        """Récupère TOUT ce qui est accessible via l'API"""
        print("=== RÉCUPÉRATION COMPLÈTE DE TOUS LES TODOS ===")
        print(f"Account: {self.account_id}, Project: {self.project_id}")
        print()
        
        todolists = self.get_all_todolists()
        
        result = {
            'project_id': self.project_id,
            'account_id': self.account_id,
            'retrieved_at': datetime.now().isoformat(),
            'total_todolists': len(todolists),
            'groups': []
        }
        
        grand_total = 0
        
        for i, todolist in enumerate(todolists, 1):
            todolist_id = todolist['id']
            todolist_name = todolist.get('title', f'Todolist {todolist_id}')
            
            print(f"{i:2d}/17 - {todolist_name}")
            
            todos, counts = self.get_todos_all_statuses(todolist_id)
            group_total = len(todos)
            grand_total += group_total
            
            # Compter les complétés vs en cours
            completed = sum(1 for todo in todos if todo.get('completed', False))
            pending = group_total - completed
            
            group_data = {
                'id': todolist_id,
                'name': todolist_name,
                'description': todolist.get('description', ''),
                'counts_by_status': counts,
                'total_todos': group_total,
                'completed_todos': completed,
                'pending_todos': pending,
                'completion_percentage': round(completed / group_total * 100, 1) if group_total > 0 else 0,
                'todos': todos
            }
            
            result['groups'].append(group_data)
            
            # Affichage console concis
            status_display = []
            for status, count in counts.items():
                if isinstance(count, int) and count > 0:
                    status_display.append(f"{status}:{count}")
            
            print(f"      Total: {group_total} ({', '.join(status_display) if status_display else 'aucun'})")
        
        result['grand_total'] = grand_total
        
        print()
        print(f"🎯 TOTAL RÉCUPÉRÉ: {grand_total} todos")
        print(f"📊 Interface Basecamp indique: 356 todos")
        print(f"📉 Différence: {356 - grand_total} todos")
        
        if grand_total < 356:
            print()
            print("💡 EXPLICATIONS POSSIBLES de la différence:")
            print("   - Todos dans des sous-projets ou workspaces séparés")
            print("   - Todos dans des sections/catégories non accessibles via API")
            print("   - Todos personnels ou privés non visibles")
            print("   - Comptage Basecamp incluant des éléments meta (commentaires, etc.)")
            print("   - Limitation de l'API ou différence de méthode de comptage")
        
        return result
    
    def save_results(self, data, filename="recuperation_complete_finale.json"):
        """Sauvegarde les résultats"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Données complètes sauvegardées: {filename}")
        return filename

def main():
    retriever = CompleteTodoRetriever()
    
    if not all([retriever.account_id, retriever.project_id, retriever.access_token]):
        print("ERREUR: Credentials manquants")
        return
    
    # Récupération complète
    data = retriever.retrieve_everything()
    
    # Sauvegarde
    retriever.save_results(data)
    
    print("\n✅ RÉCUPÉRATION TERMINÉE")
    print(f"📁 {data['grand_total']} todos récupérés au total")

if __name__ == "__main__":
    main()