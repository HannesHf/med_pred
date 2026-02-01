import torch
import torch.nn as nn
import pytorch_lightning as pl
import math

class PositionalEncoding(nn.Module):
    """
    Fügt Information über die Position im Satz hinzu (da Transformer keine Reihenfolge kennen).
    """
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x: [Batch, Seq_Len, d_model]
        # Wir addieren das Positions-Signal zum Embedding
        x = x + self.pe[:, :x.size(1), :]
        return x

class DiseasePredictor(pl.LightningModule):
    def __init__(self, cfg):
        super().__init__()
        self.save_hyperparameters()
        self.cfg = cfg
        
        # 1. Embedding Layer
        # Wandelt Token-IDs (Integer) in Vektoren um. 
        # padding_idx=0 sorgt dafür, dass das Padding (0) immer der Nullvektor bleibt.
        self.embedding = nn.Embedding(cfg.model.input_dim, cfg.model.d_model, padding_idx=0)
        
        # 2. Positional Encoding
        self.pos_encoder = PositionalEncoding(cfg.model.d_model)
        
        # 3. Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=cfg.model.d_model,
            nhead=cfg.model.nhead,
            dim_feedforward=cfg.model.dim_feedforward,
            dropout=cfg.model.dropout,
            batch_first=True  # WICHTIG: Unsere Daten sind [Batch, Seq, Feature]
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=cfg.model.num_layers)
        
        # 4. Classification Head
        # Ein einfaches lineares Layer am Ende für die Entscheidung (Tot/Lebendig)
        self.fc = nn.Linear(cfg.model.d_model, cfg.model.num_classes)
        
        # Loss Funktion für Klassifikation
        self.criterion = nn.CrossEntropyLoss()

    def forward(self, x):
        # x: [Batch, Seq_Len]
        
        # Maske erstellen: Wo ist Padding (0)?
        # True = Position ignorieren (Padding), False = Echtes Token
        src_key_padding_mask = (x == 0)

        # Embedding & Position
        x = self.embedding(x) * math.sqrt(self.cfg.model.d_model)
        x = self.pos_encoder(x)
        
        # Transformer Pass
        # output: [Batch, Seq_Len, d_model]
        x = self.transformer_encoder(x, src_key_padding_mask=src_key_padding_mask)
        
        # Pooling Strategie: Mean Pooling
        # Wir nehmen den Durchschnitt aller Token-Vektoren, ignorieren aber das Padding.
        # (Hier vereinfacht: Durchschnitt über alle, da Padding-Vektoren oft klein/null sind oder Masking hilft)
        x = x.mean(dim=1) 
        
        # Klassifikation
        logits = self.fc(x)
        return logits

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        # y muss für CrossEntropy 'long' (Integer) sein
        loss = self.criterion(logits, y.long())
        
        self.log('train_loss', loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y.long())
        
        # Accuracy berechnen
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        self.log('val_loss', loss, prog_bar=True)
        self.log('val_acc', acc, prog_bar=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.cfg.model.lr)