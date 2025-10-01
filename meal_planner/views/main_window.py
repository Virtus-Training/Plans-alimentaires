"""
MainWindow - Fenêtre principale de l'application
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from meal_planner.views.settings_panel import SettingsPanel
from meal_planner.views.meal_plan_display import MealPlanDisplay
from meal_planner.controllers.meal_plan_controller import MealPlanController
from meal_planner.models.database import DatabaseManager
from meal_planner.config import WINDOW_CONFIG, PRESETS_DIR
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application Meal Planner Pro."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.controller = MealPlanController(db_manager)

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        # Configuration de la fenêtre
        self.setWindowTitle(WINDOW_CONFIG["title"])
        self.resize(WINDOW_CONFIG["width"], WINDOW_CONFIG["height"])
        self.setMinimumSize(WINDOW_CONFIG["min_width"], WINDOW_CONFIG["min_height"])

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal avec splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Splitter pour diviser gauche/droite
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panneau de gauche (paramètres) - 1/3
        self.settings_panel = SettingsPanel()
        splitter.addWidget(self.settings_panel)

        # Panneau de droite (affichage) - 2/3
        self.meal_plan_display = MealPlanDisplay()
        splitter.addWidget(self.meal_plan_display)

        # Définir les proportions (1:2)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # Menu bar
        self._create_menu_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("Prêt")

    def _create_menu_bar(self):
        """Crée la barre de menu."""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")

        new_action = QAction("&Nouveau", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_plan)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Gérer aliments (pour Phase 3)
        # manage_foods_action = QAction("&Gérer les aliments", self)
        # manage_foods_action.triggered.connect(self.on_manage_foods)
        # file_menu.addAction(manage_foods_action)

        # file_menu.addSeparator()

        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Export (Phase 3)
        # export_menu = menubar.addMenu("&Export")
        #
        # export_pdf_action = QAction("Export &PDF", self)
        # export_pdf_action.triggered.connect(self.on_export_pdf)
        # export_menu.addAction(export_pdf_action)
        #
        # export_excel_action = QAction("Export &Excel", self)
        # export_excel_action.triggered.connect(self.on_export_excel)
        # export_menu.addAction(export_excel_action)

        # Menu Aide
        help_menu = menubar.addMenu("&Aide")

        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Connecte les signaux aux slots."""
        # Signaux de la vue vers le contrôleur
        self.settings_panel.generate_requested.connect(self.on_generate_plan)
        self.settings_panel.settings_changed.connect(self.on_settings_changed)

        # Signaux du contrôleur vers la vue
        self.controller.plan_generated.connect(self.on_plan_generated)
        self.controller.error_occurred.connect(self.on_error)
        self.controller.status_updated.connect(self._update_status)

    def on_generate_plan(self):
        """Gère la demande de génération de plan."""
        try:
            settings = self.settings_panel.get_settings()

            # Valider les paramètres
            is_valid, msg = self.controller.validate_settings(settings)
            if not is_valid:
                self.show_error("Paramètres invalides", msg)
                return

            # Vérifier qu'il y a des aliments en base
            foods_count = self.controller.load_foods_count()
            if foods_count == 0:
                self.show_error(
                    "Aucun aliment",
                    "La base de données ne contient aucun aliment.\n"
                    "Veuillez charger les aliments par défaut au démarrage."
                )
                return

            # Générer le plan
            self.controller.generate_meal_plan(settings)

        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}", exc_info=True)
            self.show_error("Erreur", f"Erreur lors de la génération du plan: {str(e)}")

    def on_plan_generated(self, meal_plan):
        """
        Gère la réception d'un plan généré.

        Args:
            meal_plan: Le plan alimentaire généré
        """
        try:
            self.meal_plan_display.display_meal_plan(meal_plan)
            self._update_status(
                f"Plan généré avec succès - {meal_plan.duration_days} jour(s)"
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage du plan: {e}", exc_info=True)
            self.show_error("Erreur d'affichage", str(e))

    def on_settings_changed(self, settings: dict):
        """
        Gère le changement de paramètres.

        Args:
            settings: Nouveaux paramètres
        """
        # Pour Phase 1, on ne fait rien
        # Phase 2: Possibilité de régénérer automatiquement
        pass

    def on_new_plan(self):
        """Crée un nouveau plan (réinitialise l'interface)."""
        reply = QMessageBox.question(
            self,
            "Nouveau plan",
            "Créer un nouveau plan ? Les données actuelles seront perdues.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.meal_plan_display.clear()
            self._update_status("Nouveau plan")

    def on_error(self, error_message: str):
        """
        Gère les erreurs du contrôleur.

        Args:
            error_message: Message d'erreur
        """
        self.show_error("Erreur", error_message)

    def on_about(self):
        """Affiche la boîte de dialogue À propos."""
        QMessageBox.about(
            self,
            "À propos de Meal Planner Pro",
            "<h3>Meal Planner Pro</h3>"
            "<p>Version 0.1.0 (Phase 1)</p>"
            "<p>Générateur de plans alimentaires personnalisés</p>"
            "<p><b>Fonctionnalités Phase 1:</b></p>"
            "<ul>"
            "<li>Configuration des objectifs nutritionnels</li>"
            "<li>Interface avec sliders interactifs</li>"
            "<li>Base de données d'aliments</li>"
            "<li>Architecture MVC complète</li>"
            "</ul>"
            "<p><b>À venir (Phase 2):</b></p>"
            "<ul>"
            "<li>Algorithme de génération optimisée</li>"
            "<li>Génération de repas complets</li>"
            "</ul>"
        )

    def show_error(self, title: str, message: str):
        """
        Affiche une boîte de dialogue d'erreur.

        Args:
            title: Titre de la boîte
            message: Message d'erreur
        """
        QMessageBox.critical(self, title, message)
        logger.error(f"{title}: {message}")

    def _update_status(self, message: str):
        """
        Met à jour la barre de statut.

        Args:
            message: Message à afficher
        """
        self.status_bar.showMessage(message)

    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre."""
        reply = QMessageBox.question(
            self,
            "Quitter",
            "Êtes-vous sûr de vouloir quitter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Fermeture de l'application")
            event.accept()
        else:
            event.ignore()
