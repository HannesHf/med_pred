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
        self.train_ds = None
        self.val_ds = None

    def setup(self, stage=None):
        # Hier später: Laden der echten Daten
        full_dataset = MimicMockDataset(
            num_samples=self.cfg.data.num_samples, 
            seq_len=self.cfg.data.seq_len, 
            input_dim=self.cfg.data.input_dim
        )
        
        train_size = int(0.8 * len(full_dataset))
        val_size = len(full_dataset) - train_size
        self.train_ds, self.val_ds = random_split(
            full_dataset, [train_size, val_size], 
            generator=torch.Generator().manual_seed(self.cfg.seed)
        )

    def train_dataloader(self):
        return DataLoader(
            self.train_ds, 
            batch_size=self.cfg.data.batch_size, 
            shuffle=True, 
            num_workers=0 # 0 für Windows/Mac Safety, auf Linux Server erhöhen
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_ds, 
            batch_size=self.cfg.data.batch_size, 
            num_workers=0
        )