# 🏥 med_pred — Repository Analysis

## Was das Projekt macht

`med_pred` ist eine **ML-Pipeline zur Vorhersage von Krankheitsverläufen**
(Sepsis, Mortalität) aus sequentiellen Patientendaten des
[MIMIC-III ICU-Datensatzes](https://physionet.org/content/mimiciii/1.4/).
Das Problem wird als binäre Zeitreihen-Klassifikation modelliert:
gegeben eine Sequenz von Vitalzeichen und Labor-Werten über Zeit,
soll das Modell vorhersagen ob ein Patient z.B. die Intensivstation
überlebt.

Das Projekt ist explizit als **MLOps-Architektur-Demo** konzipiert —
es läuft lokal auf CPU mit synthetischen Mock-Daten und ist so strukturiert,
dass es auf GPU-Cluster mit echten Daten skalieren kann.

> **Aktueller Reifegrad:** Prototyp mit funktionierendem LSTM-Training
> auf Mock-Daten. Echter Datenzugang, klinische Metriken und Deployment
> sind als Erweiterungen angelegt, aber noch nicht implementiert.

---

## Architektur-Überblick

```
med_pred/
├── conf/                   Hydra-Konfigurationsbaum
│   ├── config.yaml         Haupt-Entry-Point (Defaults, Seed)
│   ├── data/               Datensatz-Parameter
│   ├── model/              Modell-Hyperparameter (LSTM / Transformer)
│   └── training/           Trainer-Settings
├── src/
│   ├── data/
│   │   └── mimic_loader.py LightningDataModule + Mock-Datengenerator
│   └── models/
│       └── rnn_module.py   LSTM LightningModule
├── train.py                Hydra-dekorierter Trainings-Einstiegspunkt
└── pyproject.toml          uv-Dependency-Management
```

**Datenfluss:**
```
Hydra YAML → MimicDataModule (Mock-Tensoren) → DiseasePredictor (LSTM)
→ pl.Trainer → MLFlowLogger + ModelCheckpoint + EarlyStopping
```

---

## Tech Stack

| Tool | Version | Zweck |
|---|---|---|
| Python | 3.11 | Laufzeit |
| PyTorch | ≥ 2.9 | Deep-Learning-Framework |
| PyTorch Lightning | ≥ 2.6 | Strukturierter Training-Loop |
| Hydra | ≥ 1.3 | Hierarchisches Config-Management |
| MLflow | ≥ 3.7 | Experiment Tracking |
| uv | — | Dependency Management |

---

## ✅ Gute Entscheidungen

### 1. Hydra — Separation of Config and Code
Der Konfig-Baum unter `conf/` ist sauber in drei orthogonale Dimensionen
aufgeteilt: **Daten**, **Modell**, **Training**. Das Wechseln eines Modells
oder Datensatzes erfordert keinen Code-Eingriff, nur eine CLI-Flag:

```bash
python train.py model=transformer data=mimic_real
```

Das ist genau das Muster, das in Production-ML-Systemen Standard ist.

### 2. PyTorch Lightning — Strukturiertes Training
Die Verwendung von `pl.LightningModule` erzwingt eine klare Trennung:
Modell-Logik in `forward()`, Trainings-Logik in `training_step()`,
Optimizer in `configure_optimizers()`. Der Aufruf `save_hyperparameters(cfg)`
persistiert die gesamte Konfiguration automatisch im Checkpoint —
damit ist jede gespeicherte Gewichtsdatei vollständig reproduzierbar.

### 3. MLflow-Integration von Anfang an
`MLFlowLogger` ist in `train.py` fest verdrahtet. Besonders gut:
```python
mlf_logger.log_hyperparams(OmegaConf.to_container(cfg, resolve=True))
```
Das loggt die vollständig aufgelöste Hydra-Config (inkl. aller Defaults)
als flaches Dict zu MLflow — so ist jeder Run vollständig nachvollziehbar.

### 4. EarlyStopping + ModelCheckpoint
Beide Callbacks sind korrekt konfiguriert:
- `ModelCheckpoint` speichert **nur das beste Modell** (`save_top_k=1`)
  mit beschreibendem Dateinamen (`mimic-{epoch:02d}-{val_loss:.2f}.ckpt`)
- `EarlyStopping` mit konfigurierbarer Patience verhindert Overfitting
  ohne manuelle Überwachung

### 5. `accelerator="auto"` im Trainer
Der Trainer erkennt GPU/MPS/CPU automatisch — derselbe Code läuft
auf dem Laptop und auf einem GPU-Cluster ohne Anpassung.

### 6. Seeded Train/Val-Split
```python
generator=torch.Generator().manual_seed(self.cfg['seed'])
```
Der Split ist deterministisch und an den Experiment-Seed gebunden.
Das wird häufig vergessen und führt sonst zu nicht reproduzierbaren
Val-Scores.

### 7. uv als Package-Manager
`uv` ist deutlich schneller und zuverlässiger als pip. Der Einsatz
von `pyproject.toml` als einzige Wahrheitsquelle für Dependencies
ist moderner Best Practice.

---

## ⚠️ Code-Bugs (unabhängig vom Merge)

### 🔴 Fataler Config-Interface-Mismatch

`train.py` übergibt das **vollständige hierarchische Hydra-DictConfig** an
`MimicDataModule`:
```python
dm = MimicDataModule(cfg)   # cfg = {data: {seq_len: 50, ...}, model: {...}, ...}
```

`MimicDataModule.setup()` greift aber wie auf ein **flaches Dict** zu:
```python
# mimic_loader.py
seq_len=self.cfg['seq_len'],    # KeyError — liegt unter cfg.data.seq_len
input_dim=self.cfg['input_dim'] # KeyError
batch_size=self.cfg['batch_size']
```

Der Trainer crasht bei jedem Start. Fix:
```python
# Option A — Zugriff korrigieren (empfohlen)
seq_len=self.cfg.data.seq_len
input_dim=self.cfg.data.input_dim
batch_size=self.cfg.data.batch_size

# Option B — nur den data-Teil übergeben
dm = MimicDataModule(cfg.data)
```

### 🟡 `src/config.py` — totes Code

Dieses Modul definiert ein hardcodiertes Python-Dict mit denselben
Werten wie die Hydra-YAMLs. Es wird nirgends importiert und ist ein
Überbleibsel aus einer Pre-Hydra-Entwicklungsphase. Sollte gelöscht werden.

### 🟡 Kein Test-Set

Die Datenteilung ist nur Train/Val (80/20). Für ein medizinisches
Vorhersagemodell ist ein sauberes, **niemals für Early-Stopping
genutztes** Test-Set zwingend — sonst ist der reportierte Score optimistisch.

---

## 🚧 Fehlende Features & Potenzial

### 1. Echter MIMIC-III Daten-Loader *(High Priority)*
`conf/data/mimic_real.yaml` existiert, ist aber leer. Es fehlt komplett:
- Laden von CSV/Parquet aus PhysioNet
- **Fehlwert-Imputation** (in EHR-Daten kritisch — oft 30-70% Missing)
- Feature-Normalisierung (Vitalzeichen, Lab-Werte haben sehr unterschiedliche Skalen)
- Handling variabler Sequenzlängen (**Padding + Mask**)

### 2. Padding-Mask für den Transformer
`nn.TransformerEncoder` akzeptiert `src_key_padding_mask`. Mit echten
MIMIC-Daten haben Patienten unterschiedliche Aufenthaltslängen — ohne Maske
werden Padding-Tokens in die Attention einbezogen und verfälschen das Ergebnis.

### 3. Klinische Metriken
**Accuracy ist für medizinische Datensätze irreführend.** MIMIC-III hat
typischerweise ~10-15% Mortalitätsrate — ein Modell das immer "überlebt"
vorhersagt, erreicht 85%+ Accuracy. Fehlend:
- **AUROC** (Industriestandard für Sepsis/Mortalitäts-Vorhersage)
- **AUPRC** (robuster bei Class-Imbalance)
- **Sensitivity / Specificity** (klinisch interpretierbar)
- `torchmetrics` würde diese einfach integrierbar machen

### 4. Class-Imbalance-Handling
`CrossEntropyLoss` ist aktuell ungewichtet. Mit realen Daten (10% positiv)
dominiert die Mehrheitsklasse das Training. Lösung:
```python
# Gewichteter Loss
pos_weight = torch.tensor([neg_count / pos_count])
self.loss_fn = nn.CrossEntropyLoss(weight=torch.tensor([1.0, pos_weight]))
```

### 5. Optuna Hyperparameter-Sweeps
Der Commit-Verlauf und die frühere `pyproject.toml` zeigen, dass Optuna
geplant war. Eine `conf/sweeper/`-Konfiguration mit der
`hydra-optuna-sweeper`-Integration würde Bayesian HPO mit einem einzigen
CLI-Flag ermöglichen (`--multirun`).

### 6. Inference / Evaluate Script
Das gespeicherte Checkpoint (`mimic-epoch=03-val_loss=0.08.ckpt`) kann
ohne ein eigenes Skript nicht genutzt werden. Ein `evaluate.py` fehlt komplett:
```python
model = DiseasePredictor.load_from_checkpoint("checkpoints/best.ckpt")
trainer.test(model, datamodule=dm)
```

### 7. Structured Config mit Dataclasses
Aktuell sind Tippfehler in YAML-Keys erst zur Laufzeit erkennbar.
Mit Hydra's `ConfigStore` + `@dataclass` gibt es IDE-Autocompletion
und sofortiges Feedback bei falschen Schlüsseln.

### 8. Tests & CI
Keine Tests vorhanden. Minimalsinnvoll wären:
- Unit-Test: `DiseasePredictor.forward()` gibt korrekte Output-Shape zurück
- Integrations-Test: `trainer.fit()` läuft 1 Epoch ohne Fehler
- GitHub Actions Workflow für automatische Prüfung bei jedem Push

---

## Gesamtbewertung

| Bereich | Bewertung | Kommentar |
|---|---|---|
| MLOps-Architektur | ✅ Stark | Hydra + Lightning + MLflow gut kombiniert |
| LSTM-Modell | ✅ Korrekt | Many-to-One, sauber strukturiert |
| Transformer-Modell | ⚠️ Vorhanden | Implementierung war korrekt (PE, Scaling, Pooling) |
| Config-System | 🔴 Bug | Interface-Mismatch → KeyError beim Start |
| Echte Daten | 🔴 Fehlt | Nur Mock, kein Loader |
| Klinische Metriken | 🔴 Fehlt | Nur Accuracy |
| Inference | 🔴 Fehlt | Kein evaluate.py |
| Tests / CI | 🔴 Fehlt | Keine Tests |
| Class-Imbalance | 🟡 Fehlt | Ungewichteter Loss |
| Dependency-Mgmt | ✅ Gut | uv ist die richtige Wahl |
