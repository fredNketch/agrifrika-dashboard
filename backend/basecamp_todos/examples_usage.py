#!/usr/bin/env python3
"""
Exemples d'utilisation du script de récupération des todos par groupe
"""

from retrieve_todos_by_group import BasecampTodoGroupRetriever
import json

def example_get_all_groups():
    """Exemple: Récupérer tous les groupes"""
    print("🔵 EXEMPLE 1: Récupération de tous les groupes")
    print("-" * 50)
    
    retriever = BasecampTodoGroupRetriever()
    data = retriever.get_todos_for_groups()
    
    filename = retriever.save_to_file(data, "tous_les_groupes.json")
    report = retriever.generate_summary_report(data)
    print(report)

def example_get_specific_groups():
    """Exemple: Récupérer des groupes spécifiques"""
    print("\n🔵 EXEMPLE 2: Récupération de groupes spécifiques")
    print("-" * 50)
    
    retriever = BasecampTodoGroupRetriever()
    
    # Groupes spécifiques à récupérer
    target_groups = ["Produit", "IT", "Marketing, Communication, RP"]
    
    data = retriever.get_todos_for_groups(target_groups)
    
    filename = retriever.save_to_file(data, "groupes_specifiques.json")
    report = retriever.generate_summary_report(data)
    print(report)

def example_get_only_pending():
    """Exemple: Récupérer seulement les todos en cours"""
    print("\n🔵 EXEMPLE 3: Récupération des todos en cours uniquement")
    print("-" * 50)
    
    retriever = BasecampTodoGroupRetriever()
    data = retriever.get_todos_for_groups(include_completed=False)
    
    filename = retriever.save_to_file(data, "todos_en_cours.json")
    report = retriever.generate_summary_report(data)
    print(report)

def example_analyze_specific_group():
    """Exemple: Analyser un groupe spécifique en détail"""
    print("\n🔵 EXEMPLE 4: Analyse détaillée du groupe Produit")
    print("-" * 50)
    
    retriever = BasecampTodoGroupRetriever()
    
    # Récupérer seulement le groupe Produit
    data = retriever.get_todos_for_groups(["Produit"])
    
    if data['groups']:
        group = data['groups'][0]
        print(f"📋 Analyse du groupe: {group['name']}")
        print(f"📊 Statistiques:")
        stats = group['statistics']
        print(f"   - Total todos: {stats['total_todos']}")
        print(f"   - Complétés: {stats['completed_todos']}")
        print(f"   - En cours: {stats['pending_todos']}")
        print(f"   - Pourcentage completion: {stats['completion_percentage']}%")
        
        print(f"\n📝 Tous les todos:")
        for todo in group['todos']:
            status = "✅" if todo.get('completed') else "⏳"
            assignees = [a['name'] for a in todo.get('assignees', [])]
            assignee_text = f" ({', '.join(assignees)})" if assignees else ""
            due_date = f" 📅 {todo.get('due_on', '')}" if todo.get('due_on') else ""
            
            print(f"   {status} {todo.get('content', '')[:60]}...{assignee_text}{due_date}")

def example_filter_by_assignee():
    """Exemple: Filtrer les todos par assigné"""
    print("\n🔵 EXEMPLE 5: Filtrer les todos par assigné")
    print("-" * 50)
    
    retriever = BasecampTodoGroupRetriever()
    data = retriever.get_todos_for_groups()
    
    # Filtrer pour un assigné spécifique
    target_assignee = "Adrien Djonkep"  # Remplacer par le nom désiré
    
    print(f"🔍 Todos assignés à {target_assignee}:")
    
    for group in data['groups']:
        group_todos = []
        for todo in group['todos']:
            assignees = [a['name'] for a in todo.get('assignees', [])]
            if target_assignee in assignees:
                group_todos.append(todo)
        
        if group_todos:
            print(f"\n📋 {group['name']} ({len(group_todos)} todos):")
            for todo in group_todos:
                status = "✅" if todo.get('completed') else "⏳"
                due_date = f" 📅 {todo.get('due_on', '')}" if todo.get('due_on') else ""
                print(f"   {status} {todo.get('content', '')[:50]}...{due_date}")

def example_upcoming_deadlines():
    """Exemple: Identifier les todos avec échéances proches"""
    print("\n🔵 EXEMPLE 6: Todos avec échéances dans les 30 prochains jours")
    print("-" * 50)
    
    from datetime import datetime, timedelta
    
    retriever = BasecampTodoGroupRetriever()
    data = retriever.get_todos_for_groups(include_completed=False)
    
    now = datetime.now()
    in_30_days = now + timedelta(days=30)
    
    upcoming_todos = []
    
    for group in data['groups']:
        for todo in group['todos']:
            due_date_str = todo.get('due_on')
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
                    if now <= due_date <= in_30_days:
                        upcoming_todos.append({
                            'group': group['name'],
                            'todo': todo,
                            'due_date': due_date,
                            'days_remaining': (due_date - now).days
                        })
                except:
                    pass
    
    # Trier par échéance
    upcoming_todos.sort(key=lambda x: x['due_date'])
    
    print(f"🚨 {len(upcoming_todos)} todos avec échéance dans les 30 prochains jours:")
    
    for item in upcoming_todos:
        todo = item['todo']
        assignees = [a['name'] for a in todo.get('assignees', [])]
        assignee_text = f" ({', '.join(assignees)})" if assignees else ""
        days = item['days_remaining']
        urgency = "🔴" if days <= 7 else "🟡" if days <= 14 else "🟢"
        
        print(f"   {urgency} Dans {days} jours - {item['group']}")
        print(f"       {todo.get('content', '')[:50]}...{assignee_text}")
        print(f"       📅 {item['due_date'].strftime('%d/%m/%Y')}")
        print()

def main():
    """Exécuter tous les exemples"""
    print("🎯 EXEMPLES D'UTILISATION - RÉCUPÉRATION TODOS PAR GROUPE")
    print("=" * 70)
    
    try:
        # Exemple 1: Tous les groupes
        # example_get_all_groups()
        
        # Exemple 2: Groupes spécifiques
        # example_get_specific_groups()
        
        # Exemple 3: Seulement les todos en cours
        # example_get_only_pending()
        
        # Exemple 4: Analyse détaillée d'un groupe
        example_analyze_specific_group()
        
        # Exemple 5: Filtrer par assigné
        # example_filter_by_assignee()
        
        # Exemple 6: Échéances proches
        # example_upcoming_deadlines()
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()