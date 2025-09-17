"""
Service Public Engagement pour AGRIFRIKA Dashboard
Version avec logique mensuelle indépendante (pas de cumulation)
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.core.config import settings
from app.services.kpi_calculator import PublicEngagementCalculator

logger = logging.getLogger(__name__)

class PublicEngagementService:
    """Service pour récupérer les données d'engagement public avec tendances mensuelles indépendantes"""
    
    def __init__(self):
        self.service = None
        self.calculator = PublicEngagementCalculator()
        self._initialize_api()
    
    def _initialize_api(self) -> None:
        """Initialise la connexion à l'API Google Sheets"""
        try:
            credentials = Credentials.from_service_account_file(
                settings.sheets_credentials_full_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Google Sheets API initialisée pour Public Engagement (nouvelle version)")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Google Sheets API: {e}")
    
    def _safe_int(self, value: str) -> int:
        """Convertit une valeur en entier de manière sécurisée"""
        if not value or value == "" or value == "-":
            return 0
        try:
            cleaned_value = str(value).replace(" ", "").replace(",", "")
            return int(float(cleaned_value))
        except (ValueError, TypeError):
            logger.warning(f"Impossible de convertir '{value}' en entier")
            return 0
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse une date DD/MM/YYYY en YYYY-MM-DD pour le tri"""
        try:
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return None
    
    def _calculate_engagement_score(self, data: Dict[str, int]) -> int:
        """Calcule le score d'engagement pour une période donnée"""
        # Logique de calcul basée sur les métriques d'engagement
        score = 0
        
        # Vues (poids 0.1)
        score += data.get('vues', 0) * 0.1
        
        # Likes et réactions (poids 2)
        score += data.get('likes_reactions', 0) * 2
        
        # Partages (poids 3)
        score += data.get('partages', 0) * 3
        
        # Commentaires (poids 2)
        score += data.get('commentaires', 0) * 2
        
        # Nouveaux abonnés (poids 5)
        score += data.get('nouveaux_abonnes', 0) * 5
        
        # Téléchargements app (poids 10)
        score += data.get('telechargement_app', 0) * 10
        
        # Visites uniques site (poids 0.1)
        score += data.get('visites_uniques_site', 0) * 0.1
        
        # Mentions médias (poids 8)
        score += data.get('mention_medias', 0) * 8
        
        # Newsletter (poids 3)
        score += data.get('newsletter', 0) * 3
        
        # Événements 50+ (poids 15)
        score += data.get('evenement_50plus_participants', 0) * 15
        
        # Apparitions recherches (poids 2)
        score += data.get('apparition_recherches', 0) * 2
        
        # Impressions LinkedIn (poids 0.5)
        score += data.get('impressions_linkedin', 0) * 0.5
        
        return int(score)
    
    async def get_all_engagement_entries(self) -> List[Dict[str, Any]]:
        """Récupère TOUTES les données d'engagement historiques"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return []
        
        try:
            # Récupération de toutes les données d'engagement
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PUBLIC_ENGAGEMENT_SHEET_ID,
                range=settings.ENGAGEMENT_METRICS_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("Aucune donnée trouvée dans le sheet d'engagement")
                return []
            
            # Traiter toutes les lignes (pas seulement celles avec Status="Latest")
            entries = []
            for row in values:
                if len(row) >= 13:  # Vérifier qu'on a au moins les colonnes de base
                    # Mapping des colonnes selon la structure du sheet
                    entry_data = {
                        "date": row[0] if len(row) > 0 else "",
                        "semaine": row[1] if len(row) > 1 else "",
                        "vues": self._safe_int(row[2]) if len(row) > 2 else 0,
                        "likes_reactions": self._safe_int(row[3]) if len(row) > 3 else 0,
                        "partages": self._safe_int(row[4]) if len(row) > 4 else 0,
                        "commentaires": self._safe_int(row[5]) if len(row) > 5 else 0,
                        "nouveaux_abonnes": self._safe_int(row[6]) if len(row) > 6 else 0,
                        "telechargement_app": self._safe_int(row[7]) if len(row) > 7 else 0,
                        "visites_uniques_site": self._safe_int(row[8]) if len(row) > 8 else 0,
                        "mention_medias": self._safe_int(row[9]) if len(row) > 9 else 0,
                        "newsletter": self._safe_int(row[10]) if len(row) > 10 else 0,
                        "evenement_50plus_participants": self._safe_int(row[11]) if len(row) > 11 else 0,
                        "apparition_recherches": self._safe_int(row[12]) if len(row) > 12 else 0,
                        "impressions_linkedin": self._safe_int(row[13]) if len(row) > 13 else 0,
                        "status": row[14] if len(row) > 14 else ""
                    }
                    
                    # Calculer le score pour cette période
                    score = self._calculate_engagement_score(entry_data)
                    entry_data["score"] = score
                    
                    entries.append(entry_data)
            
            # Trier par date chronologique
            entries.sort(key=lambda x: self._parse_date(x["date"]) or "0000-00-00")
            
            logger.info(f"✅ {len(entries)} entrées d'engagement récupérées")
            return entries
            
        except Exception as e:
            logger.error(f"Erreur récupération données d'engagement: {e}")
            return []
    
    async def get_engagement_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les données d'engagement actuelles (dernière entrée)"""
        entries = await self.get_all_engagement_entries()
        
        if not entries:
            return None
        
        # Retourner la dernière entrée (la plus récente)
        latest_entry = entries[-1]
        
        logger.info(f"✅ Données d'engagement actuelles récupérées: {latest_entry['date']}")
        return latest_entry
    
    async def get_monthly_trends(self) -> List[Dict[str, Any]]:
        """Calcule les tendances mensuelles indépendantes basées sur les points du calculateur.

        - Agrège toutes les métriques par mois (DD/MM/YYYY → MM/YYYY)
        - Utilise PublicEngagementCalculator pour calculer les points mensuels cohérents
        - Retourne pour chaque mois:
          • month: libellé court (Jan, Fév, ...)
          • score: total_points_obtenus du mois (valeur utilisée par le graphique)
          • percentage: score en % du mois
          • total_score: alias des points (compatibilité composant)
          • autres totaux utiles pour le tooltip
        """
        entries = await self.get_all_engagement_entries()
        
        if not entries:
            return []
        
        # Grouper et sommer les métriques par mois
        monthly_totals: Dict[str, Dict[str, Any]] = {}
        
        for entry in entries:
            date_str = entry.get("date", "")
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 3:
                    month_key = f"{parts[1]}/{parts[2]}"  # MM/YYYY
                    
                    if month_key not in monthly_totals:
                        monthly_totals[month_key] = {
                            "entries": 0,
                            "vues": 0,
                            "likes_reactions": 0,
                            "partages": 0,
                            "commentaires": 0,
                            "nouveaux_abonnes": 0,
                            "telechargement_app": 0,
                            "visites_uniques_site": 0,
                            "mention_medias": 0,
                            "newsletter": 0,
                            "evenement_50plus_participants": 0,
                            "apparition_recherches": 0,
                            "impressions_linkedin": 0,
                        }

                    agg = monthly_totals[month_key]
                    agg["entries"] += 1
                    agg["vues"] += entry.get("vues", 0)
                    agg["likes_reactions"] += entry.get("likes_reactions", 0)
                    agg["partages"] += entry.get("partages", 0)
                    agg["commentaires"] += entry.get("commentaires", 0)
                    agg["nouveaux_abonnes"] += entry.get("nouveaux_abonnes", 0)
                    agg["telechargement_app"] += entry.get("telechargement_app", 0)
                    agg["visites_uniques_site"] += entry.get("visites_uniques_site", 0)
                    agg["mention_medias"] += entry.get("mention_medias", 0)
                    agg["newsletter"] += entry.get("newsletter", 0)
                    agg["evenement_50plus_participants"] += entry.get("evenement_50plus_participants", 0)
                    agg["apparition_recherches"] += entry.get("apparition_recherches", 0)
                    agg["impressions_linkedin"] += entry.get("impressions_linkedin", 0)

        # Construire le tableau de tendances en utilisant le calculateur officiel
            month_names = {
                "01": "Jan", "02": "Fév", "03": "Mar", "04": "Avr", 
                "05": "Mai", "06": "Jun", "07": "Jul", "08": "Aoû", 
                "09": "Sep", "10": "Oct", "11": "Nov", "12": "Déc"
            }

        trends: List[Dict[str, Any]] = []
        for month_key, totals in monthly_totals.items():
            # Calcul cohérent via le calculateur centralisé
            calc = self.calculator.calculate_score(totals)
            total_points = calc.get("total_points_obtenus", 0)
            percentage = calc.get("score", 0)

            month_num = month_key.split("/")[0]
            month_name = month_names.get(month_num, f"M{month_num}")
            
            trends.append({
                "month": month_name,
                "score": int(total_points),            # utilisé par le graphique (points)
                "percentage": percentage,               # % pour info complémentaire
                "total_score": int(total_points),       # compatibilité actuelle du composant
                "entries_count": totals["entries"],
                "total_vues": totals["vues"],
                "total_likes": totals["likes_reactions"],
                "total_partages": totals["partages"],
                "total_commentaires": totals["commentaires"],
                "total_abonnes": totals["nouveaux_abonnes"],
                "month_key": month_key
            })
        
        # Trier par mois chronologique et ne garder que les 3 derniers
        trends.sort(key=lambda x: x["month_key"])
        trends = trends[-3:] if len(trends) >= 3 else trends
        
        logger.info(f"✅ {len(trends)} tendances mensuelles calculées (points cohérents)")
        return trends
    
    async def get_latest_video(self) -> Optional[Dict[str, Any]]:
        """Récupère les données de la dernière vidéo postée"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Récupération des données vidéos
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PUBLIC_ENGAGEMENT_SHEET_ID,
                range=settings.VIDEOS_RANGE
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("Aucune donnée vidéo trouvée")
                return None
            
            # Chercher la vidéo avec le status "latest" ou prendre la première
            latest_video = None
            for row in values:
                if len(row) >= 9:  # Vérifier qu'on a toutes les colonnes
                    status = row[8] if len(row) > 8 else ""
                    if status.lower() == "latest":
                        latest_video = row
                        break
            
            # Si pas de "latest" trouvé, prendre la première ligne
            if not latest_video and values:
                latest_video = values[0]
            
            if not latest_video or len(latest_video) < 8:
                logger.warning("Données vidéo incomplètes")
                return None
            
            # Mapping des colonnes vidéo
            video_data = {
                "date_publication": latest_video[0] if len(latest_video) > 0 else "",
                "plateforme": latest_video[1] if len(latest_video) > 1 else "",
                "url": latest_video[2] if len(latest_video) > 2 else "",
                "titre": latest_video[3] if len(latest_video) > 3 else "",
                "vues": self._safe_int(latest_video[4]) if len(latest_video) > 4 else 0,
                "likes": self._safe_int(latest_video[5]) if len(latest_video) > 5 else 0,
                "partages": self._safe_int(latest_video[6]) if len(latest_video) > 6 else 0,
                "commentaires": self._safe_int(latest_video[7]) if len(latest_video) > 7 else 0,
                "status": latest_video[8] if len(latest_video) > 8 else "active"
            }
            
            logger.info(f"✅ Données vidéo récupérées: {video_data}")
            return video_data
            
        except Exception as e:
            logger.error(f"Erreur récupération données vidéo: {e}")
            return None
    
    async def get_top_content(self) -> Optional[list]:
        """Récupère les 2 contenus avec le plus de vues depuis le Google Sheet"""
        if not self.service:
            logger.warning("Google Sheets API non initialisée")
            return None
        
        try:
            # Récupération des données de la feuille top-content
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PUBLIC_ENGAGEMENT_SHEET_ID,
                range='top-content!A:D'  # Colonnes: Plateforme, Titre, URL, Vues
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:  # Pas de données ou seulement l'en-tête
                logger.warning("Aucune donnée trouvée dans la feuille top-content")
                return []
            
            # Ignorer l'en-tête et traiter les données
            data_rows = values[1:] if values else []
            
            # Convertir en objets avec tri par vues
            content_items = []
            for row in data_rows:
                if len(row) >= 4:  # Vérifier qu'on a toutes les colonnes
                    try:
                        vues = self._safe_int(row[3])  # Colonne D: Vues
                        if vues > 0:  # Seulement les contenus avec des vues
                            content_items.append({
                                "platform": row[0] if len(row) > 0 else "",  # Colonne A: Plateforme
                                "title": row[1] if len(row) > 1 else "",     # Colonne B: Titre
                                "url": row[2] if len(row) > 2 else "",       # Colonne C: URL
                                "vues": vues
                            })
                    except Exception as e:
                        logger.warning(f"Erreur traitement ligne top-content: {e}")
                        continue
            
            # Trier par nombre de vues (décroissant) et prendre les 2 premiers
            content_items.sort(key=lambda x: x["vues"], reverse=True)
            top_2_content = content_items[:2]
            
            logger.info(f"✅ Top 2 contenus récupérés: {top_2_content}")
            return top_2_content
            
        except Exception as e:
            logger.error(f"Erreur récupération top content: {e}")
            return []

    async def calculate_engagement_score(self) -> Optional[Dict[str, Any]]:
        """Calcule le score d'engagement basé sur les données Google Sheets"""
        engagement_data = await self.get_engagement_data()
        top_content = await self.get_top_content()
        monthly_trend = await self.get_monthly_trends()
        
        if not engagement_data:
            return None
        
        # Utiliser le calculateur pour obtenir le score
        score_result = self.calculator.calculate_score(engagement_data)
        
        # Ajouter les données réelles
        score_result["top_content"] = top_content or []
        score_result["monthly_trend"] = monthly_trend or []
        score_result["last_updated"] = datetime.now().isoformat()
        score_result["raw_data"] = engagement_data
        
        return score_result
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Google Sheets pour Public Engagement"""
        try:
            if not self.service:
                return False
            
            # Test simple de lecture
            result = self.service.spreadsheets().values().get(
                spreadsheetId=settings.PUBLIC_ENGAGEMENT_SHEET_ID,
                range='A1:B2'
            ).execute()
            
            return 'values' in result
            
        except Exception as e:
            logger.error(f"Public Engagement Google Sheets health check failed: {e}")
            return False
