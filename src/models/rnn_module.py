import torch
import torch.nn as nn
from src.models.base_module import BaseDiseasePredictor

class DiseasePredictor(BaseDiseasePredictor):
    def __init__(self, cfg):
        super().__init__(cfg)
        
        self.embedding = nn.Embedding(cfg.model.input_dim, cfg.model.hidden_dim, padding_idx=0)
        
        self.rnn = nn.LSTM(
            input_size=cfg.model.hidden_dim,
            hidden_size=cfg.model.hidden_dim,
            num_layers=cfg.model.num_layers,
            batch_first=True,
            dropout=cfg.model.dropout if cfg.model.num_layers > 1 else 0
        )
        
        self.fc = nn.Linear(cfg.model.hidden_dim, cfg.model.num_classes)

    def forward(self, x):
        embedded = self.embedding(x)
        
        output, (hidden, cell) = self.rnn(embedded)
        
        last_hidden = hidden[-1]
        
        logits = self.fc(last_hidden)
        return logits