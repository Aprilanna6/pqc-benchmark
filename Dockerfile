# Basis-Image mit Python 3.12
FROM python:3.12-slim

# Arbeitsverzeichnis
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projekt kopieren
COPY . .

# Standardkommando beim Start
CMD ["python", "benchmark_kem.py"]

