import pandas as pd
import glob
import os

# Konfiguration
base_path = "../../data/mimic-iv-3.1/"
dirs = ["icu", "hosp"]
output_file = "mimic_tabellen_report.md"

# Datei zum Schreiben öffnen (überschreibt existierende Datei)
with open(output_file, "w", encoding="utf-8") as f:
    
    # Header für das Markdown Document
    f.write("# MIMIC-IV Tabellen Übersicht\n\n")
    f.write(f"Erstellt für Pfad: `{base_path}`\n\n")

    for ordner in dirs:
        # Suchmuster zusammenbauen (z.B. ../data/mimic-iv-3.1/icu/*.csv.gz)
        suchpfad = os.path.join(base_path, ordner, "*.csv.gz")
        dateien = glob.glob(suchpfad)
        
        for datei_pfad in dateien:
            # Metadaten extrahieren
            dateiname = os.path.basename(datei_pfad)
            titel = dateiname.split('.')[0]
            
            try:
                # WICHTIG: Nur 1 Zeile laden, um RAM zu sparen!
                df_preview = pd.read_csv(datei_pfad, nrows=1)
                
                # Markdown Inhalt schreiben
                f.write(f"### 📂 Tabelle: `{titel}` (aus `{ordner}`)\n")
                f.write(f"- **Voller Pfad:** `{datei_pfad}`\n")
                
                # Spaltenliste formatieren
                cols_str = ", ".join([f"`{c}`" for c in df_preview.columns])
                f.write(f"- **Spalten:** {cols_str}\n\n")
                
                # Beispielzeile als Markdown-Tabelle
                f.write("**Beispielzeile:**\n")
                # to_markdown benötigt das Paket 'tabulate' (pip install tabulate)
                f.write(df_preview.to_markdown(index=False))
                
                f.write("\n\n---\n\n")
                
                print(f"✅ Geloggt: {titel}")
                
            except Exception as e:
                f.write(f"### ❌ Fehler bei `{titel}`\n> {str(e)}\n\n---\n\n")
                print(f"❌ Fehler: {titel}")

print(f"\nFertig! Die Übersicht liegt in '{output_file}'")