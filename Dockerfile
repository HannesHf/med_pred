# Basis Image
FROM python:3.10-slim

# uv installieren (für schnelle, korrekte Installation aus pyproject.toml)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Arbeitsverzeichnis
WORKDIR /app

# System-Abhängigkeiten (für SQLite etc.)
RUN apt-get update && apt-get install -y build-essential

# Python Abhängigkeiten installieren
COPY pyproject.toml .
# uv.lock . # (Optional: Falls du eine uv.lock hast, hier einkommentieren für exakte Reproduzierbarkeit)

# Installation direkt aus der toml -> Garantiert Übereinstimmung!
# Wir nutzen --system, da wir im Container sind.
# Wir erzwingen die CPU-Version von PyTorch via index-url, um das Image klein zu halten
RUN uv pip install --system \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    -r pyproject.toml

# Code kopieren
COPY src/ src/
COPY deploy/ deploy/
COPY conf/ conf/

# Ports freigeben
EXPOSE 8000
EXPOSE 8501

# Start-Skript (Startet beides - nur für Demo Zwecke, in Prod getrennte Container!)
CMD ["sh", "-c", "uvicorn deploy.api:app --host 0.0.0.0 --port 8000 & streamlit run deploy/dashboard.py --server.port 8501 --server.address 0.0.0.0"]