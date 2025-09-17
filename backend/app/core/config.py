"""
Configuration de l'application AGRIFRIKA Dashboard
Gestion des variables d'environnement et paramètres
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # Configuration serveur
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]
    
    # Facebook API
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_PAGE_TOKEN: str = ""
    FACEBOOK_PAGE_ID: str = ""
    
    # LinkedIn API
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    
    # Google Analytics
    GA_PROPERTY_ID: str = ""
    GA_CREDENTIALS_PATH: str = "config/credentials/google-analytics-credentials.json"
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = "config/credentials/google-sheets-new-credentials.json"
    PLANNING_SHEET_ID: str = "1x6-qEBJW3DFBXZI0PmkHfoLfrjRfsaH-kOB-KamNFDk"
    PLANNING_RANGE_TEMPLATE: str = "{week}!A2:G50"
    PLANNING_FALLBACK_RANGE: str = "33!A2:G50"
    AVAILABILITY_SHEET_ID: str = "1fc5AoqzGoCibnfZTkzVxwC_ztqzfiuUyrP5PVXrj3mM"
    AVAILABILITY_RANGE_TEMPLATE: str = "W{week}!A3:O20"
    AVAILABILITY_FALLBACK_RANGE: str = "W33!A3:O20"
    
    # Public Engagement Google Sheet
    PUBLIC_ENGAGEMENT_SHEET_ID: str = "1nmkcL0o_6V2XElDZDUCcBCEvovrGkqQInRYw-xmWsFo"
    ENGAGEMENT_METRICS_RANGE: str = "Parametres_Engagement!A2:O50"  # Ajout colonne Status (O)
    VIDEOS_RANGE: str = "Videos!A2:I50"
    
    # Fundraising Pipeline Google Sheet
    FUNDRAISING_PIPELINE_SHEET_ID: str = "1c78RDASnzYM6SkOa2rvM25RFF1IDg2ESv46itE_78R0"
    FUNDRAISING_RANGE: str = "fundraising!A2:Q50"  # Ajout colonne IsTotal (Q)
    
    # Todos Google Sheet (Migration from Basecamp)
    TODOS_SHEET_ID: str = "1gvIZvkSLf30DBglxblA8ttpkzvy-8twwcl-wlaGy33Y"
    TODOS_SHEET_NAMES: List[str] = [
        "Commercial",
        "Capital Humain - Stages", 
        "Capital Humain",
        "Prestataires",
        "Ressources Matérielles",
        "Accélération Développement",
        "Produit",
        "IT",
        "Partenariats",
        "Design & Branding",
        "Investors",
        "Opérations",
        "Marketing Communication RP",
        "Money",
        "Agrifika-Copyright",
        "Administration-management",
        "Abaca Assessment"
    ]
    TODOS_RANGE_TEMPLATE: str = "{sheet_name}!A1:E500"  # ID, Title, Status, Assigned_To, Due_Date
    
    
    # Basecamp API
    BASECAMP_CLIENT_ID: str = "d8facbd0673f0aaf17950c70a0d9bcdad78e47ff"
    BASECAMP_CLIENT_SECRET: str = "52a6a99a28ded6fa5fc52e3d30eb0109af1e36cc"
    BASECAMP_ACCESS_TOKEN: str = "BAhbB0kiAbB7ImNsaWVudF9pZCI6ImQ4ZmFjYmQwNjczZjBhYWYxNzk1MGM3MGEwZDliY2RhZDc4ZTQ3ZmYiLCJleHBpcmVzX2F0IjoiMjAyNS0wOS0wMlQwODoyNzoxNloiLCJ1c2VyX2lkcyI6WzUxNTU1ODg3XSwidmVyc2lvbiI6MSwiYXBpX2RlYWRib2x0IjoiNTY0ZmQzNmYyYjljZDU4YzI3MmVhZDRhZmFjZGRmOWMifQY6BkVUSXU6CVRpbWUNSGAfwGXgA20JOg1uYW5vX251bWkCqwE6DW5hbm9fZGVuaQY6DXN1Ym1pY3JvIgdCcDoJem9uZUkiCFVUQwY7AEY=--25ad8830efaefe59de843a3dfa6c4b81a9e7bccb"
    BASECAMP_REFRESH_TOKEN: str = "BAhbB0kiAbB7ImNsaWVudF9pZCI6ImQ4ZmFjYmQwNjczZjBhYWYxNzk1MGM3MGEwZDliY2RhZDc4ZTQ3ZmYiLCJleHBpcmVzX2F0IjoiMjAzNS0wOC0xOVQwODoyNzoxNloiLCJ1c2VyX2lkcyI6WzUxNTU1ODg3XSwidmVyc2lvbiI6MSwiYXBpX2RlYWRib2x0IjoiNTY0ZmQzNmYyYjljZDU4YzI3MmVhZDRhZmFjZGRmOWMifQY6BkVUSXU6CVRpbWUNaN4hwOrtA20JOg1uYW5vX251bWkClwM6DW5hbm9fZGVuaQY6DXN1Ym1pY3JvIgeRkDoJem9uZUkiCFVUQwY7AEY=--23efea0b7ec3ed4aa7d79e2305311cbbd3796881"
    BASECAMP_ACCOUNT_ID: str = "5809639"
    BASECAMP_PROJECT_ID: str = "29734885"
    
    # Cache et performance
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    API_RATE_LIMIT_PER_MINUTE: int = 60
    
    # Base de données
    DATABASE_URL: str = "sqlite:///./agrifrika_dashboard.db"
    
    class Config:
        env_file = "config/.env"
        case_sensitive = True
    
    @property
    def ga_credentials_full_path(self) -> str:
        """Chemin complet vers les credentials Google Analytics"""
        # Construire le chemin depuis la racine du projet
        project_root = Path(__file__).parent.parent.parent.parent
        return str(project_root / self.GA_CREDENTIALS_PATH)
    
    @property 
    def sheets_credentials_full_path(self) -> str:
        """Chemin complet vers les credentials Google Sheets"""
        # Construire le chemin depuis la racine du projet
        project_root = Path(__file__).parent.parent.parent.parent
        return str(project_root / self.GOOGLE_SHEETS_CREDENTIALS_PATH)
    
    def validate_credentials(self) -> dict:
        """Valide la présence des credentials essentiels"""
        validation = {
            "facebook": bool(self.FACEBOOK_PAGE_TOKEN and self.FACEBOOK_PAGE_ID),
            "linkedin": bool(self.LINKEDIN_ACCESS_TOKEN),
            "google_analytics": bool(self.GA_PROPERTY_ID and os.path.exists(self.ga_credentials_full_path)),
            "google_sheets": bool(self.PLANNING_SHEET_ID and os.path.exists(self.sheets_credentials_full_path)),
            "basecamp": bool(self.BASECAMP_ACCESS_TOKEN and self.BASECAMP_ACCOUNT_ID)
        }
        return validation

# Instance globale des paramètres
settings = Settings()