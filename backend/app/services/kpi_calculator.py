"""
Services de calcul des KPI pour Dashboard 1 - AGRIFRIKA
Implémentation des algorithmes selon ALGORITHMES_CALCUL.md
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PublicEngagementCalculator:
    """Calculateur pour le score Public Engagement"""
    
    ENGAGEMENT_POINTS_SYSTEM = {
        "vues": {
            "points_par_unite": 1,
            "objectif_mensuel": 40000,
            "points_objectif": 40000
        },
        "likes_reactions": {
            "points_par_unite": 1,
            "objectif_mensuel": 5000,
            "points_objectif": 5000
        },
        "partages": {
            "points_par_unite": 3,
            "objectif_mensuel": 250,
            "points_objectif": 750
        },
        "commentaires": {
            "points_par_unite": 2,
            "objectif_mensuel": 250,
            "points_objectif": 500
        },
        "nouveaux_abonnes": {
            "points_par_unite": 3,
            "objectif_mensuel": 100,
            "points_objectif": 300
        },
        "telechargement_app": {
            "points_par_unite": 5,
            "objectif_mensuel": 100,
            "points_objectif": 500
        },
        "visites_uniques_site": {
            "points_par_unite": 2,
            "objectif_mensuel": 100,
            "points_objectif": 200
        },
        "mention_medias": {
            "points_par_unite": 3,
            "objectif_mensuel": 5,
            "points_objectif": 15
        },
        "newsletter": {
            "points_par_unite": 5,
            "objectif_mensuel": 50,
            "points_objectif": 250
        },
        "evenement_50plus_participants": {
            "points_par_unite": 100,
            "objectif_mensuel": 1,
            "points_objectif": 100
        },
        "apparition_recherches": {
            "points_par_unite": 1,
            "objectif_mensuel": 2000,
            "points_objectif": 2000
        },
        "impressions_linkedin": {
            "points_par_unite": 1,
            "objectif_mensuel": 15000,
            "points_objectif": 15000
        }
    }
    
    TOTAL_OBJECTIF_MENSUEL = 64615  # Somme de tous les points_objectif
    
    @classmethod
    def calculate_score(cls, donnees_mensuelles: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score d'engagement public basé sur les données collectées
        
        Args:
            donnees_mensuelles (dict): Données collectées pour le mois en cours
            
        Returns:
            dict: Score et détails du calcul
        """
        try:
            total_points_obtenus = 0
            details_par_source = {}
            
            for source, config in cls.ENGAGEMENT_POINTS_SYSTEM.items():
                valeur_obtenue = donnees_mensuelles.get(source, 0)
                points_obtenus = valeur_obtenue * config["points_par_unite"]
                total_points_obtenus += points_obtenus
                
                details_par_source[source] = {
                    "valeur_obtenue": valeur_obtenue,
                    "points_obtenus": points_obtenus,
                    "objectif": config["objectif_mensuel"],
                    "progression_objectif": (valeur_obtenue / config["objectif_mensuel"]) * 100 if config["objectif_mensuel"] > 0 else 0
                }
            
            score_final = (total_points_obtenus / cls.TOTAL_OBJECTIF_MENSUEL) * 100
            
            return {
                "score": round(score_final, 1),
                "total_points_obtenus": total_points_obtenus,
                "total_objectif": cls.TOTAL_OBJECTIF_MENSUEL,
                "details_par_source": details_par_source,
                "status": cls._get_engagement_status(score_final),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul Public Engagement: {e}")
            return {
                "score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _get_engagement_status(score: float) -> Dict[str, str]:
        """Détermine le statut basé sur le score d'engagement"""
        if score >= 80:
            return {"level": "excellent", "color": "green", "message": "Engagement exceptionnel"}
        elif score >= 60:
            return {"level": "bon", "color": "blue", "message": "Bon niveau d'engagement"}
        elif score >= 40:
            return {"level": "moyen", "color": "orange", "message": "Engagement à améliorer"}
        else:
            return {"level": "faible", "color": "red", "message": "Engagement insuffisant"}


class DefaultAliveCalculator:
    """Calculateur pour le Default Alive (Monitoring Financier)"""
    
    # Charges moyennes 2025 selon les spécifications
    CHARGES_MOYENNES_MENSUELLES = 3268  # $ par mois
    
    @classmethod
    def calculate_metrics(cls, cash_disponible: float, charges_mensuelles: Optional[float] = None, 
                         fonds_promis: float = 0, previous_value: Optional[float] = None) -> Dict[str, Any]:
        """
        Calcule les métriques Default Alive
        
        Args:
            cash_disponible (float): Cash disponible en $
            charges_mensuelles (float, optional): Charges mensuelles. Utilise la valeur par défaut si None
            fonds_promis (float): Fonds promis mais pas encore reçus
            previous_value (float, optional): Valeur précédente pour calcul de tendance
            
        Returns:
            dict: Métriques Default Alive
        """
        try:
            charges_moyennes = charges_mensuelles or cls.CHARGES_MOYENNES_MENSUELLES
            
            # Calcul Default Alive Pratique
            default_alive_pratique = cash_disponible / charges_moyennes if charges_moyennes > 0 else 0
            
            # Calcul Default Alive Théorique  
            default_alive_theorique = (cash_disponible + fonds_promis) / charges_moyennes if charges_moyennes > 0 else 0
            
            # Statut basé sur les mois restants
            status_pratique = cls._get_default_alive_status(default_alive_pratique)
            status_theorique = cls._get_default_alive_status(default_alive_theorique)
            
            # Calcul de tendance
            trend_percentage = 0
            if previous_value is not None:
                trend_percentage = cls._calculate_trend_percentage(default_alive_pratique, previous_value)
            
            return {
                "default_alive_pratique": {
                    "mois_restants": round(default_alive_pratique, 1),
                    "status": status_pratique,
                    "trend_percentage": round(trend_percentage, 1)
                },
                "default_alive_theorique": {
                    "mois_restants": round(default_alive_theorique, 1),
                    "status": status_theorique
                },
                "donnees_base": {
                    "cash_disponible": cash_disponible,
                    "charges_mensuelles": charges_moyennes,
                    "fonds_promis": fonds_promis
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul Default Alive: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _get_default_alive_status(mois_restants: float) -> Dict[str, str]:
        """Détermine le statut basé sur les mois restants"""
        if mois_restants > 6:
            return {"status": "sain", "color": "green", "message": "Situation financière stable"}
        elif mois_restants >= 3:
            return {"status": "attention", "color": "orange", "message": "Surveillance recommandée"}
        else:
            return {"status": "critique", "color": "red", "message": "Action urgente requise"}
    
    @staticmethod
    def _calculate_trend_percentage(current_value: float, previous_value: float) -> float:
        """Calcule le pourcentage de tendance"""
        if previous_value == 0:
            return 0
        return ((current_value - previous_value) / previous_value) * 100


class FundraisingPipelineCalculator:
    """Calculateur pour le Fundraising Pipeline Score"""
    
    FUNDRAISING_POINTS_SYSTEM = {
        "concours": {
            "participation": 1,
            "participation_plus_100k": 2,  # 1 + 1 bonus
            "finaliste": 2,
            "finaliste_plus_100k": 4       # 2 + 2 bonus
        },
        "subventions": {
            "demande": 1,
            "demande_plus_100k": 2,        # 1 + 1 bonus
            "entretien": 2,
            "acceptation": 3
        },
        "investisseurs": {
            "contact": 1,
            "reponse_positive": 2,
            "meeting": 2,
            "due_diligence": 2,
            "engagement_ferme_10k": 3,
            "chaque_10k_supplementaire": 1
        }
    }
    
    @classmethod
    def calculate_score(cls, donnees_fundraising: Dict[str, Dict[str, int]], 
                       objectif_total: int = 4547) -> Dict[str, Any]:
        """
        Calcule le score de fundraising pipeline
        
        Args:
            donnees_fundraising (dict): Données de fundraising par catégorie
            objectif_total (int): Objectif total de points (défaut: 100)
            
        Returns:
            dict: Score et détails du calcul
        """
        try:
            total_points_obtenus = 0
            details_par_categorie = {}
            
            for categorie, activites in donnees_fundraising.items():
                if categorie not in cls.FUNDRAISING_POINTS_SYSTEM:
                    continue
                    
                points_categorie = 0
                
                for activite, count in activites.items():
                    if activite in cls.FUNDRAISING_POINTS_SYSTEM[categorie]:
                        points = cls.FUNDRAISING_POINTS_SYSTEM[categorie][activite] * count
                        points_categorie += points
                
                details_par_categorie[categorie] = {
                    "points_obtenus": points_categorie,
                    "activites": activites
                }
                total_points_obtenus += points_categorie
            
            score_final = (total_points_obtenus / objectif_total) * 100 if objectif_total > 0 else 0
            
            return {
                "score": round(score_final, 1),
                "total_points_obtenus": total_points_obtenus,
                "objectif_total": objectif_total,
                "details_par_categorie": details_par_categorie,
                "prochaines_echeances": cls._get_upcoming_deadlines(donnees_fundraising),
                "status": cls._get_fundraising_status(score_final),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul Fundraising Pipeline: {e}")
            return {
                "score": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    def _get_fundraising_status(score: float) -> Dict[str, str]:
        """Détermine le statut basé sur le score de fundraising"""
        if score >= 80:
            return {"level": "excellent", "color": "green", "message": "Pipeline très actif"}
        elif score >= 60:
            return {"level": "bon", "color": "blue", "message": "Bon pipeline"}
        elif score >= 40:
            return {"level": "moyen", "color": "orange", "message": "Pipeline à améliorer"}
        else:
            return {"level": "faible", "color": "red", "message": "Pipeline insuffisant"}
    
    @staticmethod
    def _get_upcoming_deadlines(donnees_fundraising: Dict[str, Any]) -> list:
        """Extrait les prochaines échéances importantes"""
        # Placeholder - à implémenter selon la structure des données
        return []


class Dashboard1KPIService:
    """Service principal pour tous les KPI du Dashboard 1"""
    
    def __init__(self):
        self.public_engagement = PublicEngagementCalculator()
        self.default_alive = DefaultAliveCalculator()
        self.fundraising_pipeline = FundraisingPipelineCalculator()
    
    async def calculate_all_kpis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule tous les KPI du Dashboard 1
        
        Args:
            data (dict): Données collectées depuis les APIs
            
        Returns:
            dict: Tous les KPI calculés
        """
        try:
            # Extraction des données par KPI
            engagement_data = data.get("engagement_data", {})
            financial_data = data.get("financial_data", {})
            fundraising_data = data.get("fundraising_data", {})
            
            # Calculs des KPI
            public_engagement = self.public_engagement.calculate_score(engagement_data)
            
            default_alive = self.default_alive.calculate_metrics(
                cash_disponible=financial_data.get("cash_disponible", 0),
                charges_mensuelles=financial_data.get("charges_mensuelles"),
                fonds_promis=financial_data.get("fonds_promis", 0),
                previous_value=financial_data.get("previous_default_alive")
            )
            
            fundraising_pipeline = self.fundraising_pipeline.calculate_score(
                donnees_fundraising=fundraising_data,
                objectif_total=fundraising_data.get("objectif_total", 4547)
            )
            
            return {
                "public_engagement": public_engagement,
                "default_alive": default_alive,
                "fundraising_pipeline": fundraising_pipeline,
                "calculation_timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul Dashboard 1 KPI: {e}")
            return {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }