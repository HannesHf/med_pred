import torch
import pandas as pd
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
import pytorch_lightning as pl

class MimicTokenDataset(Dataset):
    def __init__(self, df, max_len=None):
        self.tokens = df['token_ids'].tolist()
        self.labels = df['label'].tolist()
        self.max_len = max_len 

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, idx):
        tokens = self.tokens[idx]
        label = self.labels[idx]
        
        if self.max_len and len(tokens) > self.max_len:
            tokens = tokens[:self.max_len]
            
        return torch.tensor(tokens, dtype=torch.long), torch.tensor(label, dtype=torch.float32)

def collate_fn(batch):
    tokens_list, labels_list = zip(*batch)
    tokens_padded = pad_sequence(tokens_list, batch_first=True, padding_value=0)
    labels = torch.stack(labels_list)
    return tokens_padded, labels

class MimicDataModule(pl.LightningDataModule):
    def __init__(self, cfg, cache_path=None):
        super().__init__()
        self.cfg = cfg
        
        if cache_path:
            # cache_path ist z.B. C:\Users\...\ML_DATA
            self.data_path = Path(cache_path) / "processed/mimic_sequences.parquet"
        else:
            self.data_path = Path("../ML_DATA/processed/mimic_sequences.parquet")
            
        self.train_df = None
        self.val_df = None

    def setup(self, stage=None):
        if not self.data_path.exists():
            raise FileNotFoundError(f"❌ Datei fehlt: {self.data_path}")

        print(f"📥 Lade Parquet: {self.data_path}")
        full_df = pd.read_parquet(self.data_path, columns=['subject_id', 'token_ids', 'label'])
        
        # Patient-Level Split
        all_subjects = full_df['subject_id'].unique()
        print(f"📊 Gefunden: {len(full_df)} Chunks von {len(all_subjects)} Patienten.")
        
        np.random.seed(self.cfg.seed)
        np.random.shuffle(all_subjects)
        
        split_idx = int(len(all_subjects) * 0.8)
        train_subjects = set(all_subjects[:split_idx])
        val_subjects = set(all_subjects[split_idx:])
        
        print("✂️  Führe Patient-Level Split durch...")
        self.train_df = full_df[full_df['subject_id'].isin(train_subjects)].copy()
        self.val_df = full_df[full_df['subject_id'].isin(val_subjects)].copy()
        
        print(f"   ✅ Train: {len(self.train_df)} Chunks")
        print(f"   ✅ Val:   {len(self.val_df)} Chunks")

    def train_dataloader(self):
        return DataLoader(
            MimicTokenDataset(self.train_df, self.cfg.data.seq_len),
            batch_size=self.cfg.data.batch_size,
            shuffle=True, 
            collate_fn=collate_fn,
            num_workers=4,
            persistent_workers=True,
            pin_memory=True
        )

    def val_dataloader(self):
        return DataLoader(
            MimicTokenDataset(self.val_df, self.cfg.data.seq_len),
            batch_size=self.cfg.data.batch_size,
            shuffle=False, 
            collate_fn=collate_fn,
            num_workers=4,
            persistent_workers=True,
            pin_memory=True
        )