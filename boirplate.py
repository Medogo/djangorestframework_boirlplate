import os
import sys
import subprocess
import venv
from pathlib import Path
import shutil

class UltimeDjangoBoilerplateGenerator:
    def __init__(self):
        self.project_name = ""
        self.base_dir = Path.cwd()
        self.python_executable = sys.executable

    def get_project_details(self):
        """Demander les détails du projet"""
        while True:
            self.project_name = input("Nom du projet Django (en minuscules, sans espaces) : ").strip().lower()
            
            # Validation du nom de projet
            if not self.project_name:
                print("Le nom du projet ne peut pas être vide.")
                continue
            
            if not self.project_name.isidentifier():
                print("Nom de projet invalide. Utilisez uniquement des caractères alphanumériques et des underscores.")
                continue
            
            # Vérifier si le dossier existe déjà
            if (self.base_dir / f"{self.project_name}_env").exists():
                print(f"Un environnement pour {self.project_name} existe déjà. Choisissez un autre nom.")
                continue
            
            return True

    def create_virtual_environment(self):
        """Créer un environnement virtuel avec gestion d'erreurs"""
        env_path = self.base_dir / f"{self.project_name}_env"
        try:
            # Utiliser venv avec gestion explicite
            venv.create(env_path, with_pip=True, prompt=f"{self.project_name}-env")
            print(f"🔧 Environnement virtuel créé : {env_path}")
            return env_path
        except Exception as e:
            print(f"Erreur lors de la création de l'environnement virtuel : {e}")
            sys.exit(1)

    def get_pip_and_python_paths(self, env_path):
        """Obtenir les chemins de pip et python de manière portable"""
        if os.name == 'nt':  # Windows
            pip_path = env_path / "Scripts" / "pip"
            python_path = env_path / "Scripts" / "python"
        else:  # Unix-like
            pip_path = env_path / "bin" / "pip"
            python_path = env_path / "bin" / "python"
        
        return pip_path, python_path

    def install_dependencies(self, env_path):
        """Installer les dépendances avec robustesse"""
        pip_path, python_path = self.get_pip_and_python_paths(env_path)
        
        # Liste des dépendances
        dependencies = [
            "django", 
            "djangorestframework", 
            "djoser", 
            "djangorestframework-simplejwt",
            "django-cors-headers",
            "celery",
            "redis",
            "dramatiq[redis]",
            "pydantic",
            "drf-yasg",
            "drf-spectacular",
            "python-dotenv",
            "django-phonenumber-field[phonenumberslite]"
        ]

        # Mettre à jour pip
        try:
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        except subprocess.CalledProcessError:
            print("Impossible de mettre à jour pip")

        # Installation des dépendances
        for dep in dependencies:
            try:
                subprocess.run([str(pip_path), "install", dep], check=True)
                print(f"✅ Installé : {dep}")
            except subprocess.CalledProcessError:
                print(f"❌ Erreur lors de l'installation de {dep}")
        
        return python_path

    def create_django_project(self, python_path):
        """Créer le projet Django avec gestion d'erreurs"""
        try:
            # Créer le projet Django
            subprocess.run([str(python_path), "-m", "django", "startproject", self.project_name], check=True)
            
            # Se déplacer dans le répertoire du projet
            os.chdir(self.project_name)
            
            # Créer les apps
            apps = ["accounts", "core", "tasks"]
            for app in apps:
                subprocess.run([str(python_path), "manage.py", "startapp", app], check=True)
            
            print("🏗️ Projet Django et apps créés")
        
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la création du projet : {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Une erreur inattendue s'est produite : {e}")
            sys.exit(1)

    def generate_boilerplate(self):
        """Processus principal de génération avec gestion d'erreurs"""
        try:
            # Vérifier et obtenir le nom du projet
            if not self.get_project_details():
                return

            # Créer l'environnement virtuel
            env_path = self.create_virtual_environment()
            
            # Installer les dépendances
            python_path = self.install_dependencies(env_path)
            
            # Créer le projet Django
            self.create_django_project(python_path)

            print(f"\n🚀 Projet {self.project_name} généré avec succès!")
            print("Prochaines étapes :")
            print(f"1. cd {self.project_name}")
            print(f"2. source ../{self.project_name}_env/bin/activate")
            print("3. python manage.py makemigrations")
            print("4. python manage.py migrate")

        except Exception as e:
            print(f"Erreur fatale : {e}")
            # Nettoyer les ressources partiellement créées
            self.cleanup()

    def cleanup(self):
        """Nettoyer les ressources en cas d'erreur"""
        # Supprimer l'environnement virtuel
        env_path = self.base_dir / f"{self.project_name}_env"
        if env_path.exists():
            try:
                shutil.rmtree(env_path)
                print(f"Suppression de l'environnement virtuel : {env_path}")
            except Exception as e:
                print(f"Impossible de supprimer {env_path} : {e}")
        
        # Supprimer le projet Django
        project_path = self.base_dir / self.project_name
        if project_path.exists():
            try:
                shutil.rmtree(project_path)
                print(f"Suppression du projet : {project_path}")
            except Exception as e:
                print(f"Impossible de supprimer {project_path} : {e}")

def main():
    generator = UltimeDjangoBoilerplateGenerator()
    generator.generate_boilerplate()

if __name__ == "__main__":
    main()
