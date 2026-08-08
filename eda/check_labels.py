import duckdb
from pathlib import Path

DATA_PATH = Path("../ML_DATA/processed/mimic_sequences.parquet")

def check_label_meaning():
    print("📊 Prüfe Label-Verteilung...")
    
    query = f"""
        SELECT 
            label, 
            COUNT(*) as count,
            (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM '{str(DATA_PATH).replace("\\", "/")}') ) as percentage
        FROM '{str(DATA_PATH).replace("\\", "/")}'
        GROUP BY label
        ORDER BY label
    """
    
    df = duckdb.query(query).df()
    print(df)
    
    # Interpretation
    count_0 = df[df['label'] == 0]['count'].values[0]
    count_1 = df[df['label'] == 1]['count'].values[0]
    
    print("\n--- INTERPRETATION ---")
    if count_1 < count_0:
        print("✅ Label 1 ist die MINDERHEIT (das seltene Event).")
        print("   -> 1 bedeutet höchstwahrscheinlich 'VERSTORBEN'.")
        print("   -> Deine Metriken (AUPRC, Recall) messen die Qualität der Todes-Vorhersage.")
    else:
        print("⚠️ Label 1 ist die MEHRHEIT.")
        print("   -> 1 bedeutet 'ÜBERLEBT'.")
        print("   -> Wir müssen das Label flippen, sonst optimieren wir auf das Falsche!")

if __name__ == "__main__":
    check_label_meaning()