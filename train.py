import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import hydra
from omegaconf import DictConfig, OmegaConf
import os

from src.data.mimic_loader import MimicDataModule
from src.models.rnn_module import DiseasePredictor as RNNPredictor
from src.models.transformer_module import DiseasePredictor as TransformerPredictor

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))

    pl.seed_everything(cfg.seed)

    orig_cwd = hydra.utils.get_original_cwd()
    mlruns_path = os.path.join(orig_cwd, "mlruns")

    dm = MimicDataModule(cfg)

    model_name = getattr(cfg.model, 'name', 'lstm_baseline')
    if model_name == "transformer_encoder":
        print("🤖 Lade Transformer Modell...")
        model = TransformerPredictor(cfg)
    else:
        print("🔄 Lade LSTM Modell...")
        model = RNNPredictor(cfg)

    mlf_logger = MLFlowLogger(
        experiment_name=cfg.experiment_name,
        tracking_uri=f"file:{mlruns_path}"
    )
    
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