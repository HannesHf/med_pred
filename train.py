import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import hydra
from omegaconf import DictConfig, OmegaConf
import os

# Imports bleiben gleich
from src.data.mimic_loader import MimicDataModule
from src.models.rnn_module import DiseasePredictor

# Der Hydra Decorator injiziert die YAML-Config als 'cfg'
@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    
    # Optional: Config im Terminal ausgeben zur Kontrolle
    print(OmegaConf.to_yaml(cfg))

    pl.seed_everything(cfg.seed)

    # WICHTIG: Hydra ändert das Working Directory. 
    # Für MLflow lokal müssen wir sicherstellen, dass wir den Pfad kennen.
    # Wir nutzen hier den absoluten Pfad zum ursprünglichen Ordner.
    orig_cwd = hydra.utils.get_original_cwd()
    mlruns_path = os.path.join(orig_cwd, "mlruns")

    # Module initialisieren (wir übergeben die gesamte cfg)
    dm = MimicDataModule(cfg)
    model = DiseasePredictor(cfg)

    mlf_logger = MLFlowLogger(
        experiment_name=cfg.experiment_name,
        tracking_uri=f"file:{mlruns_path}"
    )
    
    # MLflow Parameter loggen (Flattened Dict für Übersichtlichkeit)
    mlf_logger.log_hyperparams(OmegaConf.to_container(cfg, resolve=True))

    checkpoint_callback = ModelCheckpoint(
        monitor="val_loss",
        dirpath="checkpoints",
        filename="mimic-{epoch:02d}-{val_loss:.2f}",
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

    trainer.fit(model, datamodule=dm)

if __name__ == "__main__":
    main()