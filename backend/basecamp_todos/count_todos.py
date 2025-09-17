#!/usr/bin/env python3
"""
Script rapide pour compter le nombre total de todos dans tous les groupes
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('../../config/.env')

def count_todos():
    account_id = os.getenv('BASECAMP_ACCOUNT_ID')
    project_id = os.getenv('BASECAMP_PROJECT_ID')
    access_token = os.getenv('BASECAMP_ACCESS_TOKEN')
    base_url = f"https://3.basecampapi.com/{account_id}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': 'Agrifrika Todo Counter (contact@agrifrika.com)',
        'Content-Type': 'application/json'
    }
    
    print("Comptage rapide des todos par groupe...")
    
    # Récupérer le projet
    project_url = f"{base_url}/projects/{project_id}.json"
    response = requests.get(project_url, headers=headers)
    project = response.json()
    
    # Récupérer le todoset
    dock = project.get('dock', [])
    todoset_tool = next((tool for tool in dock if tool.get('name') == 'todoset'), None)
    todoset_url = todoset_tool.get('url')
    
    response = requests.get(todoset_url, headers=headers)
    todoset = response.json()
    todolists = todoset.get('todolists', [])
    
    print(f"Nombre de groupes/todolists: {len(todolists)}")
    print()
    
    total_all_statuses = 0
    
    for todolist in todolists:
        todolist_id = todolist['id']
        todolist_name = todolist.get('title', f'Todolist {todolist_id}')
        
        print(f">> {todolist_name}")
        
        group_total = 0
        
        # Compter tous les statuts
        statuses = [
            ("en cours", {}),
            ("complétés", {"completed": "true"}),
            ("archivés actifs", {"status": "archived"}),
            ("archivés complétés", {"status": "archived", "completed": "true"}),
            ("corbeille", {"status": "trashed"})
        ]
        
        for status_name, params in statuses:
            try:
                todos_url = f"{base_url}/buckets/{project_id}/todolists/{todolist_id}/todos.json"
                response = requests.get(todos_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    todos = response.json()
                    count = len(todos)
                    if count > 0:
                        print(f"   {status_name}: {count}")
                    group_total += count
                else:
                    if response.status_code != 404:  # 404 est normal pour certains statuts
                        print(f"   {status_name}: erreur {response.status_code}")
            except Exception as e:
                print(f"   {status_name}: erreur {e}")
        
        print(f"   TOTAL GROUPE: {group_total}")
        print()
        total_all_statuses += group_total
    
    print(f">> TOTAL GÉNÉRAL (TOUS STATUTS): {total_all_statuses}")
    print("Comparaison avec l'interface Basecamp: 356 todos attendus")
    print(f"Différence: {356 - total_all_statuses}")

if __name__ == "__main__":
    count_todos()