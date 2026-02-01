import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

DATA_PATH = Path("../ML_DATA/processed/mimic_sequences.parquet")

def plot_full_lengths():
    if not DATA_PATH.exists():
        print(f"❌ Datei nicht gefunden: {DATA_PATH.resolve()}")
        return

    print("📊 Berechne echte Patienten-Längen (aggregiere Chunks)...")
    
    # Wir summieren die Längen aller Chunks eines Patienten auf
    query = f"""
        SELECT 
            subject_id,
            SUM(len(token_ids)) as total_len,
            COUNT(*) as num_chunks
        FROM '{str(DATA_PATH).replace("\\", "/")}'
        GROUP BY subject_id
    """
    
    df = duckdb.query(query).df()
    
    print(f"✅ Analyse abgeschlossen.")
    print(f"   Anzahl Patienten: {len(df)}")
    print(f"   Durschn. Länge:   {df['total_len'].mean():.1f} Events")
    print(f"   Median Länge:     {df['total_len'].median():.1f} Events")
    print(f"   Max Länge:        {df['total_len'].max()} Events")
    
    # Perzentile für Entscheidungshilfe
    p80 = np.percentile(df['total_len'], 80)
    p90 = np.percentile(df['total_len'], 90)
    p95 = np.percentile(df['total_len'], 95)
    print(f"   80% der Patienten haben < {p80:.0f} Events")
    print(f"   90% der Patienten haben < {p90:.0f} Events")
    print(f"   95% der Patienten haben < {p95:.0f} Events")

    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Wir schneiden für den Plot extrem lange Ausreißer ab (für bessere Lesbarkeit)
    # Zeige nur bis zum 95. Perzentil im Histogramm
    plot_data = df[df['total_len'] <= np.percentile(df['total_len'], 98)]
    
    sns.histplot(plot_data['total_len'], bins=100, color="#8e44ad", kde=False)
    
    plt.title("Wahre Verteilung der Patienten-Historien (Events)", fontsize=16)
    plt.xlabel("Anzahl Events (Total)", fontsize=12)
    plt.ylabel("Anzahl Patienten", fontsize=12)
    
    # Referenzlinien für mögliche Chunk-Größen
    colors = {'512': 'red', '1024': 'orange', '2048': 'green', '4096': 'blue'}
    for size, color in colors.items():
        val = int(size)
        plt.axvline(x=val, color=color, linestyle='--', label=f'Limit {val}')
        
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    
    plt.savefig("real_patient_lengths.png")
    print(f"\n🖼️ Plot gespeichert als: real_patient_lengths.png")
    plt.show()

if __name__ == "__main__":
    plot_full_lengths()