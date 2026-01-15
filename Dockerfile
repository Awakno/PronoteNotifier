FROM python:3.13-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier les fichiers du projet
COPY pyproject.toml .
COPY src/ ./src/

# Installer les dépendances Python avec uv
RUN uv pip install --system pronotepy python-dotenv schedule python-telegram-bot

# Créer le répertoire pour les logs
RUN mkdir -p logs

# Variable d'environnement par défaut
ENV PYTHONUNBUFFERED=1

# Lancer le serveur
CMD ["python", "src/main.py"]
