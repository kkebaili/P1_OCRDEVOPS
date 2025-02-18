# config.py
import os

# Récupération des variables d'environnement
TOKEN = os.getenv("GITLAB_TOKEN")
PROJECT_ID = os.getenv("GITLAB_PROJECT_ID", "66063494")  # Valeur par défaut si non défini
TOKEN_NAME = os.getenv("GITLAB_TOKEN_NAME", "gitlab+deploy-token-7355062")
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"  # Convertir en booléen

# Vérification des valeurs obligatoires
if TOKEN is None:
    raise ValueError("⚠️  La variable d'environnement 'GITLAB_TOKEN' est obligatoire mais non définie.")

print("🔐 Configuration chargée avec succès.")

