"""
Service de synchronisation automatique Basecamp → Google Sheets
Intégré dans le backend principal avec planification horaire
"""

import schedule
import time
import logging
import subprocess
import sys
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AutoSyncService:
    """Service de synchronisation automatique pour Basecamp → Google Sheets"""
    
    def __init__(self):
        self.sync_script_path = Path(__file__).parent.parent.parent / "basecamp_todos" / "sync_basecamp_to_sheets.py"
        self.running = False
        self.sync_count = 0
        self.last_sync: Optional[datetime] = None
        self.errors_count = 0
        self.scheduler_thread: Optional[threading.Thread] = None
        
    def execute_sync(self) -> Dict[str, Any]:
        """Exécute une synchronisation complète et retourne le résultat"""
        try:
            logger.info("🚀 Début de la synchronisation automatique Basecamp → Google Sheets")
            
            # Générer nom de rapport avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"auto_sync_report_{timestamp}.json"
            
            # Vérifier que le script existe
            if not self.sync_script_path.exists():
                raise FileNotFoundError(f"Script de synchronisation non trouvé: {self.sync_script_path}")
            
            # Préparer la commande
            cmd = [
                sys.executable, 
                str(self.sync_script_path), 
                "--output", 
                report_file
            ]
            
            # Exécuter la synchronisation
            result = subprocess.run(
                cmd,
                cwd=self.sync_script_path.parent,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                self.sync_count += 1
                self.last_sync = datetime.now()
                
                logger.info(f"✅ Synchronisation #{self.sync_count} réussie")
                logger.info(f"📊 Rapport généré: {report_file}")
                
                # Parser les statistiques de sortie
                stats = self._parse_sync_output(result.stdout)
                
                return {
                    "success": True,
                    "sync_number": self.sync_count,
                    "timestamp": self.last_sync.isoformat(),
                    "report_file": report_file,
                    "statistics": stats,
                    "message": f"Synchronisation #{self.sync_count} réussie"
                }
            else:
                self.errors_count += 1
                error_msg = f"Erreur synchronisation: code {result.returncode}"
                
                logger.error(error_msg)
                if result.stderr:
                    logger.error(f"Stderr: {result.stderr}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "stderr": result.stderr,
                    "stdout": result.stdout,
                    "return_code": result.returncode
                }
                
        except Exception as e:
            self.errors_count += 1
            error_msg = f"Exception durant synchronisation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "success": False,
                "error": error_msg,
                "exception": str(e)
            }
    
    def _parse_sync_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie de synchronisation pour extraire les statistiques"""
        stats = {
            "groups_processed": 0,
            "todos_synced": 0,
            "groups_details": []
        }
        
        try:
            lines = output.strip().split('\n')
            for line in lines:
                # Rechercher les lignes de statistiques
                if "todos écrits" in line:
                    # Extraire le nombre de todos
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            stats["todos_synced"] += int(part)
                            break
                elif "Synchronisation réussie" in line:
                    stats["groups_processed"] += 1
                    
        except Exception as e:
            logger.warning(f"Erreur parsing statistiques: {e}")
            
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du service"""
        next_sync = None
        try:
            next_run = schedule.next_run()
            next_sync = next_run.isoformat() if next_run else None
        except:
            pass
            
        return {
            "service_running": self.running,
            "sync_count": self.sync_count,
            "errors_count": self.errors_count,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "next_sync": next_sync,
            "script_path": str(self.sync_script_path),
            "script_exists": self.sync_script_path.exists()
        }
    
    def start_scheduler(self):
        """Démarre le planificateur automatique en arrière-plan"""
        if self.running:
            logger.warning("Le planificateur est déjà en cours d'exécution")
            return
            
        logger.info("🔄 Démarrage du planificateur de synchronisation automatique")
        logger.info("⏰ Synchronisation programmée toutes les heures")
        
        # Planifier la synchronisation toutes les heures
        schedule.every().hour.do(self.execute_sync)
        
        # Première synchronisation immédiate (optionnel)
        # logger.info("🚀 Exécution de la première synchronisation...")
        # self.execute_sync()
        
        self.running = True
        
        # Démarrer le thread du planificateur
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Planificateur de synchronisation démarré avec succès")
    
    def _run_scheduler(self):
        """Boucle principale du planificateur (exécutée en thread séparé)"""
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
        except Exception as e:
            logger.error(f"Erreur dans la boucle du planificateur: {e}", exc_info=True)
            self.running = False
    
    def stop_scheduler(self):
        """Arrête le planificateur"""
        if not self.running:
            logger.warning("Le planificateur n'est pas en cours d'exécution")
            return
            
        logger.info("🛑 Arrêt du planificateur de synchronisation")
        self.running = False
        
        # Nettoyer les tâches planifiées
        schedule.clear()
        
        # Attendre que le thread se termine (avec timeout)
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5.0)
            
        logger.info("✅ Planificateur arrêté")

# Instance globale du service
auto_sync_service = AutoSyncService()