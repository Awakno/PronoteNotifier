FROM python:3.13-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers du projet
COPY pyproject.toml .
COPY src/ ./src/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Créer le répertoire pour les logs
RUN mkdir -p logs

# Variable d'environnement par défaut
ENV PYTHONUNBUFFERED=1

# Lancer le serveur
CMD ["python", "src/main.py"]
