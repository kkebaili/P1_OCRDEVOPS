import subprocess
import typer
import requests
from pathlib import Path

app = typer.Typer()

def run_command(command, log_file, error_log_file, debug=False):
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
def build(
    token: str = typer.Option(..., help="Token d'authentification"),
    project_id: str = typer.Option(..., help="ID du projet GitLab"),
    token_name: str = typer.Option(..., help="Nom du token utilisé"),
    logs_dir: Path = Path("./logs"),
    debug: bool = False
):
    """Compile le projet avec Gradle."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    try:
        run_command(f"./gradlew build --info", logs_dir / "build_output.log", logs_dir / "build_errors.log", debug)
    except RuntimeError:
        print("❌ Échec de la compilation du projet.")
        return

    print("✅ Compilation réussie!")

@app.command()
def test(
    token: str = typer.Option(..., help="Token d'authentification"),
    project_id: str = typer.Option(..., help="ID du projet GitLab"),
    token_name: str = typer.Option(..., help="Nom du token utilisé"),
    logs_dir: Path = Path("./logs"),
    debug: bool = False
):
    """Exécute les tests unitaires avec Gradle."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    try:
        run_command(f"./gradlew test --info", logs_dir / "test_output.log", logs_dir / "test_errors.log", debug)
    except RuntimeError:
        print("❌ Échec des tests unitaires.")
        return

    print("✅ Tests exécutés avec succès!")

@app.command()
def pack(
    token: str = typer.Option(..., help="Token d'authentification"),
    project_id: str = typer.Option(..., help="ID du projet GitLab"),
    token_name: str = typer.Option(..., help="Nom du token utilisé"),
    logs_dir: Path = Path("./logs"),
    debug: bool = False
):
    """Génère le fichier .war de l'application."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    try:
        run_command(f"./gradlew war --info", logs_dir / "pack_output.log", logs_dir / "pack_errors.log", debug)
    except RuntimeError:
        print("❌ Échec de la génération du fichier .war.")
        return

    print("✅ Fichier .war généré avec succès!")

@app.command()
def publish(
    token: str = typer.Option(..., help="Token d'authentification"),
    project_id: str = typer.Option(..., help="ID du projet GitLab"),
    token_name: str = typer.Option(..., help="Nom du token utilisé"),
    gradle_command: str = typer.Option("publish", help="Commande Gradle pour la publication"),
    logs_dir: Path = Path("./logs"),
    debug: bool = False
):
    """Publie le projet dans la GitLab Package Registry avec Gradle et vérifie la publication."""
    
    logs_dir.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Publication du package dans la GitLab Package Registry (projet {project_id})...")

    # Configuration du fichier gradle.properties pour l'authentification
    gradle_props_path = Path("gradle.properties")
    gradle_props_content = f"""
publishing {{
    repositories {{
        maven {{
            url = uri("https://gitlab.com/api/v4/projects/{project_id}/packages/maven")
            credentials {{
                username = "{token_name}"
                password = "{token}"
            }}
        }}
    }}
}}
"""
    with gradle_props_path.open("w") as f:
        f.write(gradle_props_content)

    # 🔧 Exécution de Gradle avec `run_command`
    try:
        run_command(f"./gradlew {gradle_command} --info", logs_dir / "publish_output.log", logs_dir / "publish_errors.log", debug)
    except RuntimeError:
        print("❌ Échec de la publication du package.")
        return

    print("✅ Publication réussie dans la GitLab Package Registry!")

    # 🔎 Vérification de la publication avec Deploy Token
    print("🔎 Vérification de la publication dans la GitLab Package Registry...")

    package_registry_url = f"https://gitlab.com/api/v4/projects/{project_id}/packages"
    auth = (token_name, token)  # Utilisation du Deploy Token pour l'authentification

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
