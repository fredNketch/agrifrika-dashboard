"""
Service Google Sheets avec permissions d'écriture
Extension du service existant pour l'automatisation Basecamp → Google Sheets
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleSheetsWriteService:
    """Service Google Sheets avec permissions d'écriture pour automatisation"""
    
    def __init__(self):
        self.service = None
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """Initialise la connexion à l'API Google Sheets avec permissions d'écriture"""
        try:
            credentials = Credentials.from_service_account_file(
                settings.sheets_credentials_full_path,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',  # Lecture + écriture
                    'https://www.googleapis.com/auth/drive.file'     # Accès aux fichiers créés par l'app
                ]
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets Write API initialisée")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets Write API: {e}")
    
    def clear_range(self, sheet_id: str, range_name: str) -> bool:
        """Vide un range de cellules"""
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            logger.info(f"✅ Range '{range_name}' vidé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du vidage du range '{range_name}': {e}")
            return False
    
    def write_values(self, sheet_id: str, range_name: str, values: List[List[str]], 
                    value_input_option: str = 'RAW') -> bool:
        """Écrit des valeurs dans un range"""
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            logger.info(f"✅ Range '{range_name}': {len(values)} lignes écrites ({updated_cells} cellules mises à jour)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'écriture dans '{range_name}': {e}")
            return False
    
    def batch_update_values(self, sheet_id: str, updates: List[Dict[str, Any]]) -> bool:
        """Effectue plusieurs mises à jour en une seule requête"""
        try:
            body = {
                'valueInputOption': 'RAW',
                'data': updates
            }
            
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=sheet_id,
                body=body
            ).execute()
            
            total_updated_cells = result.get('totalUpdatedCells', 0)
            logger.info(f"✅ Batch update: {len(updates)} ranges mis à jour ({total_updated_cells} cellules)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du batch update: {e}")
            return False
    
    def create_headers(self, sheet_id: str, sheet_name: str, headers: List[str]) -> bool:
        """Crée les headers dans un sheet"""
        try:
            range_name = f"{sheet_name}!A1:{chr(65 + len(headers) - 1)}1"  # A1:E1 pour 5 colonnes
            
            return self.write_values(sheet_id, range_name, [headers])
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création des headers pour '{sheet_name}': {e}")
            return False
    
    def get_sheet_properties(self, sheet_id: str) -> Optional[Dict]:
        """Récupère les propriétés du spreadsheet"""
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=sheet_id,
                fields="sheets.properties"
            ).execute()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des propriétés du sheet: {e}")
            return None
    
    def check_sheet_exists(self, sheet_id: str, sheet_name: str) -> bool:
        """Vérifie si un sheet existe dans le spreadsheet"""
        try:
            properties = self.get_sheet_properties(sheet_id)
            if not properties:
                return False
            
            sheet_names = [sheet['properties']['title'] for sheet in properties.get('sheets', [])]
            exists = sheet_name in sheet_names
            
            logger.info(f"Sheet '{sheet_name}' {'existe' if exists else 'n\'existe pas'}")
            return exists
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification du sheet '{sheet_name}': {e}")
            return False
    
    def list_all_sheets(self, sheet_id: str) -> List[str]:
        """Liste tous les sheets du spreadsheet"""
        try:
            properties = self.get_sheet_properties(sheet_id)
            if not properties:
                return []
            
            sheet_names = [sheet['properties']['title'] for sheet in properties.get('sheets', [])]
            logger.info(f"Sheets disponibles: {sheet_names}")
            return sheet_names
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de la liste des sheets: {e}")
            return []
    
    def create_sheet(self, sheet_id: str, sheet_name: str) -> bool:
        """Crée un nouvel onglet dans le spreadsheet"""
        try:
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
            
            body = {
                'requests': requests
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body=body
            ).execute()
            
            logger.info(f"✅ Onglet '{sheet_name}' créé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de l'onglet '{sheet_name}': {e}")
            return False
    
    def create_sheet_with_headers(self, sheet_id: str, sheet_name: str, headers: List[str]) -> bool:
        """Crée un onglet avec headers en une seule opération"""
        try:
            # Créer l'onglet
            if not self.create_sheet(sheet_id, sheet_name):
                return False
            
            # Ajouter les headers
            return self.create_headers(sheet_id, sheet_name, headers)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de l'onglet avec headers '{sheet_name}': {e}")
            return False
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion d'écriture"""
        try:
            if not self.service:
                return False
            
            # Test simple de lecture pour vérifier les permissions
            result = self.service.spreadsheets().get(
                spreadsheetId=settings.TODOS_SHEET_ID,
                fields="properties.title"
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Google Sheets Write health check failed: {e}")
            return False