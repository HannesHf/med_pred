import pandas as pd
import json
from pathlib import Path
import random

# Pfad Konfiguration (Muss exakt zu deinem Preprocessing passen)
DATA_DIR = Path("../ML_DATA/processed")
VOCAB_FILE = DATA_DIR / "vocab.json"
PARQUET_FILE = DATA_DIR / "mimic_sequences.parquet"

def inspect():
    # 1. Vokabular laden
    if not VOCAB_FILE.exists():
        print(f"❌ Fehler: {VOCAB_FILE} nicht gefunden. Hast du das Preprocessing ausgeführt?")
        return

    print(f"📖 Lade Vokabular...")
    with open(VOCAB_FILE, "r") as f:
        vocab = json.load(f)
    
    # Reverse Map erstellen: Zahl -> Text (z.B. 42 -> "DIAG_123")
    id2token = {v: k for k, v in vocab.items()}
    print(f"✅ Vokabular Größe: {len(vocab)} Token")
    
    # 2. Sequenzen laden
    print(f"📂 Lade Parquet Daten (das kann kurz dauern)...")
    try:
        df = pd.read_parquet(PARQUET_FILE)
    except Exception as e:
        print(f"❌ Fehler beim Laden von {PARQUET_FILE}: {e}")
        return

    print(f"✅ Datensatz enthält {len(df)} Patienten-Sequenzen.")
    
    # 3. Interaktiver Loop
    while True:
        print("\n" + "="*60)
        user_input = input("Drücke ENTER für einen zufälligen Patienten (oder 'q' zum Beenden): ")
        if user_input.lower() == 'q':
            break
            
        # Zufällige Zeile ziehen
        row = df.sample(1).iloc[0]
        
        print(f"\n👤 Patient ID: {row['subject_id']}")
        print(f"💀 Label (Verstorben?): {row['label']}")
        print(f"📏 Sequenzlänge: {len(row['token_ids'])} Token")
        print("-" * 30)
        
        # Die IDs zurück in Text übersetzen
        # token_ids ist hier ein numpy array oder liste von ints
        decoded = [id2token.get(tid, "<UNK>") for tid in row['token_ids']]
        
        # Limitieren der Ausgabe, falls die Sequenz riesig ist
        if len(decoded) > 100:
            print(f"⚠️  (Zeige die ersten 100 von {len(decoded)} Events...)\n")
            decoded_view = decoded[:100]
        else:
            decoded_view = decoded

        # Hübsch formatierte Ausgabe ("Pretty Print")
        for token in decoded_view:
            if token == "ADM_START":
                print(f"\n🏥  >>> AUFNAHME START >>>")
            elif token == "ADM_END":
                print(f"🏁  <<< ENTLASSUNG <<< \n")
            elif token.startswith("TIME_"):
                # Zeit-Token formatieren
                print(f"   ⏱️  ... {token.replace('TIME_', '')} vergangen ...")
            elif token.startswith("DIAG_"):
                print(f"      🩺 {token}")
            elif token.startswith("MED_"):
                print(f"      💊 {token}")
            elif token.startswith("LAB_"):
                print(f"      🧪 {token}")
            else:
                print(f"      • {token}")

if __name__ == "__main__":
    inspect()