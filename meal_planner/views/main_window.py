"""
MainWindow - Fenêtre principale de l'application
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QSplitter, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from pathlib import Path
from datetime import datetime

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

        # Style global de l'application
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QStatusBar {
                background-color: #2c3e50;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QMenuBar {
                background-color: #34495e;
                color: white;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #2c3e50;
                border-radius: 4px;
            }
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 30px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        # Widget central
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #ecf0f1;")
        self.setCentralWidget(central_widget)

        # Layout principal avec splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Splitter pour diviser gauche/droite
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)

        # Panneau de gauche (paramètres) - 1/3
        self.settings_panel = SettingsPanel()
        self.settings_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        splitter.addWidget(self.settings_panel)

        # Panneau de droite (affichage) - 2/3
        self.meal_plan_display = MealPlanDisplay()
        self.meal_plan_display.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        splitter.addWidget(self.meal_plan_display)

        # Définir les proportions (1:2) et tailles minimales
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        # Empêcher le panneau gauche de se réduire trop
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # Définir les largeurs initiales (en pixels)
        splitter.setSizes([400, 800])

        main_layout.addWidget(splitter)

        # Menu bar
        self._create_menu_bar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("✓ Prêt")

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

        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Gestion (nouveau)
        manage_menu = menubar.addMenu("&Gestion")

        preset_meals_action = QAction("🍽️ Repas Prédéfinis", self)
        preset_meals_action.triggered.connect(self.on_manage_preset_meals)
        manage_menu.addAction(preset_meals_action)

        components_action = QAction("🥗 Composantes E/P/D", self)
        components_action.triggered.connect(self.on_manage_components)
        manage_menu.addAction(components_action)

        manage_menu.addSeparator()

        category_rules_action = QAction("📋 Règles de Catégories", self)
        category_rules_action.triggered.connect(self.on_manage_category_rules)
        manage_menu.addAction(category_rules_action)

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

        # Signaux de sauvegarde
        self.meal_plan_display.save_requested.connect(self.on_save_plan)

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
                f"✓ Plan généré avec succès - {meal_plan.duration_days} jour(s)"
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
            self._update_status("✓ Nouveau plan créé")

    def on_error(self, error_message: str):
        """
        Gère les erreurs du contrôleur.

        Args:
            error_message: Message d'erreur
        """
        self.show_error("Erreur", error_message)

    def on_manage_preset_meals(self):
        """Ouvre l'interface de gestion des repas prédéfinis."""
        from meal_planner.views.preset_meal_manager import PresetMealManager
        dialog = PresetMealManager(self.controller.db_manager, parent=self)
        dialog.exec()
        self._update_status("✓ Gestion des repas prédéfinis")

    def on_manage_components(self):
        """Ouvre l'interface de gestion des composantes E/P/D."""
        from meal_planner.views.meal_component_manager import MealComponentManager
        dialog = MealComponentManager(self.controller.db_manager, parent=self)
        dialog.exec()
        self._update_status("✓ Gestion des composantes E/P/D")

    def on_manage_category_rules(self):
        """Ouvre l'interface de configuration des règles de catégories."""
        from meal_planner.views.category_rules_dialog import CategoryRulesDialog
        dialog = CategoryRulesDialog(parent=self)
        dialog.exec()
        self._update_status("✓ Configuration des règles de catégories")

    def on_save_plan(self):
        """Gère la sauvegarde du plan alimentaire."""
        try:
            # Vérifier qu'il y a un plan à sauvegarder
            current_plan = self.controller.get_current_plan()
            if not current_plan:
                self.show_error(
                    "Aucun plan",
                    "Aucun plan alimentaire à sauvegarder.\nVeuillez d'abord générer un plan."
                )
                return

            # Créer un nom de fichier par défaut
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"plan_alimentaire_{timestamp}.json"

            # Ouvrir le dialogue de sauvegarde
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder le plan alimentaire",
                default_filename,
                "Fichiers JSON (*.json);;Tous les fichiers (*.*)"
            )

            if not file_path:
                # L'utilisateur a annulé
                return

            # Sauvegarder le plan
            self._update_status("Sauvegarde en cours...")
            success = current_plan.save_to_json(file_path)

            if success:
                self._update_status(f"✓ Plan sauvegardé: {Path(file_path).name}")
                QMessageBox.information(
                    self,
                    "Sauvegarde réussie",
                    f"Le plan alimentaire a été sauvegardé avec succès dans:\n{file_path}"
                )
                logger.info(f"Plan sauvegardé: {file_path}")
            else:
                self.show_error(
                    "Erreur de sauvegarde",
                    "Une erreur est survenue lors de la sauvegarde du plan."
                )

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}", exc_info=True)
            self.show_error("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")

    def on_about(self):
        """Affiche la boîte de dialogue À propos."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("À propos de Meal Planner Pro")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(
            "<div style='text-align: center;'>"
            "<h2 style='color: #2c3e50; margin-bottom: 10px;'>🍽️ Meal Planner Pro</h2>"
            "<p style='color: #7f8c8d; font-size: 11px; margin: 5px 0;'>Version 1.0.0 (Multi-Modes)</p>"
            "<p style='color: #34495e; margin: 15px 0;'>Générateur de plans alimentaires personnalisés</p>"
            "</div>"
            "<div style='margin-top: 20px;'>"
            "<p style='color: #2c3e50; font-weight: bold; margin-bottom: 8px;'>✨ Fonctionnalités:</p>"
            "<ul style='color: #555; margin-left: 20px;'>"
            "<li>🎯 4 modes de génération (Aliments, Repas, E/P/D, Catégories)</li>"
            "<li>🎨 Interface moderne et intuitive</li>"
            "<li>💾 Gestion des repas et composantes</li>"
            "<li>⚙️ Configuration personnalisable</li>"
            "</ul>"
            "</div>"
            "<div style='margin-top: 15px;'>"
            "<p style='color: #2c3e50; font-weight: bold; margin-bottom: 8px;'>🚀 À venir (Phase 2):</p>"
            "<ul style='color: #555; margin-left: 20px;'>"
            "<li>🧮 Algorithme de génération optimisée</li>"
            "<li>🍱 Génération de repas complets</li>"
            "<li>📊 Export PDF/Excel</li>"
            "</ul>"
            "</div>"
        )
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                min-width: 450px;
                min-height: 300px;
            }
        """)
        msg_box.exec()

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
