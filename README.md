# Medical Prediction Project

Eine kurze Übersicht, wie du das Projekt zum Laufen bekommst. Wir analysieren hier Patientendaten, um Risiken (wie Mortalität) vorherzusagen.

https://github.com/user-attachments/assets/5c5f9f5e-4d80-4f9e-a78b-9e99ffc934b5

## Quick Start (Docker)

Am einfachsten startest du das Ganze im Container, dann musst du dich nicht mit Python-Versionen rumschlagen.

1. **Image bauen:**
   ```bash
   docker build -t med-pred-app .
   ```

2. **Container starten:**
   Hierbei werden zwei Ports freigegeben: 8000 für die API und 8501 für das Dashboard.
   ```bash
   docker run -p 8000:8000 -p 8501:8501 med-pred-app
   ```

Sobald der Container läuft, findest du hier deine Tools:
- **Dashboard (Streamlit):** [http://localhost:8501](http://localhost:8501)
- **API Dokumentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠 Lokal entwickeln

Falls du am Code arbeiten willst, nutzen wir `uv` für das Dependency Management (weil es einfach schneller ist als pip).

**Voraussetzung:** Du hast uv installiert.

1. **Abhängigkeiten installieren:**
   ```bash
   uv pip install -r pyproject.toml
   ```

2. **Starten:**
   Du kannst die Services einzeln starten:

   *API:*
   ```bash
   uv run uvicorn deploy.api:app --reload
   ```

   *Dashboard:*
   ```bash
   uv run streamlit run deploy/dashboard.py
   ```
