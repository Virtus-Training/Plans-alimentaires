"""
CategoryRulesDialog - Interface de configuration des règles de catégories
"""

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QTabWidget, QWidget, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from meal_planner.config import CATEGORY_RULES_PATH, FOOD_CATEGORIES_DETAILED
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


class CategoryRulesDialog(QDialog):
    """
    Dialogue de configuration des règles de catégories alimentaires.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration des Règles de Catégories")
        self.setMinimumSize(700, 550)
        self.rules = self.load_rules()
        self.init_ui()

    def load_rules(self):
        """Charge les règles depuis le fichier JSON."""
        try:
            with open(CATEGORY_RULES_PATH, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            logger.info(f"Règles chargées depuis {CATEGORY_RULES_PATH}")
            return rules
        except FileNotFoundError:
            logger.warning("Fichier de règles introuvable, utilisation de règles par défaut")
            return {
                "breakfast": {"required": ["céréales", "produits laitiers"], "optional": ["fruits"]},
                "lunch": {"required": ["protéines", "féculents", "légumes"], "optional": []},
                "dinner": {"required": ["protéines", "légumes"], "optional": ["féculents"]},
                "snack": {"required": ["fruits"], "optional": ["produits laitiers"]},
            }
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            return {}

    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Titre
        title = QLabel("📋 Configuration des Règles de Catégories")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Définissez quelles catégories d'aliments sont <b>requises</b> ou "
            "<b>optionnelles</b> pour chaque type de repas."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #555; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Tabs par type de repas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #ddd;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
                font-weight: bold;
            }
        """)

        self.meal_widgets = {}

        # Créer un tab pour chaque type de repas
        meal_types = [
            ("breakfast", "Petit-déjeuner"),
            ("lunch", "Déjeuner"),
            ("dinner", "Dîner"),
            ("snack", "Collation"),
            ("afternoon_snack", "Goûter"),
            ("morning_snack", "Collation matinale"),
            ("evening_snack", "Collation soirée")
        ]

        for meal_type, display_name in meal_types:
            tab_widget = self._create_meal_type_tab(meal_type)
            self.tabs.addTab(tab_widget, display_name)
            self.meal_widgets[meal_type] = tab_widget

        layout.addWidget(self.tabs)

        # Info sur les catégories disponibles
        info_label = QLabel(
            "<b>Catégories disponibles:</b> " +
            ", ".join(sorted(FOOD_CATEGORIES_DETAILED.keys()))
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            background-color: #fff3cd;
            padding: 8px;
            border-radius: 4px;
            border-left: 3px solid #ffc107;
            font-size: 11px;
        """)
        layout.addWidget(info_label)

        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        reset_btn = QPushButton("🔄 Réinitialiser aux défauts")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b2babb;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_btn.clicked.connect(self.save_rules)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _create_meal_type_tab(self, meal_type):
        """Crée un tab pour un type de repas."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Liste des catégories requises
        required_layout = QVBoxLayout()
        required_label = QLabel("Catégories <b>REQUISES</b>")
        required_label.setStyleSheet("font-size: 12px; color: #e74c3c;")
        required_layout.addWidget(required_label)

        required_list = QListWidget()
        required_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        required_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e74c3c;
                border-radius: 5px;
                background: #fff5f5;
            }
            QListWidget::item:selected {
                background: #e74c3c;
                color: white;
            }
        """)
        required_layout.addWidget(required_list)

        # Ajouter toutes les catégories
        for category in sorted(FOOD_CATEGORIES_DETAILED.keys()):
            required_list.addItem(category)

        # Pré-sélectionner les catégories requises
        meal_rules = self.rules.get(meal_type, {})
        required_cats = meal_rules.get("required", [])
        for i in range(required_list.count()):
            item = required_list.item(i)
            if item.text() in required_cats:
                item.setSelected(True)

        layout.addLayout(required_layout)

        # Liste des catégories optionnelles
        optional_layout = QVBoxLayout()
        optional_label = QLabel("Catégories <b>OPTIONNELLES</b>")
        optional_label.setStyleSheet("font-size: 12px; color: #3498db;")
        optional_layout.addWidget(optional_label)

        optional_list = QListWidget()
        optional_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        optional_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #3498db;
                border-radius: 5px;
                background: #f5f9ff;
            }
            QListWidget::item:selected {
                background: #3498db;
                color: white;
            }
        """)
        optional_layout.addWidget(optional_list)

        # Ajouter toutes les catégories
        for category in sorted(FOOD_CATEGORIES_DETAILED.keys()):
            optional_list.addItem(category)

        # Pré-sélectionner les catégories optionnelles
        optional_cats = meal_rules.get("optional", [])
        for i in range(optional_list.count()):
            item = optional_list.item(i)
            if item.text() in optional_cats:
                item.setSelected(True)

        layout.addLayout(optional_layout)

        # Stocker les références
        widget.required_list = required_list
        widget.optional_list = optional_list

        return widget

    def save_rules(self):
        """Sauvegarde les règles dans le fichier JSON."""
        new_rules = {}

        for meal_type, widget in self.meal_widgets.items():
            # Récupérer les catégories sélectionnées
            required = [
                widget.required_list.item(i).text()
                for i in range(widget.required_list.count())
                if widget.required_list.item(i).isSelected()
            ]

            optional = [
                widget.optional_list.item(i).text()
                for i in range(widget.optional_list.count())
                if widget.optional_list.item(i).isSelected()
            ]

            # Validation : au moins 1 catégorie requise
            if not required:
                QMessageBox.warning(
                    self,
                    "Validation",
                    f"Le type de repas '{meal_type}' doit avoir au moins une catégorie requise."
                )
                return

            new_rules[meal_type] = {
                "required": required,
                "optional": optional
            }

        # Sauvegarder dans le fichier
        try:
            # Créer le répertoire si nécessaire
            CATEGORY_RULES_PATH.parent.mkdir(parents=True, exist_ok=True)

            with open(CATEGORY_RULES_PATH, 'w', encoding='utf-8') as f:
                json.dump(new_rules, f, indent=2, ensure_ascii=False)

            logger.info(f"Règles sauvegardées dans {CATEGORY_RULES_PATH}")
            QMessageBox.information(
                self,
                "Succès",
                "Les règles de catégories ont été sauvegardées avec succès!"
            )
            self.accept()

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de sauvegarder les règles:\n{str(e)}"
            )

    def reset_to_defaults(self):
        """Réinitialise les règles aux valeurs par défaut."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment réinitialiser les règles aux valeurs par défaut ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            default_rules = {
                "breakfast": {"required": ["céréales", "produits laitiers"], "optional": ["fruits"]},
                "lunch": {"required": ["protéines", "féculents", "légumes"], "optional": []},
                "dinner": {"required": ["protéines", "légumes"], "optional": ["féculents"]},
                "snack": {"required": ["fruits"], "optional": ["produits laitiers"]},
                "afternoon_snack": {"required": ["fruits"], "optional": ["produits laitiers", "noix"]},
                "morning_snack": {"required": ["fruits"], "optional": ["produits laitiers"]},
                "evening_snack": {"required": [], "optional": ["produits laitiers", "fruits"]}
            }

            self.rules = default_rules

            # Recharger l'interface
            for meal_type, widget in self.meal_widgets.items():
                meal_rules = self.rules.get(meal_type, {})
                required_cats = meal_rules.get("required", [])
                optional_cats = meal_rules.get("optional", [])

                # Désélectionner tout
                for i in range(widget.required_list.count()):
                    widget.required_list.item(i).setSelected(False)
                for i in range(widget.optional_list.count()):
                    widget.optional_list.item(i).setSelected(False)

                # Sélectionner selon les valeurs par défaut
                for i in range(widget.required_list.count()):
                    item = widget.required_list.item(i)
                    if item.text() in required_cats:
                        item.setSelected(True)

                for i in range(widget.optional_list.count()):
                    item = widget.optional_list.item(i)
                    if item.text() in optional_cats:
                        item.setSelected(True)

            QMessageBox.information(self, "Info", "Règles réinitialisées aux valeurs par défaut.")
