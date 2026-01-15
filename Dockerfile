FROM python:3.13-slim

WORKDIR /app

# Installer les dépendances système et curl pour uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Ajouter uv au PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copier les fichiers du projet
COPY pyproject.toml .
COPY src/ ./src/

# Installer les dépendances Python avec uv
RUN uv pip install --system -r pyproject.toml

# Créer le répertoire pour les logs
RUN mkdir -p logs

# Variable d'environnement par défaut
ENV PYTHONUNBUFFERED=1

# Lancer le serveur
CMD ["python", "src/main.py"]
