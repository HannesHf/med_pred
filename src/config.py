# src/config.py

CONFIG = {
    # Data Params
    "seq_len": 50,          # Zeitliche Tiefe (z.B. Stunden)
    "input_dim": 20,        # Anzahl Features
    "num_classes": 2,       # Binäre Klassifikation
    
    # Model Params
    "hidden_dim": 64,
    "num_layers": 2,
    "dropout": 0.1,
    
    # Training Params
    "batch_size": 16,       # Klein für Laptop-CPU
    "lr": 1e-3,
    "max_epochs": 5,
    "experiment_name": "MIMIC_Modular_Prototype",
    "seed": 42
}