import torch
import pytorch_lightning as pl
from omegaconf import OmegaConf
import time
import sys
import os

# Imports aus dem src Ordner
from src.models.rnn_module import DiseasePredictor
from src.data.mimic_loader import MimicDataModule

def run_gpu_poc():
    print("="*50)
    print("   GPU TRAINING POC TEST (Proof of Concept)")
    print("="*50)

    # 1. Hardware Check
    if not torch.cuda.is_available():
        print("❌ FEHLER: Kein CUDA-fähiges Gerät gefunden.")
        print("   Bitte Nvidia-Treiber prüfen oder PyTorch mit CUDA installieren.")
        print("   Test wird abgebrochen.")
        return
    
    device_name = torch.cuda.get_device_name(0)
    print(f"✅ GPU erkannt: {device_name}")
    print(f"   CUDA Version: {torch.version.cuda}")

    # 2. Mock Configuration (Simuliert die Hydra Config Struktur)
    # Wir bauen hier manuell das Config-Objekt nach, das sonst aus der YAML kommt.
    conf_data = {
        "seed": 42,
        "experiment_name": "gpu_poc_test",
        "data": {
            "seq_len": 50,
            "input_dim": 20,
            "batch_size": 64,
            "num_samples": 1000,
            "num_samples": 10000
            },
        "model": {
            "hidden_dim": 128,
            "num_layers": 2,
            "dropout": 0.1,
            "num_classes": 2,
            "lr": 0.001
        },
        "training": {
            "max_epochs": 1,
            "patience": 1
        }
        }
    cfg = OmegaConf.create(conf_data)

    # 3. Module initialisieren
    print("\nInitialisiere DataModule und Model...")
    dm = MimicDataModule(cfg)
    model = DiseasePredictor(cfg)

    # 4. Trainer Setup für GPU
    # fast_dev_run=True: Lässt nur 1 Batch durchlaufen (Train/Val) um Fehler zu finden
    print("\nStarte Lightning Trainer (Modus: fast_dev_run)...")
    trainer = pl.Trainer(
        accelerator="gpu",
        devices=1,
        fast_dev_run=True,  # Wichtig: Kein echtes Training, nur Funktionstest
        enable_checkpointing=False,
        logger=False
    )

    # 5. Ausführung
    try:
        start = time.time()
        trainer.fit(model, datamodule=dm)
        print(f"\n✅ SUCCESS: GPU-Durchlauf erfolgreich in {time.time() - start:.2f}s!")
    except Exception as e:
        print(f"\n❌ FEHLER während des GPU-Tests: {e}")

if __name__ == "__main__":
    run_gpu_poc()