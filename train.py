import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import hydra
from omegaconf import DictConfig, OmegaConf, open_dict
import os
import pathlib
import json

# --- IMPORTS FÜR UNSERE MODULE ---
from src.data.mimic_loader import MimicDataModule
# Wir importieren BEIDE Modelle, um umschalten zu können
from src.models.rnn_module import DiseasePredictor as RNNPredictor
from src.models.transformer_module import DiseasePredictor as TransformerPredictor

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    
    # Optional: Config drucken
    # print(OmegaConf.to_yaml(cfg))

    pl.seed_everything(cfg.seed)

    # ---------------------------------------------------------
    # 1. PFAD MANAGEMENT (ML_DATA außerhalb des Repos)
    # ---------------------------------------------------------
    orig_cwd = pathlib.Path(hydra.utils.get_original_cwd())
    
    # Pfad zu "../ML_DATA" auflösen
    ml_data_path = (orig_cwd / cfg.mlflow.storage_dir).resolve()
    ml_data_path.mkdir(parents=True, exist_ok=True)

    # Unterordner für Artifacts und Processed Data
    artifact_path = ml_data_path / "artifacts"
    artifact_path.mkdir(parents=True, exist_ok=True)
    
    processed_path = ml_data_path / "processed" # Hier liegen Parquet & Vocab

    # MLflow Setup (SQLite ist super stabil lokal!)
    db_url = f"sqlite:///{(ml_data_path / 'mlflow.db').as_posix()}"
    artifact_url = artifact_path.as_uri()

    print(f"📂 Daten & Logs liegen in: {ml_data_path}")

    # ---------------------------------------------------------
    # 2. DYNAMISCHE KONFIGURATION (Vokabular laden)
    # ---------------------------------------------------------
    # Wenn wir echte Daten nutzen (preprocessing lief), laden wir die Vocab-Größe
    vocab_file = processed_path / "vocab.json"
    
    if vocab_file.exists():
        with open(vocab_file, "r") as f:
            vocab = json.load(f)
        vocab_size = len(vocab)
        print(f"📖 Vokabular gefunden! Setze input_dim auf {vocab_size}")
        
        # WICHTIG: Config überschreiben, damit das Embedding die richtige Größe hat
        with open_dict(cfg):
            cfg.model.input_dim = vocab_size
    else:
        print("⚠️ Kein Vokabular gefunden (Mock-Mode?). Nutze Config input_dim.")

    # ---------------------------------------------------------
    # 3. DATEN LADEN
    # ---------------------------------------------------------
    # Wir übergeben den Pfad zu ML_DATA, damit der Loader das Parquet findet
    dm = MimicDataModule(cfg, cache_path=ml_data_path)

    # ---------------------------------------------------------
    # 4. MODELL WAHL (Transformer vs. LSTM)
    # ---------------------------------------------------------
    # Wir schauen in die Config (cfg.model.name), was gewünscht ist
    model_name = cfg.model.get("name", "rnn") # Fallback auf RNN
    
    if model_name == "transformer_encoder":
        print("🤖 Starte Training mit TRANSFORMER")
        model = TransformerPredictor(cfg)
    else:
        print("🔄 Starte Training mit LSTM/RNN")
        model = RNNPredictor(cfg)

    # ---------------------------------------------------------
    # 5. LOGGER & TRAINER SETUP
    # ---------------------------------------------------------
    mlf_logger = MLFlowLogger(
        experiment_name=cfg.experiment_name,
        tracking_uri=db_url,
        artifact_location=artifact_url
    )
    
    print(f"\n🚀 MLflow UI starten mit: mlflow ui --backend-store-uri {db_url}\n")

    mlf_logger.log_hyperparams(OmegaConf.to_container(cfg, resolve=True))

    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        dirpath="checkpoints",
        filename="model-{epoch:02d}-{val_loss:.2f}",
        save_top_k=1,
        mode="min",
    )

    early_stop = EarlyStopping(
        monitor="val_loss", 
        patience=cfg.training.patience, 
        mode="min"
    )

    trainer = pl.Trainer(
        max_epochs=cfg.training.max_epochs,
        logger=mlf_logger,
        callbacks=[checkpoint_callback, early_stop],
        accelerator="auto", 
        devices=1,
        log_every_n_steps=5
    )

    # ---------------------------------------------------------
    # 6. TRAINING STARTEN
    # ---------------------------------------------------------
    trainer.fit(model, datamodule=dm)

    # Return Value für Optuna (Hyperparameter Optimierung)
    val_loss = trainer.callback_metrics.get("val_loss")
    return val_loss.item() if val_loss is not None else 0.0

if __name__ == "__main__":
    main()