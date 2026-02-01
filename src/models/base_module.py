# src/models/base_module.py
import torch
import torch.nn as nn
import pytorch_lightning as pl
from pytorch_lightning.loggers import MLFlowLogger
import torchmetrics
import mlflow
import matplotlib.pyplot as plt

class BaseDiseasePredictor(pl.LightningModule):
    """
    Diese Klasse enthält die gesamte Logik für Training, Validierung,
    Metriken und Logging. Die Kind-Klassen müssen nur __init__ (Layer)
    und forward() implementieren.
    """
    def __init__(self, cfg):
        super().__init__()
        self.save_hyperparameters()
        self.cfg = cfg
        
        # Standard Loss für Klassifikation
        self.criterion = nn.CrossEntropyLoss()

        # --- METRIKEN (Zentral definiert) ---
        self.val_auroc = torchmetrics.classification.BinaryAUROC()
        self.val_auprc = torchmetrics.classification.BinaryAveragePrecision()
        self.val_f1 = torchmetrics.classification.BinaryF1Score()
        self.val_acc = torchmetrics.classification.BinaryAccuracy()

        # --- PLOTTING DATA ---
        self.roc_curve = torchmetrics.classification.BinaryROC()
        self.pr_curve = torchmetrics.classification.BinaryPrecisionRecallCurve()
        self.conf_mat = torchmetrics.classification.BinaryConfusionMatrix()

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x) # Ruft forward() der Kind-Klasse auf
        loss = self.criterion(logits, y.long())
        self.log('train_loss', loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        y = y.long()
        loss = self.criterion(logits, y.long())
        
        # Wahrscheinlichkeiten für Klasse 1 (Target/Tod)
        probs = torch.softmax(logits, dim=1)[:, 1]
        preds = torch.argmax(logits, dim=1)

        # Metriken updaten
        self.val_auroc(probs, y)
        self.val_auprc(probs, y)
        self.val_f1(preds, y)
        self.val_acc(preds, y)
        
        # Daten für Plots sammeln
        self.roc_curve(probs, y)
        self.pr_curve(probs, y)
        self.conf_mat(preds, y)
        
        # Logging
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_auroc', self.val_auroc, on_step=False, on_epoch=True, prog_bar=True)
        self.log('val_auprc', self.val_auprc, on_step=False, on_epoch=True, prog_bar=True)
        self.log('val_f1', self.val_f1, on_step=False, on_epoch=True)
        
        return loss

    def on_validation_epoch_end(self):
        mlf_logger = None
        loggers = self.loggers if self.loggers else [self.logger]

        for logger in loggers:
            if isinstance(logger, MLFlowLogger):
                mlf_logger = logger
                break
        if mlf_logger and self.trainer.is_global_zero:
            try:
                client = mlf_logger.experiment
                run_id = mlf_logger.run_id

                # 1. ROC Kurve
                fig_roc, _ = self.roc_curve.plot(score=True)
                fig_roc.suptitle(f"ROC Curve (Epoch {self.current_epoch})")
                client.log_figure(run_id, fig_roc, f"plots/roc_epoch_{self.current_epoch:02d}.png")
                plt.close(fig_roc)

                # 2. PR Kurve
                fig_pr, _ = self.pr_curve.plot(score=True)
                fig_pr.suptitle(f"PR Curve (Epoch {self.current_epoch})")
                client.log_figure(run_id, fig_pr, f"plots/pr_epoch_{self.current_epoch:02d}.png")
                plt.close(fig_pr)

                # 3. Confusion Matrix
                fig_cm, _ = self.conf_mat.plot()
                fig_cm.suptitle(f"Confusion Matrix (Epoch {self.current_epoch})")
                client.log_figure(run_id, fig_cm, f"plots/cm_epoch_{self.current_epoch:02d}.png")
                plt.close(fig_cm)
                
            except Exception as e:
                print(f"⚠️ Plotting Fehler (wird ignoriert): {e}")
            
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.cfg.model.lr)