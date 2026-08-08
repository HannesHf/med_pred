# src/data/mimic_loader.py
import torch
from torch.utils.data import Dataset, DataLoader, random_split
import pytorch_lightning as pl

class MimicMockDataset(Dataset):
    """
    Simuliert MIMIC-III Daten für Prototyping.
    """
    def __init__(self, num_samples=1000, seq_len=50, input_dim=20):
        self.num_samples = num_samples
        # Simuliere Features: (Samples, Time, Features)
        self.data = torch.randn(num_samples, seq_len, input_dim)
        
        # Simuliere Labels: Logic -> Wenn letzter Zeitschritt pos. Mittelwert hat = 1
        last_step_mean = self.data[:, -1, :].mean(dim=1)
        self.labels = (last_step_mean > 0).long()

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

class MimicDataModule(pl.LightningDataModule):
    def __init__(self, config):
        super().__init__()
        self.cfg = config

    def setup(self, stage=None):
        data_cfg = getattr(self.cfg, 'data', self.cfg)
        seq_len = getattr(data_cfg, 'seq_len', data_cfg.get('seq_len', 50) if isinstance(data_cfg, dict) else 50)
        input_dim = getattr(data_cfg, 'input_dim', data_cfg.get('input_dim', 20) if isinstance(data_cfg, dict) else 20)
        seed = getattr(self.cfg, 'seed', self.cfg.get('seed', 42) if isinstance(self.cfg, dict) else 42)

        full_dataset = MimicMockDataset(
            num_samples=500, 
            seq_len=seq_len, 
            input_dim=input_dim
        )
        
        train_size = int(0.8 * len(full_dataset))
        val_size = len(full_dataset) - train_size
        self.train_ds, self.val_ds = random_split(
            full_dataset, [train_size, val_size], 
            generator=torch.Generator().manual_seed(seed)
        )

    def train_dataloader(self):
        data_cfg = getattr(self.cfg, 'data', self.cfg)
        batch_size = getattr(data_cfg, 'batch_size', data_cfg.get('batch_size', 16) if isinstance(data_cfg, dict) else 16)
        num_workers = getattr(data_cfg, 'num_workers', data_cfg.get('num_workers', 0) if isinstance(data_cfg, dict) else 0)
        return DataLoader(
            self.train_ds, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=num_workers
        )

    def val_dataloader(self):
        data_cfg = getattr(self.cfg, 'data', self.cfg)
        batch_size = getattr(data_cfg, 'batch_size', data_cfg.get('batch_size', 16) if isinstance(data_cfg, dict) else 16)
        num_workers = getattr(data_cfg, 'num_workers', data_cfg.get('num_workers', 0) if isinstance(data_cfg, dict) else 0)
        return DataLoader(
            self.val_ds, 
            batch_size=batch_size, 
            num_workers=num_workers
        )