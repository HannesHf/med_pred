import sys
from pathlib import Path
import mlflow
import mlflow.pytorch
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import subprocess

# --- PFAD SETUP ---
# Damit wir 'src' finden, auch wenn wir aus 'deploy' starten
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

# --- MLFLOW SETUP ---
# Wir nutzen dieselbe Logik wie in deinen Eval-Skripten
db_path = root_path.parent / "ML_DATA" / "mlflow.db"
db_url = f"sqlite:///{db_path.as_posix()}"
mlflow.set_tracking_uri(db_url)

app = FastAPI(title="MIMIC Mortality Predictor API")

# Globaler Modell-Speicher
model = None
model_meta = {}

class PatientSequence(BaseModel):
    token_ids: List[int]

@app.on_event("startup")
def load_model():
    global model, model_meta
    model_name = "MIMIC_Mortality_Predictor"
    # Wir laden die neueste Version aus der Production oder Staging Stage
    # Falls du keine Stages nutzt, nehmen wir "latest" via None
    model_uri = f"models:/{model_name}/latest"
    
    # Bestimme Device für das Laden (wichtig für Docker ohne GPU)
    map_loc = "cuda" if torch.cuda.is_available() else "cpu"

    # --- FIX: Datenbank Schema Update ---
    print("🔧 Prüfe und aktualisiere MLflow Datenbank-Schema...")
    try:
        subprocess.run(["mlflow", "db", "upgrade", db_url], check=True)
    except Exception as e:
        print(f"⚠️ DB-Upgrade Warnung (meist harmlos): {e}")

    print(f"🔌 Lade Modell von: {model_uri}")
    try:
        model = mlflow.pytorch.load_model(model_uri, map_location=map_loc)
        model_meta = {"source": "Standard URI", "uri": model_uri}
    except Exception as e:
        print(f"⚠️ Standard-Laden fehlgeschlagen ({e}).")
        print("   -> Versuche Fallback für Docker (Windows-Pfad Fix)...")
        
        try:
            client = mlflow.tracking.MlflowClient(tracking_uri=db_url)
            versions = client.search_model_versions(f"name='{model_name}'")
            
            if not versions:
                raise RuntimeError(f"Kein Modell mit Namen '{model_name}' in der Registry gefunden.")
            
            # Sortieren: Neueste Version zuerst
            versions.sort(key=lambda x: int(x.version), reverse=True)
            
            found_path = None
            
            # Wir iterieren durch Versionen, falls die neueste kaputt ist (z.B. leere Artefakte)
            for v in versions:
                run_id = v.run_id
                
                # FIX: Überspringe Versionen ohne Run ID (kaputte Registry-Einträge)
                if not run_id:
                    print(f"   ⚠️ Version {v.version} hat keine Run ID. Überspringe.")
                    continue

                print(f"🔎 Prüfe Version {v.version} (Run {run_id})...")
                
                try:
                    run = client.get_run(run_id)
                    experiment_id = run.info.experiment_id
                except Exception as e:
                    print(f"   ⚠️ Konnte Run-Infos nicht laden: {e}. Überspringe.")
                    continue
                
                search_roots = [
                    Path("/ML_DATA/artifacts") / run_id,
                    Path("/ML_DATA/artifacts") / experiment_id / run_id,
                ]
                
                for root in search_roots:
                    if root.exists():
                        matches = list(root.rglob("MLmodel"))
                        if matches:
                            found_path = matches[0].parent
                            print(f"   ✅ Artefakte gefunden: {found_path}")
                            break
                
                if found_path:
                    try:
                        model = mlflow.pytorch.load_model(found_path.as_posix(), map_location=map_loc)
                        model_meta = {"source": "Registry Fallback", "version": v.version, "run_id": run_id}
                        print(f"✅ Modell Version {v.version} erfolgreich geladen!")
                        break
                    except Exception as load_e:
                        print(f"   ❌ Laden fehlgeschlagen: {load_e}")
                        found_path = None # Weiter zur nächsten Version
                else:
                    print(f"   ❌ Keine Artefakte für Version {v.version} gefunden.")
                    # Debugging für die allerneueste Version, damit man sieht was los ist
                    if v == versions[0]:
                        for r in search_roots:
                            if r.exists():
                                print(f"      Inhalt {r.name}: {[x.name for x in r.iterdir()]}")
                                if (r / "artifacts").exists():
                                    print(f"      Inhalt artifacts: {[x.name for x in (r / 'artifacts').iterdir()]}")

            # --- NEU: Last Resort (Notfall-Suche auf Festplatte) ---
            if model is None:
                print("⚠️ Registry-Fallback erfolglos. Starte 'Last Resort' Suche im Dateisystem...")
                artifact_root = Path("/ML_DATA/artifacts")
                
                if artifact_root.exists():
                    # Suche rekursiv nach ALLEN 'MLmodel' Dateien
                    candidates = list(artifact_root.rglob("MLmodel"))
                    
                    if candidates:
                        # Sortiere nach Änderungsdatum (neueste zuerst)
                        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                        
                        print(f"🔎 Habe {len(candidates)} potenzielle Modelle auf der Festplatte gefunden.")
                        
                        for cand in candidates:
                            model_path = cand.parent
                            print(f"   Prüfe Kandidat: {model_path}")
                            try:
                                model = mlflow.pytorch.load_model(model_path.as_posix(), map_location=map_loc)
                                
                                # Versuche Run ID aus Pfad zu extrahieren (32 Zeichen Hex)
                                run_id_guess = None
                                for part in model_path.parts:
                                    if len(part) == 32 and all(c in "0123456789abcdef" for c in part):
                                        run_id_guess = part
                                        break
                                
                                model_meta = {"source": "Last Resort (Disk)", "path": model_path.as_posix()}
                                if run_id_guess: model_meta["run_id"] = run_id_guess
                                print(f"✅ Modell erfolgreich geladen (Last Resort)!")
                                break
                            except Exception as e:
                                print(f"   ❌ Laden fehlgeschlagen: {e}")

            if model is None:
                raise RuntimeError("Keine ladbare Modell-Version gefunden.")
            
        except Exception as e2:
            print(f"❌ Auch Fallback gescheitert: {e2}")
            raise RuntimeError("Modell konnte nicht geladen werden.")

    # --- METADATEN ANREICHERN (Run Name holen) ---
    if model is not None and "run_id" in model_meta:
        try:
            client = mlflow.tracking.MlflowClient(tracking_uri=db_url)
            run = client.get_run(model_meta["run_id"])
            model_meta["run_name"] = run.info.run_name
            print(f"   🏷️  Run Name identifiziert: {model_meta['run_name']}")
        except Exception as e:
            print(f"   ⚠️ Konnte Run-Namen nicht laden: {e}")

    model.eval()
    if torch.cuda.is_available():
        model.cuda()

@app.post("/predict")
def predict_risk(data: PatientSequence):
    if model is None:
        raise HTTPException(status_code=503, detail="Modell nicht geladen")
    
    try:
        # Daten vorbereiten
        # Modell erwartet: [Batch_Size, Seq_Len]
        input_tensor = torch.tensor([data.token_ids], dtype=torch.long)
        
        if torch.cuda.is_available():
            input_tensor = input_tensor.cuda()
            
        with torch.no_grad():
            logits = model(input_tensor)
            # Wahrscheinlichkeit für Klasse 1 (Tod)
            prob = torch.softmax(logits, dim=1)[:, 1].item()
            
        return {
            "mortality_risk": prob,
            "seq_len": len(data.token_ids),
            "model_info": model_meta
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Startet den Server lokal
    uvicorn.run(app, host="0.0.0.0", port=8000)
