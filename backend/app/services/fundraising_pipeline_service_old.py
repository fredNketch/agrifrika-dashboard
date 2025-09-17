"""
Service Fundraising Pipeline pour AGRIFRIKA Dashboard
Récupération des données de fundraising depuis Google Sheets
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
from app.services.kpi_calculator import FundraisingPipelineCalculator

logger = logging.getLogger(__name__)

class FundraisingPipelineService:
    """Service pour récupérer les données de fundraising depuis Google Sheets"""
    
    def __init__(self):
        self.service = None
        self.calculator = FundraisingPipelineCalculator()
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """Initialise la connexion à l'API Google Sheets"""
        try:
            credentials = Credentials.from_service_account_file(
                settings.sheets_credentials_full_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets API initialisée pour Fundraising Pipeline")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets API: {e}")
    
    async def get_fundraising_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les données de fundraising depuis Google Sheets (logique cumulative)"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Récupération de toutes les données de fundraising
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.FUNDRAISING_PIPELINE_SHEET_ID,
                range=settings.FUNDRAISING_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                logger.warning("Aucune donnée trouvée dans le sheet de fundraising")
                return None
            
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
                return None
            
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
    
    async def calculate_fundraising_score(self) -> Optional[Dict[str, Any]]:
        """Calcule le score de fundraising basé sur les données Google Sheets"""
        fundraising_data = await self.get_fundraising_data()
        
        if not fundraising_data:
            return None
        
        # Restructurer les données pour le calculateur
        structured_data = {
            "concours": {
                "participation": fundraising_data.get("participation_simple", 0),
                "participation_plus_100k": fundraising_data.get("participation_plus_100k", 0),
                "finaliste": fundraising_data.get("finaliste_simple", 0),
                "finaliste_plus_100k": fundraising_data.get("finaliste_plus_100k", 0),
                "vainqueur": fundraising_data.get("vainqueur", 0)
            },
            "subventions": {
                "demande": fundraising_data.get("demande_simple", 0),
                "demande_plus_100k": fundraising_data.get("demande_plus_100k", 0),
                "entretien": fundraising_data.get("entretien_presentation", 0),
                "acceptation": fundraising_data.get("acceptation", 0)
            },
            "investisseurs": {
                "contact": fundraising_data.get("contact_initial", 0),
                "reponse_positive": fundraising_data.get("reponse_positive", 0),
                "meeting": fundraising_data.get("meeting_programme", 0),
                "due_diligence": fundraising_data.get("due_diligence", 0),
                "engagement_ferme_10k": fundraising_data.get("engagement_ferme", 0)
            }
        }
        
        # Calculer le score avec l'objectif total correct selon PDF (4 547 points)
        concours_points = self._calculate_concours_points_correct(structured_data["concours"])
        subventions_points = self._calculate_subventions_points_correct(structured_data["subventions"]) 
        investisseurs_points = self._calculate_investisseurs_points_correct(structured_data["investisseurs"])
        
        total_points_obtenus = concours_points + subventions_points + investisseurs_points
        
        objectif_total = 4547  # Selon TABLE 3 du PDF
        score_pct = (total_points_obtenus / objectif_total) * 100
        
        score_result = {
            "score": round(score_pct, 1),
            "total_points_obtenus": total_points_obtenus,
            "objectif_total": objectif_total,
            "status": self._get_status_from_score(score_pct)
        }
        
        # Ajouter les données brutes pour référence
        score_result["raw_data"] = fundraising_data
        
        return score_result
    
    async def get_fundraising_trends(self) -> List[Dict[str, Any]]:
        """Récupère les vraies tendances de fundraising avec pente basée sur l'activité mensuelle"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return []
        
        try:
            # Récupération de toutes les données de fundraising
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.FUNDRAISING_PIPELINE_SHEET_ID,
                range=settings.FUNDRAISING_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                logger.warning("Aucune donnée trouvée dans le sheet de fundraising")
                return []
            
            # Récupérer toutes les lignes de données (ignorer la ligne header)
            data_entries = []
            for i, row in enumerate(values[1:], start=2):
                if len(row) >= 16:
                    entry = {
                        "row_number": i,
                        "date": self._safe_str(row[0]) if len(row) > 0 else "",
                        "week": self._safe_str(row[1]) if len(row) > 1 else "",
                        "data": {
                            "participation_simple": self._safe_int(row[2]) if len(row) > 2 else 0,
                            "participation_plus_100k": self._safe_int(row[3]) if len(row) > 3 else 0,
                            "finaliste_simple": self._safe_int(row[4]) if len(row) > 4 else 0,
                            "finaliste_plus_100k": self._safe_int(row[5]) if len(row) > 5 else 0,
                            "vainqueur": self._safe_int(row[6]) if len(row) > 6 else 0,
                            "demande_simple": self._safe_int(row[7]) if len(row) > 7 else 0,
                            "demande_plus_100k": self._safe_int(row[8]) if len(row) > 8 else 0,
                            "entretien_presentation": self._safe_int(row[9]) if len(row) > 9 else 0,
                            "acceptation": self._safe_int(row[10]) if len(row) > 10 else 0,
                            "contact_initial": self._safe_int(row[11]) if len(row) > 11 else 0,
                            "reponse_positive": self._safe_int(row[12]) if len(row) > 12 else 0,
                            "meeting_programme": self._safe_int(row[13]) if len(row) > 13 else 0,
                            "due_diligence": self._safe_int(row[14]) if len(row) > 14 else 0,
                            "engagement_ferme": self._safe_int(row[15]) if len(row) > 15 else 0
                        }
                    }
                    data_entries.append(entry)
            
            if not data_entries:
                logger.warning("Aucune entrée de données valide trouvée")
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
            
            # Calculer les tendances avec pente basée sur l'activité mensuelle
            trend_entries = []
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
            
            for i, entry in enumerate(sorted_entries):
                # Calculer l'activité de ce mois (données brutes de cette période)
                monthly_activity_points = self._calculate_fundraising_points(entry["data"])
                
                # Ajouter les données de cette période au cumul
                for key, value in entry["data"].items():
                    cumulative_data[key] += value
                
                # Calculer le cumul total
                cumulative_points = self._calculate_fundraising_points(cumulative_data)
                cumulative_score_percentage = (cumulative_points / 4547) * 100
                
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
                    "score": round(cumulative_score_percentage, 1),
                    "total_points": cumulative_points,  # Hauteur finale = cumul
                    "monthly_activity": monthly_activity_points,  # Pente = activité du mois
                    "date": entry["date"],
                    "week": entry["week"]
                }
                trend_entries.append(trend_entry)
            
            logger.info(f"✅ Tendances de fundraising générées: {len(trend_entries)} points avec pente basée sur l'activité mensuelle")
            return trend_entries
            
        except Exception as e:
            logger.error(f"Erreur génération tendances fundraising: {e}")
            return []
    
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
    
    async def get_fundraising_categories(self) -> Optional[Dict[str, Any]]:
        """Récupère les catégories de fundraising avec calculs détaillés"""
        fundraising_data = await self.get_fundraising_data()
        
        if not fundraising_data:
            return None
        
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
        
        return {
            "concours": concours_points,
            "subventions": subventions_points,
            "investisseurs": investisseurs_points,
            "activités": 0,  # Placeholder
            "total": concours_points + subventions_points + investisseurs_points
        }
    
    async def get_detailed_breakdown(self) -> Optional[Dict[str, Any]]:
        """Récupère une analyse détaillée par catégorie"""
        fundraising_data = await self.get_fundraising_data()
        
        if not fundraising_data:
            return None
        
        # Calcul détaillé par catégorie selon ALGORITHMES_CALCUL.md (× notation)
        concours_details = {
            "participation_simple": {
                "valeur": fundraising_data.get("participation_simple", 0),
                "points_unitaires": 1,
                "points_obtenus": fundraising_data.get("participation_simple", 0) * 1  # valeur × 1
            },
            "participation_plus_100k": {
                "valeur": fundraising_data.get("participation_plus_100k", 0),
                "points_unitaires": 2,  # 1 × 1 + 1 bonus = 2
                "points_obtenus": fundraising_data.get("participation_plus_100k", 0) * 2  # valeur × 2
            },
            "finaliste_simple": {
                "valeur": fundraising_data.get("finaliste_simple", 0),
                "points_unitaires": 2,
                "points_obtenus": fundraising_data.get("finaliste_simple", 0) * 2  # valeur × 2
            },
            "finaliste_plus_100k": {
                "valeur": fundraising_data.get("finaliste_plus_100k", 0),
                "points_unitaires": 4,  # 2 × 1 + 2 bonus = 4
                "points_obtenus": fundraising_data.get("finaliste_plus_100k", 0) * 4  # valeur × 4
            },
            "vainqueur": {
                "valeur": fundraising_data.get("vainqueur", 0),
                "points_unitaires": 3,  # Valeur estimée basée sur l'analyse
                "points_obtenus": fundraising_data.get("vainqueur", 0) * 3  # valeur × 3
            }
        }
        
        subventions_details = {
            "demande_simple": {
                "valeur": fundraising_data.get("demande_simple", 0),
                "points_unitaires": 1,
                "points_obtenus": fundraising_data.get("demande_simple", 0) * 1  # valeur × 1
            },
            "demande_plus_100k": {
                "valeur": fundraising_data.get("demande_plus_100k", 0),
                "points_unitaires": 2,  # 1 × 1 + 1 bonus = 2
                "points_obtenus": fundraising_data.get("demande_plus_100k", 0) * 2  # valeur × 2
            },
            "entretien": {
                "valeur": fundraising_data.get("entretien_presentation", 0),
                "points_unitaires": 2,
                "points_obtenus": fundraising_data.get("entretien_presentation", 0) * 2  # valeur × 2
            },
            "acceptation": {
                "valeur": fundraising_data.get("acceptation", 0),
                "points_unitaires": 3,
                "points_obtenus": fundraising_data.get("acceptation", 0) * 3  # valeur × 3
            }
        }
        
        investisseurs_details = {
            "contact": {
                "valeur": fundraising_data.get("contact_initial", 0),
                "points_unitaires": 1,
                "points_obtenus": fundraising_data.get("contact_initial", 0) * 1  # valeur × 1
            },
            "reponse_positive": {
                "valeur": fundraising_data.get("reponse_positive", 0),
                "points_unitaires": 2,
                "points_obtenus": fundraising_data.get("reponse_positive", 0) * 2  # valeur × 2
            },
            "meeting": {
                "valeur": fundraising_data.get("meeting_programme", 0),
                "points_unitaires": 2,
                "points_obtenus": fundraising_data.get("meeting_programme", 0) * 2  # valeur × 2
            },
            "due_diligence": {
                "valeur": fundraising_data.get("due_diligence", 0),
                "points_unitaires": 2,
                "points_obtenus": fundraising_data.get("due_diligence", 0) * 2  # valeur × 2
            },
            "engagement_ferme": {
                "valeur": fundraising_data.get("engagement_ferme", 0),
                "points_unitaires": 3,  # engagement_ferme_10k selon spec
                "points_obtenus": fundraising_data.get("engagement_ferme", 0) * 3  # valeur × 3
            }
        }
        
        # Calcul des totaux par catégorie
        concours_total = sum([details["points_obtenus"] for details in concours_details.values()])
        subventions_total = sum([details["points_obtenus"] for details in subventions_details.values()])
        investisseurs_total = sum([details["points_obtenus"] for details in investisseurs_details.values()])
        
        return {
            "date": fundraising_data.get("date", ""),
            "semaine": fundraising_data.get("semaine", ""),
            "concours": {
                "details": concours_details,
                "total_points": concours_total
            },
            "subventions": {
                "details": subventions_details,
                "total_points": subventions_total
            },
            "investisseurs": {
                "details": investisseurs_details,
                "total_points": investisseurs_total
            },
            "score_total": concours_total + subventions_total + investisseurs_total,
            "timestamp": datetime.now().isoformat()
        }
    
    def _safe_int(self, value: str) -> int:
        """Convertit une valeur en entier de manière sécurisée"""
        if not value or value == "" or value == "-":
            return 0
        
        try:
            # Nettoyer la valeur (supprimer les espaces, virgules, etc.)
            cleaned_value = str(value).replace(" ", "").replace(",", "")
            return int(float(cleaned_value))
        except (ValueError, TypeError):
            logger.warning(f"Impossible de convertir '{value}' en entier")
            return 0
    
    def _safe_str(self, value: str) -> str:
        """Convertit une valeur en string de manière sécurisée"""
        return str(value).strip() if value else ""
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Google Sheets pour Fundraising"""
        try:
            if not self.service:
                return False
            
            # Test simple de lecture
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.FUNDRAISING_PIPELINE_SHEET_ID,
                range='A1:B2'
            ).execute()
            
            return 'values' in result
            
        except Exception as e:
            logger.error(f"Fundraising Pipeline Google Sheets health check failed: {e}")
            return False
    
    def _calculate_concours_details(self, concours_data):
        """Calcule les détails des concours"""
        return {
            "participation": {
                "valeur": concours_data.get("participation", 0),
                "points_unitaires": 1,
                "points_obtenus": concours_data.get("participation", 0) * 1
            },
            "participation_plus_100k": {
                "valeur": concours_data.get("participation_plus_100k", 0),
                "points_unitaires": 2,
                "points_obtenus": concours_data.get("participation_plus_100k", 0) * 2
            },
            "finaliste": {
                "valeur": concours_data.get("finaliste", 0),
                "points_unitaires": 2,
                "points_obtenus": concours_data.get("finaliste", 0) * 2
            },
            "finaliste_plus_100k": {
                "valeur": concours_data.get("finaliste_plus_100k", 0),
                "points_unitaires": 4,
                "points_obtenus": concours_data.get("finaliste_plus_100k", 0) * 4
            }
        }
    
    def _calculate_subventions_details(self, subventions_data):
        """Calcule les détails des subventions"""
        return {
            "demande": {
                "valeur": subventions_data.get("demande", 0),
                "points_unitaires": 1,
                "points_obtenus": subventions_data.get("demande", 0) * 1
            },
            "demande_plus_100k": {
                "valeur": subventions_data.get("demande_plus_100k", 0),
                "points_unitaires": 2,
                "points_obtenus": subventions_data.get("demande_plus_100k", 0) * 2
            },
            "entretien": {
                "valeur": subventions_data.get("entretien", 0),
                "points_unitaires": 2,
                "points_obtenus": subventions_data.get("entretien", 0) * 2
            },
            "acceptation": {
                "valeur": subventions_data.get("acceptation", 0),
                "points_unitaires": 3,
                "points_obtenus": subventions_data.get("acceptation", 0) * 3
            }
        }
    
    def _calculate_investisseurs_details(self, investisseurs_data):
        """Calcule les détails des investisseurs"""
        return {
            "contact": {
                "valeur": investisseurs_data.get("contact", 0),
                "points_unitaires": 1,
                "points_obtenus": investisseurs_data.get("contact", 0) * 1
            },
            "reponse_positive": {
                "valeur": investisseurs_data.get("reponse_positive", 0),
                "points_unitaires": 2,
                "points_obtenus": investisseurs_data.get("reponse_positive", 0) * 2
            },
            "meeting": {
                "valeur": investisseurs_data.get("meeting", 0),
                "points_unitaires": 2,
                "points_obtenus": investisseurs_data.get("meeting", 0) * 2
            },
            "due_diligence": {
                "valeur": investisseurs_data.get("due_diligence", 0),
                "points_unitaires": 2,
                "points_obtenus": investisseurs_data.get("due_diligence", 0) * 2
            },
            "engagement_ferme_10k": {
                "valeur": investisseurs_data.get("engagement_ferme_10k", 0),
                "points_unitaires": 3,
                "points_obtenus": investisseurs_data.get("engagement_ferme_10k", 0) * 3
            }
        }
    
    def _calculate_concours_points_correct(self, concours_data):
        """Calcule les points concours selon les formules PDF correctes"""
        points = 0
        
        # Participation simple: valeur × 1 point
        points += concours_data.get("participation", 0) * 1
        
        # Participation +100k: valeur × 2 points (1 base + 1 bonus)
        points += concours_data.get("participation_plus_100k", 0) * 2
        
        # Finaliste simple: valeur × 2 points
        points += concours_data.get("finaliste", 0) * 2
        
        # Finaliste +100k: valeur × 4 points (2 base + 2 bonus)
        points += concours_data.get("finaliste_plus_100k", 0) * 4
        
        # Vainqueur: valeur × 3 points (estimation basée sur l'analyse)
        points += concours_data.get("vainqueur", 0) * 3
        
        return points
    
    def _calculate_subventions_points_correct(self, subventions_data):
        """Calcule les points subventions selon les formules PDF correctes"""
        points = 0
        
        # Demande simple: valeur × 1 point
        points += subventions_data.get("demande", 0) * 1
        
        # Demande +100k: valeur × 2 points (1 base + 1 bonus)
        points += subventions_data.get("demande_plus_100k", 0) * 2
        
        # Entretien/Présentation: valeur × 2 points
        points += subventions_data.get("entretien", 0) * 2
        
        # Acceptation: valeur × 3 points
        points += subventions_data.get("acceptation", 0) * 3
        
        return points
    
    def _calculate_investisseurs_points_correct(self, investisseurs_data):
        """Calcule les points investisseurs selon les formules PDF correctes"""
        points = 0
        
        # Contact initial: valeur × 1 point
        points += investisseurs_data.get("contact", 0) * 1
        
        # Réponse positive: valeur × 2 points
        points += investisseurs_data.get("reponse_positive", 0) * 2
        
        # Meeting programmé: valeur × 2 points
        points += investisseurs_data.get("meeting", 0) * 2
        
        # Due diligence: valeur × 2 points
        points += investisseurs_data.get("due_diligence", 0) * 2
        
        # Engagement ferme 10k+: valeur × 3 points
        points += investisseurs_data.get("engagement_ferme_10k", 0) * 3
        
        # Chaque 10k supplémentaire: valeur × 1 point (si applicable)
        chaque_10k_supp = investisseurs_data.get("chaque_10k_supplementaire", 0)
        points += chaque_10k_supp * 1
        
        return points

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