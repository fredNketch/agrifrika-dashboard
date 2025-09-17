#!/usr/bin/env python3
"""
Script d'automatisation : Basecamp → Google Sheets
Synchronise automatiquement les todos Basecamp vers vos Google Sheets
Basé sur la pagination complète développée dans retrieve_todos_by_group.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import du convertisseur de dates avancé
from date_converter import BasecampDateConverter

# Ajouter le chemin backend pour imports
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from app.core.config import settings
from app.services.google_sheets_write_service import GoogleSheetsWriteService
from retrieve_todos_by_group import BasecampTodoGroupRetriever

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasecampToSheetsSync:
    """Synchronisation automatique Basecamp → Google Sheets"""
    
    def __init__(self):
        self.basecamp_retriever = BasecampTodoGroupRetriever()
        self.sheets_service = GoogleSheetsWriteService()
        self.date_converter = BasecampDateConverter()
        
        # Mapping des noms de groupes Basecamp vers les sheets Google
        self.group_to_sheet_mapping = {
            "Marketing, Communication, RP": "Marketing Communication RP",
            "IT": "IT", 
            "Money": "Money",
            "Administration / Management": "Administration-management",
            "Produit": "Produit",
            "Opérations": "Opérations",
            "Commercial": "Commercial",
            "Partenariats": "Partenariats",
            "Design & Branding": "Design & Branding",
            "Investors": "Investors",
            "Prestataires": "Prestataires",
            "Ressources matérielles": "Ressources Matérielles",  # Correspondance exacte
            "Capital Humain - Stages": "Capital Humain - Stages",
            "Capital Humain": "Capital Humain",  # Nouveau
            "Agrifrika - Copyright": "Agrifika-Copyright",
            "Abaca Assessment - Investment Readiness Tool": "Abaca Assessment",
            "Accélération / Développement": "Accélération Développement"  # Nouveau
        }
    
    def transform_basecamp_todo_to_sheets_row(self, todo: Dict[str, Any]) -> List[str]:
        """Transforme un todo Basecamp en ligne Google Sheets"""
        try:
            # Mapping des champs
            todo_id = str(todo.get('id', ''))
            title = todo.get('content', todo.get('title', ''))
            
            # Mapping du statut
            completed = todo.get('completed', False)
            status = "completed" if completed else "pending"
            
            # Assigné à (extraire les noms depuis les données assignées)
            assigned_to = ""
            assignees = todo.get('assignees', [])
            if assignees:
                # Prendre les noms de tous les assignés et les joindre avec des virgules
                names = [assignee.get('name', '') for assignee in assignees if assignee.get('name')]
                assigned_to = ', '.join(names)
            
            # Date d'échéance avec convertisseur avancé
            due_date = ""
            due_on = todo.get('due_on')
            if due_on:
                # Utiliser le convertisseur avancé pour une conversion robuste
                due_date = self.date_converter.convert_to_format(due_on, 'google_sheets_fr')
                
                # Log pour debug si conversion échoue
                if due_date == due_on:  # Pas de conversion effectuée
                    validation = self.date_converter.validate_date(due_on)
                    if not validation['is_valid']:
                        logger.warning(f"Date non convertie pour todo {todo.get('id', 'unknown')}: '{due_on}' - Erreurs: {validation['errors']}")
                else:
                    logger.debug(f"Date convertie: '{due_on}' → '{due_date}'")
            
            return [todo_id, title, status, assigned_to, due_date]
            
        except Exception as e:
            logger.warning(f"Erreur lors de la transformation du todo {todo.get('id', 'unknown')}: {e}")
            return []
    
    def clear_sheet_data(self, sheet_name: str) -> bool:
        """Vide les données d'un sheet (garde les headers)"""
        try:
            range_name = f"{sheet_name}!A2:E500"
            return self.sheets_service.clear_range(settings.TODOS_SHEET_ID, range_name)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du vidage du sheet '{sheet_name}': {e}")
            return False
    
    def write_todos_to_sheet(self, sheet_name: str, todos: List[Dict[str, Any]]) -> bool:
        """Écrit les todos dans un sheet Google"""
        try:
            if not todos:
                logger.info(f"Aucun todo à écrire pour '{sheet_name}'")
                return True
            
            # Transformer les todos en lignes
            rows = []
            for todo in todos:
                row = self.transform_basecamp_todo_to_sheets_row(todo)
                if row:
                    rows.append(row)
            
            if not rows:
                logger.warning(f"Aucune ligne valide à écrire pour '{sheet_name}'")
                return True
            
            # Limiter à 499 lignes maximum (A2:E500)
            rows = rows[:499]
            
            # Construire le range
            end_row = len(rows) + 1  # +1 car on commence à A2
            range_name = f"{sheet_name}!A2:E{end_row}"
            
            body = {
                'values': rows
            }
            
            result = self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=settings.TODOS_SHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            logger.info(f"✅ '{sheet_name}': {len(rows)} todos écrits ({updated_cells} cellules mises à jour)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'écriture dans '{sheet_name}': {e}")
            return False
    
    def sync_group_to_sheet(self, basecamp_group: str, sheet_name: str) -> Dict[str, Any]:
        """Synchronise un groupe Basecamp vers un sheet Google"""
        try:
            logger.info(f"🔄 Synchronisation: '{basecamp_group}' → '{sheet_name}'")
            
            # Récupérer les todos depuis Basecamp
            basecamp_data = self.basecamp_retriever.get_todos_for_groups([basecamp_group])
            
            if not basecamp_data or 'groups' not in basecamp_data:
                logger.warning(f"Aucune donnée Basecamp trouvée pour '{basecamp_group}'")
                return {'success': False, 'error': 'No Basecamp data'}
            
            # Extraire les todos du groupe
            group_data = None
            for group in basecamp_data['groups']:
                if group['name'] == basecamp_group:
                    group_data = group
                    break
            
            if not group_data:
                logger.warning(f"Groupe '{basecamp_group}' non trouvé dans les données Basecamp")
                return {'success': False, 'error': 'Group not found'}
            
            todos = group_data.get('todos', [])
            
            # Vider le sheet et écrire les nouveaux todos
            if self.clear_sheet_data(sheet_name):
                if self.write_todos_to_sheet(sheet_name, todos):
                    return {
                        'success': True,
                        'todos_count': len(todos),
                        'basecamp_group': basecamp_group,
                        'sheet_name': sheet_name
                    }
            
            return {'success': False, 'error': 'Write operation failed'}
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la synchronisation '{basecamp_group}' → '{sheet_name}': {e}")
            return {'success': False, 'error': str(e)}
    
    def detect_missing_categories(self) -> Dict[str, Any]:
        """Détecte les catégories Basecamp qui n'existent pas encore dans Google Sheets"""
        try:
            logger.info("🔍 Détection des catégories manquantes...")
            
            # Récupérer tous les groupes Basecamp disponibles
            basecamp_groups = self.basecamp_retriever.get_available_groups_data()
            basecamp_names = [group['name'] for group in basecamp_groups]
            
            # Récupérer tous les onglets Google Sheets existants
            existing_sheets = self.sheets_service.list_all_sheets(settings.TODOS_SHEET_ID)
            
            # Identifier les correspondances manquantes
            missing_in_sheets = []
            missing_in_mapping = []
            
            for basecamp_name in basecamp_names:
                # Vérifier si on a un mapping pour ce groupe
                if basecamp_name not in self.group_to_sheet_mapping:
                    missing_in_mapping.append(basecamp_name)
                    continue
                
                # Vérifier si l'onglet existe dans Google Sheets
                expected_sheet_name = self.group_to_sheet_mapping[basecamp_name]
                if expected_sheet_name not in existing_sheets:
                    missing_in_sheets.append({
                        'basecamp_group': basecamp_name,
                        'expected_sheet': expected_sheet_name
                    })
            
            return {
                'basecamp_groups': basecamp_names,
                'existing_sheets': existing_sheets,
                'missing_in_sheets': missing_in_sheets,
                'missing_in_mapping': missing_in_mapping,
                'analysis_complete': True
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la détection des catégories manquantes: {e}")
            return {'analysis_complete': False, 'error': str(e)}
    
    def create_missing_sheets(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Crée automatiquement les onglets manquants avec headers"""
        try:
            if not detection_result.get('analysis_complete'):
                return {'success': False, 'error': 'Analysis not complete'}
            
            missing_sheets = detection_result.get('missing_in_sheets', [])
            
            if not missing_sheets:
                logger.info("✅ Aucun onglet manquant détecté")
                return {'success': True, 'created_sheets': []}
            
            # Headers standards pour tous les onglets todos
            headers = ["ID", "Title", "Status", "Assigned_To", "Due_Date"]
            created_sheets = []
            failed_sheets = []
            
            for missing in missing_sheets:
                sheet_name = missing['expected_sheet']
                basecamp_group = missing['basecamp_group']
                
                logger.info(f"🔧 Création de l'onglet '{sheet_name}' pour le groupe '{basecamp_group}'")
                
                if self.sheets_service.create_sheet_with_headers(settings.TODOS_SHEET_ID, sheet_name, headers):
                    created_sheets.append({
                        'sheet_name': sheet_name,
                        'basecamp_group': basecamp_group
                    })
                    logger.info(f"✅ Onglet '{sheet_name}' créé avec succès")
                else:
                    failed_sheets.append({
                        'sheet_name': sheet_name,
                        'basecamp_group': basecamp_group
                    })
                    logger.error(f"❌ Échec création onglet '{sheet_name}'")
            
            return {
                'success': True,
                'created_sheets': created_sheets,
                'failed_sheets': failed_sheets,
                'total_created': len(created_sheets),
                'total_failed': len(failed_sheets)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création des onglets manquants: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_all_groups(self, groups_filter: Optional[List[str]] = None, auto_create_sheets: bool = True) -> Dict[str, Any]:
        """Synchronise tous les groupes ou une liste filtrée"""
        try:
            logger.info("🚀 Début de la synchronisation complète Basecamp → Google Sheets")
            
            # Étape 1: Détection et création automatique des onglets manquants
            creation_result = {'created_sheets': [], 'failed_sheets': []}
            if auto_create_sheets:
                logger.info("🔍 Vérification des catégories manquantes...")
                detection_result = self.detect_missing_categories()
                
                if detection_result.get('analysis_complete'):
                    missing_sheets = detection_result.get('missing_in_sheets', [])
                    missing_mappings = detection_result.get('missing_in_mapping', [])
                    
                    if missing_sheets:
                        logger.info(f"📋 Onglets manquants détectés: {len(missing_sheets)}")
                        creation_result = self.create_missing_sheets(detection_result)
                    
                    if missing_mappings:
                        logger.warning(f"⚠️ Groupes sans mapping détectés: {missing_mappings}")
                        logger.warning("Ces groupes seront ignorés dans la synchronisation")
                else:
                    logger.warning("⚠️ Échec de la détection des catégories manquantes")
            
            # Étape 2: Déterminer les groupes à synchroniser
            groups_to_sync = groups_filter or list(self.group_to_sheet_mapping.keys())
            
            results = {
                'sync_timestamp': datetime.now().isoformat(),
                'total_groups': len(groups_to_sync),
                'successful_syncs': 0,
                'failed_syncs': 0,
                'details': []
            }
            
            for basecamp_group in groups_to_sync:
                sheet_name = self.group_to_sheet_mapping.get(basecamp_group)
                
                if not sheet_name:
                    logger.warning(f"⚠️  Aucun mapping trouvé pour le groupe '{basecamp_group}'")
                    results['details'].append({
                        'basecamp_group': basecamp_group,
                        'success': False,
                        'error': 'No sheet mapping found'
                    })
                    results['failed_syncs'] += 1
                    continue
                
                # Synchroniser ce groupe
                sync_result = self.sync_group_to_sheet(basecamp_group, sheet_name)
                results['details'].append(sync_result)
                
                if sync_result['success']:
                    results['successful_syncs'] += 1
                    logger.info(f"✅ Synchronisation réussie: '{basecamp_group}' ({sync_result.get('todos_count', 0)} todos)")
                else:
                    results['failed_syncs'] += 1
                    logger.error(f"❌ Échec synchronisation: '{basecamp_group}' - {sync_result.get('error', 'Unknown error')}")
            
            # Résumé final
            success_rate = (results['successful_syncs'] / results['total_groups']) * 100
            logger.info(f"🎯 Synchronisation terminée: {results['successful_syncs']}/{results['total_groups']} groupes réussis ({success_rate:.1f}%)")
            
            # Statistiques de conversion des dates
            date_stats = self.date_converter.get_conversion_stats()
            if date_stats['total_conversions'] > 0:
                logger.info(f"📅 Dates converties: {date_stats['successful_conversions']}/{date_stats['total_conversions']} ({date_stats['success_rate']}%)")
                if date_stats['formats_detected']:
                    logger.info(f"📋 Formats détectés: {', '.join(date_stats['formats_detected'].keys())}")
            
            # Ajouter les stats de dates au résultat
            results['date_conversion_stats'] = date_stats
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur critique lors de la synchronisation complète: {e}")
            return {
                'success': False,
                'error': str(e),
                'sync_timestamp': datetime.now().isoformat()
            }
    
    def create_headers_if_missing(self, sheet_name: str) -> bool:
        """Crée les headers dans un sheet s'ils sont manquants"""
        try:
            # Headers standard
            headers = ["ID", "Title", "Status", "Assigned_To", "Due_Date"]
            
            range_name = f"{sheet_name}!A1:E1"
            body = {
                'values': [headers]
            }
            
            result = self.sheets_service.service.spreadsheets().values().update(
                spreadsheetId=settings.TODOS_SHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"✅ Headers créés pour '{sheet_name}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création des headers pour '{sheet_name}': {e}")
            return False

def main():
    """Fonction principale avec options CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Synchronisation Basecamp → Google Sheets")
    parser.add_argument('--groups', nargs='*', help='Groupes spécifiques à synchroniser')
    parser.add_argument('--create-headers', action='store_true', help='Créer les headers dans tous les sheets')
    parser.add_argument('--dry-run', action='store_true', help='Mode test sans écriture')
    parser.add_argument('--output', help='Fichier de sortie pour le rapport JSON')
    parser.add_argument('--detect-missing', action='store_true', help='Détecter les catégories manquantes seulement')
    parser.add_argument('--create-missing', action='store_true', help='Créer les onglets manquants seulement')
    parser.add_argument('--no-auto-create', action='store_true', help='Désactiver la création automatique des onglets')
    
    args = parser.parse_args()
    
    syncer = BasecampToSheetsSync()
    
    try:
        # Détection des catégories manquantes seulement
        if args.detect_missing:
            logger.info("🔍 Détection des catégories manquantes uniquement...")
            detection_result = syncer.detect_missing_categories()
            
            if detection_result.get('analysis_complete'):
                print(f"\n=== ANALYSE DES CATEGORIES ===")
                print(f"Groupes Basecamp: {len(detection_result['basecamp_groups'])}")
                print(f"Onglets Google Sheets: {len(detection_result['existing_sheets'])}")
                print(f"Onglets manquants: {len(detection_result['missing_in_sheets'])}")
                print(f"Groupes sans mapping: {len(detection_result['missing_in_mapping'])}")
                
                if detection_result['missing_in_sheets']:
                    print(f"\n=== ONGLETS A CREER ===")
                    for missing in detection_result['missing_in_sheets']:
                        print(f"  - {missing['expected_sheet']} (pour {missing['basecamp_group']})")
                
                if detection_result['missing_in_mapping']:
                    print(f"\n=== GROUPES SANS MAPPING ===")
                    for group in detection_result['missing_in_mapping']:
                        print(f"  - {group}")
                        
                print(f"\n=== GROUPES BASECAMP DETECTES ===")
                for group in detection_result['basecamp_groups'][:5]:  # Premiers 5 seulement
                    print(f"  - {group}")
                if len(detection_result['basecamp_groups']) > 5:
                    print(f"  ... et {len(detection_result['basecamp_groups']) - 5} autres")
                    
                print(f"\n=== ONGLETS GOOGLE SHEETS EXISTANTS ===")
                for sheet in detection_result['existing_sheets']:
                    print(f"  - {sheet}")
            return
        
        # Création des onglets manquants seulement  
        if args.create_missing:
            logger.info("🔧 Création des onglets manquants uniquement...")
            detection_result = syncer.detect_missing_categories()
            
            if detection_result.get('analysis_complete'):
                creation_result = syncer.create_missing_sheets(detection_result)
                print(f"\n🔧 CRÉATION D'ONGLETS")
                print(f"Onglets créés: {creation_result.get('total_created', 0)}")
                print(f"Échecs: {creation_result.get('total_failed', 0)}")
                
                for created in creation_result.get('created_sheets', []):
                    print(f"  ✅ {created['sheet_name']}")
                    
                for failed in creation_result.get('failed_sheets', []):
                    print(f"  ❌ {failed['sheet_name']}")
            return
        
        # Créer les headers si demandé
        if args.create_headers:
            logger.info("🔧 Création des headers dans tous les sheets...")
            for sheet_name in settings.TODOS_SHEET_NAMES:
                syncer.create_headers_if_missing(sheet_name)
            logger.info("✅ Headers créés avec succès")
        
        # Mode dry-run
        if args.dry_run:
            logger.info("🧪 Mode DRY-RUN activé - Aucune écriture ne sera effectuée")
            # Ici on pourrait juste afficher ce qui serait synchronisé
            return
        
        # Synchronisation avec ou sans auto-création
        auto_create = not args.no_auto_create
        results = syncer.sync_all_groups(args.groups, auto_create_sheets=auto_create)
        
        # Sauvegarder le rapport si demandé
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Rapport sauvegardé dans '{args.output}'")
        
        # Afficher le résumé
        print(f"\n🎯 RÉSUMÉ DE LA SYNCHRONISATION")
        print(f"Groupes traités: {results['total_groups']}")
        print(f"Réussites: {results['successful_syncs']}")
        print(f"Échecs: {results['failed_syncs']}")
        print(f"Taux de réussite: {(results['successful_syncs']/results['total_groups']*100):.1f}%")
        
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()