"""
Service Fundraising Pipeline pour AGRIFRIKA Dashboard - VERSION COMPLÈTEMENT NOUVELLE
Récupération des données de fundraising depuis Google Sheets avec logique cumulative
Pente = Performance mensuelle, Hauteur = Cumul total
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class FundraisingPipelineServiceNew:
    """Service pour récupérer les données de fundraising depuis Google Sheets avec logique cumulative"""
    
    def __init__(self):
        self.service = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialise la connexion à l'API Google Sheets"""
        try:
            credentials = Credentials.from_service_account_file(
                "../config/credentials/google-sheets-new-credentials.json",
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets API initialisée pour Fundraising Pipeline")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets API: {e}")
    
    def _safe_int(self, value: str) -> int:
        """Convertit une valeur en entier de manière sécurisée"""
        if not value or value == "" or value == "-":
            return 0
        try:
            cleaned = str(value).replace(" ", "").replace(",", "").strip()
            return int(float(cleaned)) if cleaned else 0
        except (ValueError, TypeError):
            logger.warning(f"Impossible de convertir '{value}' en entier")
            return 0
    
    def _safe_str(self, value: str) -> str:
        """Convertit une valeur en string de manière sécurisée"""
        return str(value).strip() if value else ""
    
    def _calculate_fundraising_points(self, data: Dict[str, int]) -> int:
        """Calcule les points de fundraising selon le système de scoring"""
        points = 0
        
        # CONCOURS
        points += data.get("participation_simple", 0) * 1
        points += data.get("participation_plus_100k", 0) * 2
        points += data.get("finaliste_simple", 0) * 2
        points += data.get("finaliste_plus_100k", 0) * 4
        points += data.get("vainqueur", 0) * 3
        
        # SUBVENTIONS
        points += data.get("demande_simple", 0) * 1
        points += data.get("demande_plus_100k", 0) * 2
        points += data.get("entretien_presentation", 0) * 2
        points += data.get("acceptation", 0) * 3
        
        # INVESTISSEURS
        points += data.get("contact_initial", 0) * 1
        points += data.get("reponse_positive", 0) * 2
        points += data.get("meeting_programme", 0) * 2
        points += data.get("due_diligence", 0) * 2
        points += data.get("engagement_ferme", 0) * 3
        
        return points
    
    async def get_all_fundraising_entries(self) -> List[Dict[str, Any]]:
        """Récupère toutes les entrées de fundraising depuis Google Sheets"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return []
        
        try:
            # Récupération de toutes les données de fundraising
            result = self.service.spreadsheets().values().get(
                spreadsheetId='1c78RDASnzYM6SkOa2rvM25RFF1IDg2ESv46itE_78R0',
                range='fundraising!A1:Q50'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                logger.warning("Aucune donnée trouvée dans le sheet de fundraising")
                return []
            
            # Récupérer toutes les lignes de données (ignorer la ligne header)
            data_entries = []
            for i, row in enumerate(values[1:], start=2):
                if len(row) >= 16:  # Minimum pour avoir toutes les colonnes de données
                    entry = {
                        "row_number": i,
                        "date": self._safe_str(row[0]) if len(row) > 0 else "",
                        "week": self._safe_str(row[1]) if len(row) > 1 else "",
                        "data": {
                            # CONCOURS (C-G)
                            "participation_simple": self._safe_int(row[2]) if len(row) > 2 else 0,
                            "participation_plus_100k": self._safe_int(row[3]) if len(row) > 3 else 0,
                            "finaliste_simple": self._safe_int(row[4]) if len(row) > 4 else 0,
                            "finaliste_plus_100k": self._safe_int(row[5]) if len(row) > 5 else 0,
                            "vainqueur": self._safe_int(row[6]) if len(row) > 6 else 0,
                            
                            # SUBVENTIONS (H-K)
                            "demande_simple": self._safe_int(row[7]) if len(row) > 7 else 0,
                            "demande_plus_100k": self._safe_int(row[8]) if len(row) > 8 else 0,
                            "entretien_presentation": self._safe_int(row[9]) if len(row) > 9 else 0,
                            "acceptation": self._safe_int(row[10]) if len(row) > 10 else 0,
                            
                            # INVESTISSEURS (L-P)
                            "contact_initial": self._safe_int(row[11]) if len(row) > 11 else 0,
                            "reponse_positive": self._safe_int(row[12]) if len(row) > 12 else 0,
                            "meeting_programme": self._safe_int(row[13]) if len(row) > 13 else 0,
                            "due_diligence": self._safe_int(row[14]) if len(row) > 14 else 0,
                            "engagement_ferme": self._safe_int(row[15]) if len(row) > 15 else 0
                        }
                    }
                    data_entries.append(entry)
            
            if not data_entries:
                logger.warning("Aucune donnée valide trouvée dans le sheet de fundraising")
                return []
            
            # Trier par date chronologique
            def parse_date(date_str):
                try:
                    parts = date_str.split("/")
                    if len(parts) == 3:
                        day, month, year = parts
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except:
                    pass
                return date_str
            
            sorted_entries = sorted(data_entries, key=lambda x: parse_date(x["date"]))
            logger.info(f"✅ {len(sorted_entries)} entrées de fundraising récupérées et triées")
            return sorted_entries
            
        except Exception as e:
            logger.error(f"Erreur récupération entrées fundraising: {e}")
            return []
    
    async def get_fundraising_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les données de fundraising cumulées (pour l'affichage principal)"""
        try:
            # Récupérer toutes les entrées
            sorted_entries = await self.get_all_fundraising_entries()
            
            if not sorted_entries:
                return None
            
            # Calculer les cumuls
            cumulative_data = {
                "participation_simple": 0,
                "participation_plus_100k": 0,
                "finaliste_simple": 0,
                "finaliste_plus_100k": 0,
                "vainqueur": 0,
                "demande_simple": 0,
                "demande_plus_100k": 0,
                "entretien_presentation": 0,
                "acceptation": 0,
                "contact_initial": 0,
                "reponse_positive": 0,
                "meeting_programme": 0,
                "due_diligence": 0,
                "engagement_ferme": 0
            }
            
            # Ajouter toutes les données au cumul
            for entry in sorted_entries:
                for key, value in entry["data"].items():
                    cumulative_data[key] += value
            
            # Prendre la dernière entrée pour les métadonnées
            latest_entry = sorted_entries[-1]
            
            fundraising_data = {
                "date": latest_entry["date"],
                "semaine": latest_entry["week"],
                **cumulative_data  # Inclure toutes les données cumulées
            }
            
            logger.info(f"✅ Données de fundraising cumulées récupérées: {len(sorted_entries)} entrées")
            return fundraising_data
            
        except Exception as e:
            logger.error(f"Erreur récupération données de fundraising: {e}")
            return None
    
    async def get_fundraising_trends(self) -> List[Dict[str, Any]]:
        """Récupère les vraies tendances de fundraising avec logique de pente basée sur la performance mensuelle"""
        try:
            # Récupérer toutes les entrées
            sorted_entries = await self.get_all_fundraising_entries()
            
            if not sorted_entries:
                return []
            
            # Calculer les tendances avec logique de pente basée sur l'activité
            cumulative_entries = []
            cumulative_data = {
                "participation_simple": 0,
                "participation_plus_100k": 0,
                "finaliste_simple": 0,
                "finaliste_plus_100k": 0,
                "vainqueur": 0,
                "demande_simple": 0,
                "demande_plus_100k": 0,
                "entretien_presentation": 0,
                "acceptation": 0,
                "contact_initial": 0,
                "reponse_positive": 0,
                "meeting_programme": 0,
                "due_diligence": 0,
                "engagement_ferme": 0
            }
            
            previous_cumulative_points = 0
            
            for entry in sorted_entries:
                # Calculer l'activité réelle de cette période (données de cette période uniquement)
                activity_points = self._calculate_fundraising_points(entry["data"])
                
                # Ajouter les données de cette période au cumul global
                for key, value in entry["data"].items():
                    cumulative_data[key] += value
                
                # Calculer les points cumulés totaux
                cumulative_points = self._calculate_fundraising_points(cumulative_data)
                score_percentage = (cumulative_points / 4547) * 100
                
                # Extraire le mois de la date
                month = entry["date"].split("/")[1] if "/" in entry["date"] else ""
                month_names = {
                    "01": "Jan", "02": "Fév", "03": "Mar", "04": "Avr", 
                    "05": "Mai", "06": "Jun", "07": "Jul", "08": "Aoû", 
                    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Déc"
                }
                month_name = month_names.get(month, f"M{month}")
                
                trend_entry = {
                    "month": month_name,
                    "base_points": previous_cumulative_points,  # État du mois précédent (pour la pente)
                    "activity_points": activity_points,         # Activité réelle du mois (pente)
                    "total_points": cumulative_points,          # Hauteur finale (cumul total)
                    "score": round(score_percentage, 1),
                    "date": entry["date"],
                    "week": entry["week"]
                }
                cumulative_entries.append(trend_entry)
                
                # Mettre à jour pour la prochaine itération
                previous_cumulative_points = cumulative_points
            
            logger.info(f"✅ Tendances de fundraising générées: {len(cumulative_entries)} points")
            return cumulative_entries
            
        except Exception as e:
            logger.error(f"Erreur génération tendances fundraising: {e}")
            return []
    
    async def calculate_fundraising_score(self) -> Optional[Dict[str, Any]]:
        """Calcule le score de fundraising basé sur les données cumulées"""
        fundraising_data = await self.get_fundraising_data()
        
        if not fundraising_data:
            return None
        
        # Calculer le score avec l'objectif total correct selon PDF (4 547 points)
        total_points_obtenus = self._calculate_fundraising_points(fundraising_data)
        
        objectif_total = 4547  # Selon TABLE 3 du PDF
        score_pct = (total_points_obtenus / objectif_total) * 100
        
        # Calculer les points par catégorie avec les coefficients
        concours_points = (
            fundraising_data.get("participation_simple", 0) * 1 +
            fundraising_data.get("participation_plus_100k", 0) * 2 +
            fundraising_data.get("finaliste_simple", 0) * 2 +
            fundraising_data.get("finaliste_plus_100k", 0) * 4 +
            fundraising_data.get("vainqueur", 0) * 3
        )
        
        subventions_points = (
            fundraising_data.get("demande_simple", 0) * 1 +
            fundraising_data.get("demande_plus_100k", 0) * 2 +
            fundraising_data.get("entretien_presentation", 0) * 2 +
            fundraising_data.get("acceptation", 0) * 3
        )
        
        investisseurs_points = (
            fundraising_data.get("contact_initial", 0) * 1 +
            fundraising_data.get("reponse_positive", 0) * 2 +
            fundraising_data.get("meeting_programme", 0) * 2 +
            fundraising_data.get("due_diligence", 0) * 2 +
            fundraising_data.get("engagement_ferme", 0) * 3
        )
        
        score_result = {
            "score": round(score_pct, 1),
            "total_points_obtenus": total_points_obtenus,
            "objectif_total": objectif_total,
            "status": self._get_status_from_score(score_pct),
            "categories": {
                "concours": concours_points,
                "subventions": subventions_points,
                "investisseurs": investisseurs_points,
                "activités": 0  # Placeholder
            },
            "raw_data": fundraising_data,
            "timestamp": datetime.now().isoformat()
        }
        
        return score_result
    
    def _get_status_from_score(self, score_pct):
        """Détermine le statut basé sur le pourcentage de score"""
        if score_pct >= 80:
            return "EXCELLENT"
        elif score_pct >= 60:
            return "BON"
        elif score_pct >= 40:
            return "MOYEN"
        else:
            return "FAIBLE"
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Google Sheets pour Fundraising"""
        try:
            if not self.service:
                return False
            
            # Test simple de connexion
            result = self.service.spreadsheets().values().get(
                spreadsheetId='1c78RDASnzYM6SkOa2rvM25RFF1IDg2ESv46itE_78R0',
                range="fundraising!A1:A1"
            ).execute()
            
            return True
        except Exception as e:
            logger.error(f"Fundraising Pipeline Google Sheets health check failed: {e}")
            return False