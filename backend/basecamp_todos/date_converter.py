"""
Module de conversion avancée des dates pour Basecamp → Google Sheets
Gère tous les formats possibles avec validation et formatage intelligent
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)

class BasecampDateConverter:
    """Convertisseur de dates avancé pour Basecamp"""
    
    def __init__(self):
        # Formats de dates supportés (ordre de priorité)
        self.date_patterns = [
            # Format ISO standard Basecamp
            {
                'pattern': r'^\d{4}-\d{2}-\d{2}$',
                'format': '%Y-%m-%d',
                'description': 'ISO Standard (YYYY-MM-DD)'
            },
            # Format ISO avec time
            {
                'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
                'format': '%Y-%m-%dT%H:%M:%S',
                'description': 'ISO DateTime (YYYY-MM-DDTHH:MM:SS)'
            },
            # Formats européens
            {
                'pattern': r'^\d{2}/\d{2}/\d{4}$',
                'format': '%d/%m/%Y',
                'description': 'Européen (DD/MM/YYYY)'
            },
            {
                'pattern': r'^\d{2}-\d{2}-\d{4}$',
                'format': '%d-%m-%Y',
                'description': 'Européen tirets (DD-MM-YYYY)'
            },
            # Formats américains
            {
                'pattern': r'^\d{2}/\d{2}/\d{4}$',
                'format': '%m/%d/%Y',
                'description': 'Américain (MM/DD/YYYY)'
            },
            # Formats raccourcis
            {
                'pattern': r'^\d{4}/\d{2}/\d{2}$',
                'format': '%Y/%m/%d',
                'description': 'ISO slashes (YYYY/MM/DD)'
            }
        ]
        
        # Formats de sortie supportés
        self.output_formats = {
            'google_sheets_fr': 'custom_no_leading_zeros',  # Format français sans zéros de tête
            'google_sheets_fr_padded': '%d/%m/%Y',          # Format français avec zéros de tête
            'iso': '%Y-%m-%d',                              # Format ISO standard
            'excel': '%d/%m/%Y',                            # Format Excel français
            'american': '%m/%d/%Y',                         # Format américain
            'verbose_fr': '%d %B %Y',                       # Format verbeux français
        }
        
        # Statistiques de conversion
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'formats_detected': {},
            'errors': []
        }
    
    def detect_date_format(self, date_str: str) -> Optional[Dict[str, str]]:
        """Détecte automatiquement le format d'une date"""
        if not date_str or not isinstance(date_str, str):
            return None
            
        date_str = date_str.strip()
        
        for pattern_info in self.date_patterns:
            if re.match(pattern_info['pattern'], date_str):
                return pattern_info
                
        return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date depuis différents formats avec détection automatique"""
        if not date_str or not isinstance(date_str, str):
            return None
            
        date_str = date_str.strip()
        
        # Nettoyer les caractères spéciaux (timezone, etc.)
        if 'Z' in date_str:
            date_str = date_str.replace('Z', '+00:00')
        if '+' in date_str and 'T' in date_str:
            date_str = date_str.split('+')[0]  # Supprimer timezone
            
        # Détecter le format
        format_info = self.detect_date_format(date_str)
        
        if format_info:
            try:
                # Cas spécial pour datetime ISO
                if 'T' in date_str:
                    # Gérer les millisecondes optionnelles
                    if '.' in date_str:
                        date_str = date_str.split('.')[0]
                    return datetime.fromisoformat(date_str.replace('T', ' '))
                
                # Parse normal
                parsed_date = datetime.strptime(date_str, format_info['format'])
                
                # Mise à jour des stats
                format_desc = format_info['description']
                if format_desc not in self.conversion_stats['formats_detected']:
                    self.conversion_stats['formats_detected'][format_desc] = 0
                self.conversion_stats['formats_detected'][format_desc] += 1
                
                return parsed_date
                
            except ValueError as e:
                logger.warning(f"Erreur parsing date '{date_str}' avec format {format_info['description']}: {e}")
        
        # Tentative de parsing automatique en dernier recours
        try:
            # Essayer la détection automatique Python
            return datetime.fromisoformat(date_str.replace('/', '-'))
        except:
            pass
            
        logger.warning(f"Format de date non reconnu: '{date_str}'")
        self.conversion_stats['errors'].append(f"Format non reconnu: '{date_str}'")
        return None
    
    def convert_to_format(self, date_str: str, output_format: str = 'google_sheets_fr') -> str:
        """Convertit une date vers le format de sortie spécifié"""
        self.conversion_stats['total_conversions'] += 1
        
        if not date_str:
            return ""
            
        # Parser la date
        parsed_date = self.parse_date(date_str)
        
        if parsed_date:
            try:
                # Obtenir le format de sortie
                if output_format in self.output_formats:
                    format_str = self.output_formats[output_format]
                else:
                    format_str = output_format  # Format personnalisé
                
                # Gestion spéciale pour format Google Sheets sans zéros de tête
                if output_format == 'google_sheets_fr':
                    # Format personnalisé : M/D/YYYY (sans zéros de tête) - Format américain
                    day = parsed_date.day
                    month = parsed_date.month  
                    year = parsed_date.year
                    converted = f"{month}/{day}/{year}"
                else:
                    # Convertir avec strftime standard
                    converted = parsed_date.strftime(format_str)
                
                self.conversion_stats['successful_conversions'] += 1
                
                logger.debug(f"Date convertie: '{date_str}' → '{converted}'")
                return converted
                
            except Exception as e:
                logger.error(f"Erreur formatage date {parsed_date}: {e}")
                self.conversion_stats['failed_conversions'] += 1
                return date_str  # Retourner l'original en cas d'erreur
        else:
            self.conversion_stats['failed_conversions'] += 1
            return date_str  # Retourner l'original si parsing échoue
    
    def validate_date(self, date_str: str) -> Dict[str, Any]:
        """Valide une date et retourne des informations détaillées"""
        result = {
            'original': date_str,
            'is_valid': False,
            'parsed_date': None,
            'detected_format': None,
            'converted_formats': {},
            'errors': []
        }
        
        if not date_str:
            result['errors'].append("Date vide")
            return result
        
        # Détecter le format
        format_info = self.detect_date_format(date_str)
        if format_info:
            result['detected_format'] = format_info['description']
        
        # Parser
        parsed = self.parse_date(date_str)
        if parsed:
            result['is_valid'] = True
            result['parsed_date'] = parsed.isoformat()
            
            # Convertir vers tous les formats supportés
            for format_name in self.output_formats:
                try:
                    converted = self.convert_to_format(date_str, format_name)
                    result['converted_formats'][format_name] = converted
                except Exception as e:
                    result['errors'].append(f"Erreur conversion {format_name}: {e}")
        else:
            result['errors'].append("Impossible de parser la date")
        
        return result
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de conversion"""
        success_rate = 0
        if self.conversion_stats['total_conversions'] > 0:
            success_rate = (self.conversion_stats['successful_conversions'] / 
                          self.conversion_stats['total_conversions']) * 100
        
        return {
            **self.conversion_stats,
            'success_rate': round(success_rate, 2)
        }
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'formats_detected': {},
            'errors': []
        }

# Instance globale pour utilisation dans les scripts
date_converter = BasecampDateConverter()

def convert_basecamp_date(date_str: str, output_format: str = 'google_sheets_fr') -> str:
    """Fonction utilitaire pour conversion rapide"""
    return date_converter.convert_to_format(date_str, output_format)

def validate_basecamp_date(date_str: str) -> Dict[str, Any]:
    """Fonction utilitaire pour validation rapide"""
    return date_converter.validate_date(date_str)

if __name__ == "__main__":
    # Tests de démonstration
    converter = BasecampDateConverter()
    
    test_dates = [
        "2025-12-31",
        "2025-08-17",
        "31/12/2025",
        "12/31/2025",
        "2025/12/31",
        "31-12-2025",
        "2025-08-17T10:30:00Z",
        "invalid_date",
        "",
        None
    ]
    
    print("=== TEST DU CONVERTISSEUR DE DATES ===")
    for date in test_dates:
        print(f"\nDate: {date}")
        validation = converter.validate_date(str(date) if date else "")
        print(f"  Valid: {validation['is_valid']}")
        if validation['is_valid']:
            print(f"  Format détecté: {validation['detected_format']}")
            print(f"  Google Sheets: {validation['converted_formats'].get('google_sheets_fr', 'N/A')}")
        else:
            print(f"  Erreurs: {validation['errors']}")
    
    print(f"\n=== STATISTIQUES ===")
    stats = converter.get_conversion_stats()
    print(f"Total conversions: {stats['total_conversions']}")
    print(f"Succès: {stats['successful_conversions']}")
    print(f"Échecs: {stats['failed_conversions']}")
    print(f"Taux de réussite: {stats['success_rate']}%")