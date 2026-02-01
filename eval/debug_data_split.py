import torch
import numpy as np
from pathlib import Path
from omegaconf import OmegaConf
import sys
import pytorch_lightning as pl

# --- PFAD FIX ---
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from src.data.mimic_loader import MimicDataModule

def check_for_leakage():
    print(f"🕵️‍♂️ Starte Data Leakage Untersuchung aus: {Path(__file__).parent}")
    print(f"   Projekt-Root erkannt als: {root_path}")
    
    # 1. Config laden
    config_path = root_path / "conf" / "config.yaml"
    if not config_path.exists():
        print(f"❌ Fehler: Config nicht gefunden unter {config_path}")
        return
    
    cfg = OmegaConf.load(config_path)

    # 2. Seed setzen
    seed = cfg.get("seed", 42)
    pl.seed_everything(seed, workers=True)
    print(f"🌱 Seed gesetzt auf: {seed}")

    # 3. DataModule Setup
    if "storage_dir" in cfg.mlflow:
        cache_dir = Path(cfg.mlflow.storage_dir).resolve()
    else:
        cache_dir = root_path.parent / "ML_DATA"
    
    print(f"📂 Nutze Cache Verzeichnis: {cache_dir}")
    dm = MimicDataModule(cfg, cache_path=cache_dir)
    
    print("⏳ Führe dm.setup() aus...")
    dm.setup(stage="fit")

    # --- ÄNDERUNG: Wir holen die Datasets über die Loader ---
    print("🔍 Extrahiere Datasets über Dataloaders...")
    try:
        # Wir rufen die Dataloader ab, um an das Dataset-Objekt zu kommen
        train_loader = dm.train_dataloader()
        val_loader = dm.val_dataloader()
        
        train_subset = train_loader.dataset
        val_subset = val_loader.dataset
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Dataloader: {e}")
        return

    # 4. IDs rekonstruieren
    print("📊 Analysiere Indizes und Metadaten...")
    
    try:
        # Wir müssen an das "Mutter-Dataset" kommen, das die Metadaten hält.
        # Bei einem RandomSplit ist 'dataset' ein Subset, und 'dataset.dataset' ist das Original.
        if hasattr(train_subset, 'dataset'):
            full_ds = train_subset.dataset
            train_indices = train_subset.indices
            val_indices = val_subset.indices
        else:
            # Falls kein Subset genutzt wurde (unwahrscheinlich bei Split), nehmen wir an es ist direkt das DS
            full_ds = train_subset
            # Wenn wir keine Indizes haben, können wir Leakage schwer prüfen, 
            # außer das DS hat eigene IDs gespeichert.
            train_indices = range(len(train_subset)) 
            # Das wäre hier aber untypisch. Wir gehen vom Standard Subset aus.

        # Jetzt greifen wir auf die Metadaten zu ('chunks_metadata')
        if hasattr(full_ds, 'chunks_metadata'):
            print("   ✅ 'chunks_metadata' gefunden. Extrahiere Patient IDs...")
            
            # Wir holen die subject_id Spalte für die entsprechenden Indizes
            # Annahme: chunks_metadata ist ein Pandas DataFrame
            meta = full_ds.chunks_metadata
            
            train_pids = set(meta.iloc[train_indices]['subject_id'].unique())
            val_pids = set(meta.iloc[val_indices]['subject_id'].unique())
            
        else:
            print("❌ 'chunks_metadata' nicht im Dataset gefunden. Kann IDs nicht prüfen.")
            print(f"   Verfügbare Attribute im Dataset: {dir(full_ds)}")
            return

    except Exception as e:
        print(f"❌ Fehler bei der ID-Extraktion: {e}")
        return

    print(f"\n📊 Statistik:")
    print(f"   Patienten im TRAIN Set: {len(train_pids)}")
    print(f"   Patienten im VAL Set:   {len(val_pids)}")

    # 5. Der Leakage-Test
    overlap = train_pids.intersection(val_pids)
    
    if len(overlap) > 0:
        print("\n🚨🚨🚨 CRITICAL: DATA LEAKAGE GEFUNDEN! 🚨🚨🚨")
        print(f"   -> {len(overlap)} Patienten sind in BEIDEN Sets!")
        print(f"   -> Beispiel-IDs: {list(overlap)[:5]}")
        print("   Das Modell lernt diese Patienten auswendig!")
    else:
        print("\n✅✅✅ CLEAN SPLIT CONFIRMED ✅✅✅")
        print("   Es gibt KEINE Überlappung von Patienten zwischen Train und Val.")
        print("   Die Performance von 0.93 AUROC ist technisch echt.")

if __name__ == "__main__":
    check_for_leakage()