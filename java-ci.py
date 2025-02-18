import subprocess
import typer
import requests
from pathlib import Path
import config  # Importer les variables depuis config.py

app = typer.Typer()

def run_command(command, log_file, error_log_file, debug=config.DEBUG_MODE):
    """Exécute une commande shell et enregistre les logs."""
    print(f"🔧 Exécution de la commande: {command}")

    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )

    with open(log_file, "w") as f_out, open(error_log_file, "w") as f_err:
        f_out.write(result.stdout or "")
        f_err.write(result.stderr or "")

    if result.returncode != 0:
        print(f"❌ Erreur lors de l'exécution de: {command}")
        print(f"📄 Consulte les logs: {error_log_file}")
        raise RuntimeError(f"Commande échouée avec le code {result.returncode}")

    print(f"✅ Commande réussie: {command}")

@app.command()
def build():
    """Compile le projet avec Gradle."""
    logs_dir = Path("./logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        run_command(f"./gradlew build --info", logs_dir / "build_output.log", logs_dir / "build_errors.log")
    except RuntimeError:
        print("❌ Échec de la compilation du projet.")
        return

    print("✅ Compilation réussie!")

@app.command()
def test():
    """Exécute les tests unitaires avec Gradle."""
    logs_dir = Path("./logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    try:
        run_command(f"./gradlew test --info", logs_dir / "test_output.log", logs_dir / "test_errors.log")
    except RuntimeError:
        print("❌ Échec des tests unitaires.")
        return

    print("✅ Tests exécutés avec succès!")

@app.command()
def pack():
    """Génère le fichier .war de l'application."""
    logs_dir = Path("./logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    try:
        run_command(f"./gradlew war --info", logs_dir / "pack_output.log", logs_dir / "pack_errors.log")
    except RuntimeError:
        print("❌ Échec de la génération du fichier .war.")
        return

    print("✅ Fichier .war généré avec succès!")

@app.command()
def publish():
    """Publie le projet dans la GitLab Package Registry avec Gradle."""
    
    logs_dir = Path("./logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Publication du package dans la GitLab Package Registry (projet {config.PROJECT_ID})...")

    # Configuration du fichier gradle.properties pour l'authentification
    gradle_props_path = Path("gradle.properties")
    gradle_props_content = f"""
publishing {{
    repositories {{
        maven {{
            url = uri("https://gitlab.com/api/v4/projects/{config.PROJECT_ID}/packages/maven")
            credentials {{
                username = "{config.TOKEN_NAME}"
                password = "{config.TOKEN}"
            }}
        }}
    }}
}}
"""
    with gradle_props_path.open("w") as f:
        f.write(gradle_props_content)

    # 🔧 Exécution de Gradle avec `run_command`
    try:
        run_command(f"./gradlew publish --info", logs_dir / "publish_output.log", logs_dir / "publish_errors.log")
    except RuntimeError:
        print("❌ Échec de la publication du package.")
        return

    print("✅ Publication réussie dans la GitLab Package Registry!")

    # 🔎 Vérification de la publication avec Deploy Token
    print("🔎 Vérification de la publication dans la GitLab Package Registry...")

    package_registry_url = f"https://gitlab.com/api/v4/projects/{config.PROJECT_ID}/packages"
    auth = (config.TOKEN_NAME, config.TOKEN)  # Utilisation du Deploy Token pour l'authentification

    response = requests.get(package_registry_url, auth=auth)

    if response.status_code == 200 and response.json():
        print(f"📦 Package(s) publié(s) avec succès :")
        for package in response.json():
            print(f"- {package.get('name', 'Inconnu')} (version {package.get('version', 'N/A')})")
    else:
        print("❌ Erreur : Impossible de vérifier la publication du package !")
        print(f"Code HTTP: {response.status_code}")
        print(f"Réponse: {response.text}")

# 🔥 Exécuter l'application Typer
if __name__ == "__main__":
    app()
