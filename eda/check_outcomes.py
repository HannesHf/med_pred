import duckdb
from pathlib import Path

# Wir brauchen die Rohdaten (Admissions), nicht nur die Sequenzen
MIMIC_RAW_PATH = Path("../data/mimic-iv-3.1/hosp/admissions.csv.gz")

def analyze_quality_of_life():
    print("🏥 Analysiere Entlassungs-Orte (Proxy für Lebensqualität)...")
    
    # Wir schauen uns nur die Patienten an, die NICHT gestorben sind (hospital_expire_flag = 0)
    query = f"""
        SELECT 
            discharge_location,
            COUNT(*) as count
        FROM read_csv_auto('{MIMIC_RAW_PATH}')
        WHERE hospital_expire_flag = 0
        GROUP BY discharge_location
        ORDER BY count DESC
    """
    
    try:
        df = duckdb.query(query).df()
        
        # Berechnung der Anteile
        total_survivors = df['count'].sum()
        df['percentage'] = (df['count'] / total_survivors * 100).round(1)
        
        print(f"\nAnzahl Überlebende in Analyse: {total_survivors}")
        print("-" * 60)
        print(f"{'ENTLASSUNG NACH':<40} | {'ANZAHL':<10} | {'ANTEIL %':<10}")
        print("-" * 60)
        
        for _, row in df.iterrows():
            print(f"{str(row['discharge_location']):<40} | {row['count']:<10} | {row['percentage']}%")
            
    except Exception as e:
        print(f"Fehler: {e}")
        print("Stelle sicher, dass der Pfad zu admissions.csv.gz stimmt!")

if __name__ == "__main__":
    analyze_quality_of_life()