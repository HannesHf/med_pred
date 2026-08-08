import sys
from pathlib import Path
import mlflow # <--- Sicherstellen, dass das importiert ist

# 1. Root Path finden (med_pred)
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

# --- FIX START: MLflow sagen, wo die Datenbank liegt ---
# Wir gehen davon aus, dass ML_DATA parallel zu med_pred liegt
db_path = root_path.parent / "ML_DATA" / "mlflow.db"
db_url = f"sqlite:///{db_path.as_posix()}"

print(f"🔌 Verbinde mit MLflow DB: {db_url}")
mlflow.set_tracking_uri(db_url)
# --- FIX ENDE ---

from src.models.transformer_module import DiseasePredictor as TransformerPredictor
import torch
import mlflow
import mlflow.pytorch
import matplotlib.pyplot as plt
from tqdm import tqdm
from pathlib import Path
import argparse
import torchmetrics

# Wir brauchen die Imports noch, damit Pickle die Klassen findet, 
# auch wenn wir sie nicht direkt instanziieren.
from src.models.rnn_module import DiseasePredictor as RNNPredictor
from src.data.mimic_loader import MimicDataModule


def evaluate_from_registry(model_name="MIMIC_Mortality_Predictor", version="latest", fractions=[0.2, 0.4, 0.6, 0.8, 1.0]):
    
    model_uri = f"models:/{model_name}/{version}"
    print(f"☁️ Lade Modell aus Registry: {model_uri}")
    
    try:
        model = mlflow.pytorch.load_model(model_uri)
    except Exception as e:
        print(f"❌ Fehler beim Laden: {e}")
        print("Tipp: Hast du 'train.py' schon einmal mit dem neuen Registry-Code ausgeführt?")
        return

    model.eval()
    if torch.cuda.is_available():
        model.cuda()
        print("🚀 Modell auf GPU geladen.")

    # 2. Daten laden
    # Der Clou: Das geladene MLflow-Modell hat die Config (self.cfg) noch gespeichert!
    print("📂 Rekonstruiere DataModule aus gespeicherter Config...")
    cfg = model.cfg 
    
    # Pfad-Fix (falls du auf einem anderen PC bist, sonst optional)
    # cfg.mlflow.storage_dir = "../ML_DATA"
    
    dm = MimicDataModule(cfg, cache_path=Path(cfg.mlflow.storage_dir).resolve())
    dm.setup()
    val_loader = dm.val_dataloader()

    # 3. Evaluation Loop (wie vorher)
    auroc_metric = torchmetrics.classification.BinaryAUROC().to(model.device)
    results = {}

    print(f"🔬 Starte Early Warning Analyse...")
    
    for frac in fractions:
        all_probs = []
        all_targets = []
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc=f"Sicht {int(frac*100)}%", leave=False):
                x, y = batch
                x = x.to(model.device)
                y = y.to(model.device).long()
                
                # Truncation
                seq_len = x.shape[1]
                cutoff = int(seq_len * frac)
                if cutoff < 1: cutoff = 1
                
                x_truncated = x[:, :cutoff]
                
                logits = model(x_truncated)
                probs = torch.softmax(logits, dim=1)[:, 1]
                
                all_probs.append(probs)
                all_targets.append(y)
        
        score = auroc_metric(torch.cat(all_probs), torch.cat(all_targets)).item()
        results[frac] = score
        print(f"   -> {int(frac*100)}% Sicht: AUROC {score:.4f}")

    return results

def plot_results(results):
    x = [k * 100 for k in results.keys()]
    y = list(results.values())
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='purple', linewidth=2)
    plt.title("Early Warning Performance (Loaded from MLflow)", fontsize=14)
    plt.xlabel("Percentage of Stay Observed (%)")
    plt.ylabel("AUROC")
    plt.grid(True, alpha=0.3)
    plt.ylim(0.5, 1.0)
    plt.savefig("early_warning_mlflow.png")
    print("\n✅ Plot gespeichert als 'early_warning_mlflow.png'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", type=str, default="Latest", help="Modell Version (z.B. '1', '2' oder 'Latest'/'Production')")
    args = parser.parse_args()

    results = evaluate_from_registry(version=args.version)
    if results:
        plot_results(results)