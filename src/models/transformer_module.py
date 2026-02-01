# src/models/transformer_module.py
import torch
import torch.nn as nn
import math
from src.models.base_module import BaseDiseasePredictor

class PositionalEncoding(nn.Module):
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
        x = x + self.pe[:, :x.size(1), :]
        return x

class DiseasePredictor(BaseDiseasePredictor):
    def __init__(self, cfg):
        # 1. Basis-Klasse initialisieren
        super().__init__(cfg)
        
        # 2. Architektur bauen
        self.embedding = nn.Embedding(cfg.model.input_dim, cfg.model.d_model, padding_idx=0)
        self.pos_encoder = PositionalEncoding(cfg.model.d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=cfg.model.d_model,
            nhead=cfg.model.nhead,
            dim_feedforward=cfg.model.dim_feedforward,
            dropout=cfg.model.dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=cfg.model.num_layers)
        
        self.fc = nn.Linear(cfg.model.d_model, cfg.model.num_classes)
        
        # Logging, welche Strategie genutzt wird
        print(f"🔧 Model initialized with Pooling Strategy: {cfg.model.pooling.upper()}")

    def forward(self, x):
        # x: [Batch, SeqLen]
        src_key_padding_mask = (x == 0)
        
        # Embedding & PosEncoding
        x = self.embedding(x) * math.sqrt(self.cfg.model.d_model)
        x = self.pos_encoder(x)
        
        # Transformer Pass
        # x shape: [Batch, SeqLen, D_Model]
        x = self.transformer_encoder(x, src_key_padding_mask=src_key_padding_mask)
        
        # --- POOLING STRATEGIE (Der entscheidende Teil) ---
        pooling_type = self.cfg.model.get("pooling", "mean") # Fallback auf Mean
        
        if pooling_type == "max":
            # Max-Pooling: Sucht das stärkste Signal in der gesamten Sequenz
            # Wir nehmen das Max über Dimension 1 (Zeit)
            # x.max(dim=1) gibt (values, indices) zurück, wir brauchen nur values
            x, _ = x.max(dim=1)
            
        elif pooling_type == "mean":
            # Mean-Pooling: Der Durchschnitt (verwässert oft Signale)
            # Um es sauber zu machen, sollten wir Padding nicht mitzählen,
            # aber einfaches Mean ist Standard und oft gut genug.
            x = x.mean(dim=1)
            
        else:
            raise ValueError(f"Unbekannte Pooling Strategie: {pooling_type}")
        
        # Classification Head
        logits = self.fc(x)
        return logits