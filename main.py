"""
Point d'entrée de l'application Meal Planner Pro
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from meal_planner.models.database import DatabaseManager
from meal_planner.views.main_window import MainWindow
from meal_planner.config import DATABASE_PATH, PRESETS_DIR, LOG_CONFIG
from meal_planner.utils.logger import setup_logger

# Configurer le logger
logger = setup_logger(
    level=LOG_CONFIG["level"],
    log_file=LOG_CONFIG["filename"],
    format_string=LOG_CONFIG["format"]
)


def initialize_database(db_manager: DatabaseManager) -> None:
    """
    Initialise la base de données avec les aliments par défaut si nécessaire.

    Args:
        db_manager: Gestionnaire de base de données
    """
    try:
        stats = db_manager.get_statistics()
        total_foods = stats.get("total_foods", 0)

        logger.info(f"Base de données: {total_foods} aliments trouvés")

        if total_foods == 0:
            logger.info("Base de données vide, chargement des aliments par défaut...")

            default_foods_path = PRESETS_DIR / "default_foods.json"

            if default_foods_path.exists():
                count = db_manager.load_foods_from_json(default_foods_path)
                logger.info(f"{count} aliments chargés depuis {default_foods_path}")
                print(f"[OK] {count} aliments charges dans la base de donnees")
            else:
                logger.warning(f"Fichier d'aliments par défaut introuvable: {default_foods_path}")
                print(f"[ATTENTION] Fichier d'aliments par defaut introuvable")

        # Afficher les statistiques
        stats = db_manager.get_statistics()
        logger.info(f"Statistiques de la base: {stats}")

        print(f"\n=== Base de données initialisée ===")
        print(f"Total d'aliments: {stats['total_foods']}")
        print(f"Catégories: {len(stats['categories'])}")
        for category, count in stats['categories'].items():
            print(f"  - {category}: {count}")
        print()

    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}", exc_info=True)
        print(f"[ERREUR] Erreur lors de l'initialisation: {e}")


def main():
    """Point d'entrée principal de l'application."""
    try:
        logger.info("=" * 60)
        logger.info("Démarrage de Meal Planner Pro")
        logger.info("=" * 60)

        # Créer l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Meal Planner Pro")
        app.setOrganizationName("Meal Planner")

        # Initialiser le gestionnaire de base de données
        logger.info(f"Initialisation de la base de données: {DATABASE_PATH}")
        db_manager = DatabaseManager(DATABASE_PATH)

        # Charger les aliments par défaut si nécessaire
        initialize_database(db_manager)

        # Créer et afficher la fenêtre principale
        logger.info("Création de la fenêtre principale")
        main_window = MainWindow(db_manager)
        main_window.show()

        logger.info("Application démarrée avec succès")
        print("[OK] Application lancee avec succes\n")

        # Lancer la boucle d'événements
        exit_code = app.exec()

        logger.info(f"Application terminée avec le code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Erreur fatale lors du démarrage: {e}", exc_info=True)
        print(f"\n[ERREUR FATALE] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
