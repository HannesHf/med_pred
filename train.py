import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import hydra
from omegaconf import DictConfig, OmegaConf, open_dict
import os
from pathlib import Path  # Wichtig: Path direkt importieren
import json
import mlflow
import torch

# --- IMPORTS FÜR UNSERE MODULE ---
from src.data.mimic_loader import MimicDataModule
from src.models.rnn_module import DiseasePredictor as RNNPredictor
from src.models.transformer_module import DiseasePredictor as TransformerPredictor

torch.set_float32_matmul_precision('medium')

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    
    # Seed für Reproduzierbarkeit
    pl.seed_everything(cfg.seed)

    # ---------------------------------------------------------
    # 1. PFAD MANAGEMENT
    # ---------------------------------------------------------
    orig_cwd = Path(hydra.utils.get_original_cwd())
    
    # Pfad zu "../ML_DATA" auflösen
    ml_data_path = (orig_cwd / cfg.mlflow.storage_dir).resolve()
    ml_data_path.mkdir(parents=True, exist_ok=True)

    # Unterordner
    artifact_path = ml_data_path / "artifacts"
    artifact_path.mkdir(parents=True, exist_ok=True)
    
    processed_path = ml_data_path / "processed" 

    # MLflow Setup
    db_url = f"sqlite:///{(ml_data_path / 'mlflow.db').as_posix()}"
    
    mlflow.set_tracking_uri(db_url)
    print(f"📂 Daten & Logs liegen in: {ml_data_path}")

    # ---------------------------------------------------------
    # 2. VOKABULAR & CONFIG UPDATE
    # ---------------------------------------------------------
    vocab_file = processed_path / "vocab.json"
    
    if vocab_file.exists():
        with open(vocab_file, "r") as f:
            vocab = json.load(f)
        vocab_size = len(vocab)
        print(f"📖 Vokabular gefunden! Setze input_dim auf {vocab_size}")
        
        with open_dict(cfg):
            cfg.model.input_dim = vocab_size
    else:
        print("⚠️ Kein Vokabular gefunden. Nutze Config input_dim.")

    # ---------------------------------------------------------
    # 3. DATEN LADEN
    # ---------------------------------------------------------
    dm = MimicDataModule(cfg, cache_path=ml_data_path)

    # ---------------------------------------------------------
    # 4. MODELL WAHL
    # ---------------------------------------------------------
    model_name = cfg.model.get("name", "rnn")
    
    if model_name == "transformer_encoder":
        print(f"🤖 Starte Training mit TRANSFORMER (Pooling: {cfg.model.get('pooling', 'mean')})")
        model = TransformerPredictor(cfg)
    else:
        print("🔄 Starte Training mit LSTM/RNN")
        model = RNNPredictor(cfg)

    # ---------------------------------------------------------
    # 5. LOGGER & CALLBACKS
    # ---------------------------------------------------------
    mlf_logger = MLFlowLogger(
        experiment_name=cfg.logger.mlflow.experiment_name,
        run_name=None, # None erzwingt MLflow-Namen (z.B. "dashing-fawn-23")
        tracking_uri=db_url,              # WICHTIG: Nutzung der SQLite DB
        artifact_location=artifact_path.as_posix() # Artefakte im Ordner speichern
    )
    
    print(f"\n🚀 MLflow UI starten mit: uv run mlflow ui --backend-store-uri {db_url}\n")

    # Hyperparameter loggen
    mlf_logger.log_hyperparams(OmegaConf.to_container(cfg, resolve=True))

    checkpoint_callback = ModelCheckpoint(
        monitor="val_auprc",    # Wir optimieren auf AUPRC
        mode="max",             # Je höher, desto besser
        save_top_k=1, 
        dirpath="checkpoints",
        filename="best-model-{epoch:02d}-{val_auprc:.4f}"
    )

    early_stop_callback = EarlyStopping(
        monitor="val_auprc", 
        patience=cfg.training.patience, 
        mode="max"
    )

    trainer = pl.Trainer(
        max_epochs=cfg.training.max_epochs,
        accelerator=cfg.training.get("accelerator", "auto"),
        devices=cfg.training.get("devices", "auto"),
        logger=mlf_logger,
        callbacks=[checkpoint_callback, early_stop_callback],
        log_every_n_steps=10
    )

    # ---------------------------------------------------------
    # 6. TRAINING
    # ---------------------------------------------------------
    try:
        trainer.fit(model, datamodule=dm)
    
    except KeyboardInterrupt:
        print("\n🛑 Training manuell unterbrochen (Strg+C).")
        print("   Versuche trotzdem, das bis dahin beste Modell zu retten...")
    
    finally:
        # ---------------------------------------------------------
        # 7. MODEL REGISTRY & RETTUNG
        # ---------------------------------------------------------
        # Jetzt greifen wir auf genau den Callback zu, der im Trainer lief
        best_path = checkpoint_callback.best_model_path
        
        # Prüfung: Existiert der Pfad und ist er nicht leer?
        if best_path and Path(best_path).exists():
            print(f"\n🏆 Bestes Modell gefunden: {best_path}")
            
            # Wir laden die Gewichte in eine neue Instanz der Klasse
            best_model = model.__class__.load_from_checkpoint(best_path)
            
            print("💾 Lade Modell zu MLflow hoch...")
            
            # Nur registrieren, wenn gewünscht (Default: True). Bei Sweeps auf False setzen!
            reg_name = "MIMIC_Mortality_Predictor" if cfg.get("register_model", True) else None
            
            # Wir müssen sicherstellen, dass wir in denselben Run loggen
            with mlflow.start_run(run_id=mlf_logger.run_id):
                mlflow.pytorch.log_model(
                    pytorch_model=best_model,
                    artifact_path="model",
                    registered_model_name=reg_name
                )
            print(f"✅ Modell erfolgreich registriert! (Run ID: {mlf_logger.run_id})")
        else:
            print("⚠️ Kein Checkpoint gefunden. (Training war zu kurz oder kein val_auprc berechnet)")

        val_auprc = trainer.callback_metrics.get("val_auprc")
        return val_auprc.item() if val_auprc is not None else 0.0

if __name__ == "__main__":
    main()