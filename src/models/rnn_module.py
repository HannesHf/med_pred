import torch
import torch.nn as nn
import pytorch_lightning as pl
from omegaconf import DictConfig

class DiseasePredictor(pl.LightningModule):
    def __init__(self, cfg: DictConfig):
        super().__init__()
        self.save_hyperparameters(cfg) # Loggt alles sauber
        self.cfg = cfg
        
        self.lstm = nn.LSTM(
            input_size=cfg.data.input_dim,     # Beachte die Punkt-Notation!
            hidden_size=cfg.model.hidden_dim,
            num_layers=cfg.model.num_layers,
            batch_first=True,
            dropout=cfg.model.dropout
        )
        
        self.classifier = nn.Linear(cfg.model.hidden_dim, cfg.model.num_classes)
        self.loss_fn = nn.CrossEntropyLoss()

    def forward(self, x):
        # x: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)
        
        # Nimm den letzten Zeitschritt (Many-to-One)
        last_time_step = lstm_out[:, -1, :]
        logits = self.classifier(last_time_step)
        return logits

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self.forward(x)
        loss = self.loss_fn(logits, y)
        
        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self.forward(x)
        loss = self.loss_fn(logits, y)
        
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_acc", acc, prog_bar=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.cfg.model.lr)