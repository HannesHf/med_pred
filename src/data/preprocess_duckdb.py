import duckdb
import pandas as pd
import json
import os
import shutil
import sys
from pathlib import Path

# --- KONFIGURATION ---
MIMIC_PATH = Path("../data/mimic-iv-3.1") 
OUTPUT_PATH = Path("../ML_DATA/processed") 
TEMP_DIR = Path("../ML_DATA/duckdb_temp") 

CHUNK_SIZE = 512 
MIN_FREQ = 5 

def run_pipeline():
    print(f"🦆 Starte DuckDB Pipeline (Type-Safe & Debugged)...")
    
    # Pfade absolut machen (WICHTIG für Windows)
    abs_mimic = MIMIC_PATH.resolve()
    abs_output = OUTPUT_PATH.resolve()
    abs_temp = TEMP_DIR.resolve()
    
    print(f"   📂 Rohdaten: {abs_mimic}")
    print(f"   💾 Output:   {abs_output}")
    print(f"   ⚙️ Temp:     {abs_temp}")

    abs_output.mkdir(parents=True, exist_ok=True)
    if abs_temp.exists(): shutil.rmtree(abs_temp)
    abs_temp.mkdir(parents=True, exist_ok=True)

    db_file = abs_output / "mimic_temp.db"
    if db_file.exists(): os.remove(db_file)

    con = duckdb.connect(str(db_file))
    
    # RAM & Temp Config
    con.execute("SET memory_limit='8GB'") 
    # Temp Verzeichnis muss absolut sein und Slashes haben
    temp_sql_path = str(abs_temp).replace("\\", "/")
    con.execute(f"SET temp_directory='{temp_sql_path}'")
    con.execute("SET threads=4")
    con.execute("SET preserve_insertion_order=false")

    # ---------------------------------------------------------
    # 1. VIEWS (Mit Typ-Casting!)
    # ---------------------------------------------------------
    print("   ... 1/7 Lade Tabellen (mit Type-Safety)")
    
    # Helper um Pfade sicher zu machen
    def safe_path(subpath):
        return str(abs_mimic / subpath).replace("\\", "/")

    # WICHTIG: Wir lesen alles, casten aber subject_id sofort zu BIGINT
    con.execute(f"CREATE OR REPLACE VIEW raw_diagnoses AS SELECT CAST(subject_id AS BIGINT) as subject_id, hadm_id, icd_code FROM read_csv('{safe_path('hosp/diagnoses_icd.csv.gz')}', AUTO_DETECT=TRUE)")
    con.execute(f"CREATE OR REPLACE VIEW raw_labs AS SELECT CAST(subject_id AS BIGINT) as subject_id, itemid, flag, charttime FROM read_csv('{safe_path('hosp/labevents.csv.gz')}', AUTO_DETECT=TRUE)")
    con.execute(f"CREATE OR REPLACE VIEW raw_meds AS SELECT CAST(subject_id AS BIGINT) as subject_id, drug, starttime FROM read_csv('{safe_path('hosp/prescriptions.csv.gz')}', AUTO_DETECT=TRUE)")
    con.execute(f"CREATE OR REPLACE VIEW raw_admissions AS SELECT CAST(subject_id AS BIGINT) as subject_id, hadm_id, admittime, dischtime, hospital_expire_flag FROM read_csv('{safe_path('hosp/admissions.csv.gz')}', AUTO_DETECT=TRUE)")

    # ---------------------------------------------------------
    # 2. UNION
    # ---------------------------------------------------------
    print("   ... 2/7 Vereinige Events (Union)")
    con.execute("""
        CREATE OR REPLACE TABLE all_events_base AS
        SELECT subject_id, admittime as t, 0 as priority, 'ADM_START' as token FROM raw_admissions
        UNION ALL
        SELECT subject_id, charttime as t, 1 as priority, 'LAB_' || itemid || '_' || flag as token FROM raw_labs WHERE flag = 'abnormal'
        UNION ALL
        SELECT subject_id, starttime as t, 1 as priority, 'MED_' || drug as token FROM raw_meds WHERE drug IS NOT NULL
        UNION ALL
        SELECT d.subject_id, a.dischtime as t, 2 as priority, 'DIAG_' || icd_code as token FROM raw_diagnoses d JOIN raw_admissions a ON d.hadm_id = a.hadm_id
        UNION ALL
        SELECT subject_id, dischtime as t, 3 as priority, 'ADM_END' as token FROM raw_admissions
    """)
    
    # DEBUG CHECK
    count = con.execute("SELECT count(*) FROM all_events_base").fetchone()[0]
    print(f"      📊 Events gefunden: {count}")
    if count == 0:
        print("❌ FEHLER: Keine Events geladen! Pfade prüfen.")
        sys.exit(1)

    # ---------------------------------------------------------
    # 3. TIME DELTAS
    # ---------------------------------------------------------
    print("   ... 3/7 Berechne Zeitabstände")
    con.execute("""
        CREATE OR REPLACE TABLE events_with_lag AS
        SELECT *, date_diff('minute', LAG(t) OVER (PARTITION BY subject_id ORDER BY t, priority), t) as diff_minutes
        FROM all_events_base
    """)
    con.execute("DROP TABLE all_events_base")

    # ---------------------------------------------------------
    # 4. TIME TOKENS
    # ---------------------------------------------------------
    print("   ... 4/7 Generiere Time-Tokens")
    con.execute("""
        CREATE OR REPLACE TABLE time_tokens AS
        SELECT subject_id, t, priority, 
            CASE 
                WHEN diff_minutes > 525600 THEN 'TIME_GT_12M'
                WHEN diff_minutes > 262800 THEN 'TIME_GT_6M'
                WHEN diff_minutes > 43200  THEN 'TIME_GT_1M'
                WHEN diff_minutes > 20160  THEN 'TIME_GT_14D'
                WHEN diff_minutes > 7200   THEN 'TIME_GT_5D'
                WHEN diff_minutes > 2880   THEN 'TIME_GT_2D'
                WHEN diff_minutes > 1440   THEN 'TIME_GT_24H'
                WHEN diff_minutes > 720    THEN 'TIME_GT_12H'
                WHEN diff_minutes > 480    THEN 'TIME_GT_8H'
                WHEN diff_minutes > 240    THEN 'TIME_GT_4H'
                WHEN diff_minutes > 120    THEN 'TIME_GT_2H'
                WHEN diff_minutes > 30     THEN 'TIME_GT_30MIN'
                WHEN diff_minutes > 1      THEN 'TIME_GT_1MIN'
                ELSE NULL
            END as token
        FROM events_with_lag WHERE diff_minutes > 1
    """)

    con.execute("""
        CREATE OR REPLACE TABLE final_stream AS
        SELECT subject_id, t, priority, 1 as sub_priority, token FROM events_with_lag
        UNION ALL
        SELECT subject_id, t, priority, 0 as sub_priority, token FROM time_tokens WHERE token IS NOT NULL
    """)
    
    con.execute("DROP TABLE events_with_lag")
    con.execute("DROP TABLE time_tokens")

    # ---------------------------------------------------------
    # 5. VOKABULAR
    # ---------------------------------------------------------
    print("   ... 5/7 Erstelle Vokabular")
    vocab_df = con.execute(f"""
        SELECT token, count(*) as freq FROM final_stream 
        WHERE token NOT LIKE 'TIME_%' AND token NOT LIKE 'ADM_%'
        GROUP BY token HAVING count(*) >= {MIN_FREQ}
        ORDER BY freq DESC
    """).df()
    special_df = con.execute("SELECT DISTINCT token FROM final_stream WHERE token LIKE 'TIME_%' OR token LIKE 'ADM_%'").df()
    
    vocab = {"<PAD>": 0, "<UNK>": 1, "<CLS>": 2, "<SEP>": 3}
    for t in special_df['token'].tolist():
        if t not in vocab: vocab[t] = len(vocab)
    for t in vocab_df['token'].tolist():
        if t not in vocab: vocab[t] = len(vocab)
        
    with open(abs_output / "vocab.json", "w") as f:
        json.dump(vocab, f)
    print(f"      ✅ Vokabular Größe: {len(vocab)} Token")

    # ---------------------------------------------------------
    # 6. MAPPING & CHUNKING
    # ---------------------------------------------------------
    print("   ... 6/7 Berechne Chunks")
    
    con.execute("CREATE OR REPLACE TABLE vocab_map (token VARCHAR, id INTEGER)")
    con.executemany("INSERT INTO vocab_map VALUES (?, ?)", [(k, v) for k, v in vocab.items()])

    con.execute(f"""
        CREATE OR REPLACE TABLE stream_integers AS
        WITH ranked_events AS (
            SELECT 
                s.subject_id, 
                s.t, 
                s.priority, 
                s.sub_priority,
                COALESCE(v.id, 1) as token_id,
                ROW_NUMBER() OVER (PARTITION BY s.subject_id ORDER BY s.t ASC, s.priority ASC) as rn
            FROM final_stream s
            LEFT JOIN vocab_map v ON s.token = v.token
        )
        SELECT 
            subject_id, 
            t, 
            token_id,
            CAST(FLOOR((rn - 1) / {CHUNK_SIZE}) AS INTEGER) as chunk_id
        FROM ranked_events
    """)

    # Check ob stream_integers leer ist
    count = con.execute("SELECT count(*) FROM stream_integers").fetchone()[0]
    print(f"      📊 Events nach Mapping: {count}")
    
    print("      🧹 Lösche RAM-Tabellen...")
    con.execute("DROP TABLE final_stream")
    con.execute("DROP TABLE vocab_map")
    con.execute("CHECKPOINT")

    # ---------------------------------------------------------
    # 7. AGGREGATION & EXPORT
    # ---------------------------------------------------------
    print("   ... 7/7 Aggregiere Chunks & Speichere")
    
    parquet_sql_path = str(abs_output / 'mimic_sequences.parquet').replace("\\", "/")
    print(f"      💾 Zielpfad: {parquet_sql_path}")
    
    # SCHRITT A: Labels vorkalkulieren (1 Zeile pro Patient!)
    # Verhindert, dass Events mit JEDER Admission multipliziert werden.
    con.execute("""
        CREATE OR REPLACE TABLE unique_labels AS
        SELECT 
            CAST(subject_id AS BIGINT) as subject_id, 
            MAX(hospital_expire_flag) as label
        FROM raw_admissions
        GROUP BY subject_id
    """)
    
    # SCHRITT B: Der saubere Join
    # Jetzt joinen wir 89 Mio Events mit (nur) ~40k Patienten-Labels.
    # Das Ergebnis bleibt bei 89 Mio Zeilen (keine Explosion mehr!).
    
    # Zuerst prüfen wir die Anzahl der Chunks (nicht Zeilen!)
    chunk_count_query = """
        SELECT count(DISTINCT CAST(s.subject_id AS VARCHAR) || '_' || CAST(s.chunk_id AS VARCHAR))
        FROM stream_integers s
        JOIN unique_labels l ON s.subject_id = l.subject_id
    """
    final_count = con.execute(chunk_count_query).fetchone()[0]
    print(f"      📊 Zu schreibende Chunks (Sequenzen): {final_count}")

    if final_count > 0:
        con.execute(f"""
            COPY (
                SELECT 
                    s.subject_id,
                    s.chunk_id,
                    -- Das Label kommt jetzt aus der eindeutigen Tabelle
                    MAX(l.label) as label,
                    -- Liste der Tokens im Chunk
                    LIST(s.token_id ORDER BY s.t ASC) as token_ids
                FROM stream_integers s
                JOIN unique_labels l ON s.subject_id = l.subject_id
                GROUP BY s.subject_id, s.chunk_id
                ORDER BY s.subject_id, s.chunk_id
            ) TO '{parquet_sql_path}' (FORMAT PARQUET)
        """)
        print("      ✅ Export Befehl erfolgreich gesendet.")
    else:
        print("      ❌ FEHLER: 0 Chunks gefunden. Prüfe Subject-IDs.")

    con.close()
    if db_file.exists(): os.remove(db_file)
    if abs_temp.exists(): shutil.rmtree(abs_temp)

    final_file = abs_output / 'mimic_sequences.parquet'
    if final_file.exists() and final_file.stat().st_size > 0:
        print(f"🚀 FERTIG! Datei erstellt ({final_file.stat().st_size / (1024*1024):.2f} MB).")
    else:
        print("❌ CRITICAL: Datei ist 0 Bytes groß. Export abgebrochen?")

if __name__ == "__main__":
    run_pipeline()