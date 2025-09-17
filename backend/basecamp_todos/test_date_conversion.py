"""
Tests unitaires pour le convertisseur de dates Basecamp
Valide la conversion de différents formats vers Google Sheets
"""

import sys
from pathlib import Path
from date_converter import BasecampDateConverter

def test_date_conversion_comprehensive():
    """Test complet du convertisseur de dates"""
    converter = BasecampDateConverter()
    
    # Test cases avec formats variés - Format américain M/D/YYYY
    test_cases = [
        # Format Basecamp standard
        ("2025-12-31", "12/31/2025", "ISO Standard"),
        ("2024-08-17", "8/17/2024", "ISO Standard"),
        
        # Formats avec time
        ("2025-08-17T10:30:00Z", "8/17/2025", "ISO DateTime"),
        ("2025-08-17T10:30:00", "8/17/2025", "ISO DateTime"),
        
        # Formats européens convertis en américain
        ("31/12/2025", "12/31/2025", "Européen"),
        ("17-08-2025", "8/17/2025", "Européen tirets"),
        
        # Formats ISO variés
        ("2025/12/31", "12/31/2025", "ISO slashes"),
        
        # Cases limites
        ("", "", "Date vide"),
        ("invalid_date", "invalid_date", "Format invalide"),
        ("2025-13-40", "2025-13-40", "Date invalide"),
    ]
    
    print("=== TEST COMPLET CONVERSION DATES ===")
    print(f"{'Input':<25} {'Expected':<12} {'Actual':<12} {'Status':<10} {'Format'}")
    print("-" * 75)
    
    passed = 0
    failed = 0
    
    for input_date, expected_output, test_type in test_cases:
        actual_output = converter.convert_to_format(input_date, 'google_sheets_fr')
        
        if actual_output == expected_output:
            status = "[PASS]"
            passed += 1
        else:
            status = "[FAIL]"
            failed += 1
        
        # Détecter le format pour les cas valides
        format_detected = "N/A"
        if input_date:
            validation = converter.validate_date(input_date)
            if validation['detected_format']:
                format_detected = validation['detected_format'][:15]  # Tronquer pour affichage
        
        print(f"{input_date:<25} {expected_output:<12} {actual_output:<12} {status:<10} {format_detected}")
    
    print("-" * 75)
    success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
    print(f"Résultats: {passed} passés, {failed} échoués ({success_rate:.1f}% réussite)")
    
    # Stats du convertisseur
    stats = converter.get_conversion_stats()
    print(f"\nStatistiques convertisseur:")
    print(f"  Total conversions: {stats['total_conversions']}")
    print(f"  Succès: {stats['successful_conversions']} ({stats['success_rate']}%)")
    print(f"  Formats détectés: {list(stats['formats_detected'].keys())}")
    
    return passed, failed

def test_edge_cases():
    """Test des cas limites spécifiques"""
    converter = BasecampDateConverter()
    
    edge_cases = [
        # Années bissextiles
        "2024-02-29",  # Année bissextile valide
        "2023-02-29",  # Année non bissextile invalide
        
        # Dates limites
        "2000-01-01",  # Y2K
        "2099-12-31",  # Futur lointain
        
        # Formats avec millisecondes
        "2025-08-17T10:30:00.123Z",
        "2025-08-17T10:30:00.123456Z",
        
        # Formats avec timezone
        "2025-08-17T10:30:00+02:00",
        "2025-08-17T10:30:00-05:00",
    ]
    
    print("\n=== TEST CAS LIMITES ===")
    for date in edge_cases:
        validation = converter.validate_date(date)
        converted = converter.convert_to_format(date, 'google_sheets_fr')
        
        status = "[OK]" if validation['is_valid'] else "[KO]"
        print(f"{status} {date:<30} -> {converted:<12} [{validation.get('detected_format', 'Non detecte')}]")
        
        if validation['errors']:
            print(f"    Erreurs: {', '.join(validation['errors'])}")

def test_multiple_formats():
    """Test de conversion vers différents formats de sortie"""
    converter = BasecampDateConverter()
    
    input_date = "2025-08-17"
    
    print(f"\n=== TEST FORMATS MULTIPLES ===")
    print(f"Date d'entrée: {input_date}")
    
    output_formats = ['google_sheets_fr', 'iso', 'excel', 'american', 'verbose_fr']
    
    for format_name in output_formats:
        converted = converter.convert_to_format(input_date, format_name)
        print(f"  {format_name:<15}: {converted}")

def benchmark_conversion():
    """Benchmark de performance de conversion"""
    import time
    
    converter = BasecampDateConverter()
    
    # Générer beaucoup de dates pour le benchmark
    test_dates = [f"2025-{month:02d}-{day:02d}" for month in range(1, 13) for day in range(1, 29)]
    
    print(f"\n=== BENCHMARK PERFORMANCE ===")
    print(f"Conversion de {len(test_dates)} dates...")
    
    start_time = time.time()
    
    for date in test_dates:
        converter.convert_to_format(date, 'google_sheets_fr')
    
    end_time = time.time()
    duration = end_time - start_time
    conversions_per_second = len(test_dates) / duration
    
    stats = converter.get_conversion_stats()
    
    print(f"Temps total: {duration:.3f}s")
    print(f"Vitesse: {conversions_per_second:.0f} conversions/seconde")
    print(f"Réussite: {stats['success_rate']}%")

if __name__ == "__main__":
    # Exécuter tous les tests
    print("=== TESTS DU CONVERTISSEUR DE DATES BASECAMP ===")
    print("=" * 50)
    
    passed, failed = test_date_conversion_comprehensive()
    test_edge_cases()
    test_multiple_formats()
    benchmark_conversion()
    
    print("\n" + "=" * 50)
    if failed == 0:
        print("=== TOUS LES TESTS SONT PASSES ! ===")
    else:
        print(f"=== {failed} tests ont echoue sur {passed + failed} ===")
    
    print("=== Tests termines ===")