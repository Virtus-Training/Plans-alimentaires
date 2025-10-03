"""
MealComponentManager - Interface de gestion des composantes de repas (E/P/D)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QComboBox,
    QLineEdit, QDialogButtonBox, QListWidget, QSpinBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from meal_planner.models.meal_component import MealComponent
from meal_planner.models.database import DatabaseManager
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


class MealComponentManager(QDialog):
    """
    Interface de gestion CRUD pour les composantes de repas.
    """

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Gestion des Composantes de Repas")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_components()

    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Titre
        title = QLabel("🥗 Composantes Entrée/Plat/Dessert")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)

        # Filtre par type
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrer par type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tous", "entrée", "plat", "dessert", "accompagnement"])
        self.type_filter.currentTextChanged.connect(self.load_components)
        filter_layout.addWidget(self.type_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Tableau des composantes
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nom", "Type", "Calories", "Aliments"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_button = QPushButton("➕ Ajouter")
        self.add_button.setStyleSheet("""
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
        self.add_button.clicked.connect(self.add_component)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("✏️ Modifier")
        self.edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        self.edit_button.clicked.connect(self.edit_component)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("🗑️ Supprimer")
        self.delete_button.setStyleSheet("""
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
        self.delete_button.clicked.connect(self.delete_component)
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Fermer")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #b2babb;
            }
        """)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def load_components(self):
        """Charge les composantes depuis la base de données."""
        try:
            filter_type = self.type_filter.currentText()

            if filter_type == "Tous":
                components = self.db_manager.get_all_meal_components()
            else:
                components = self.db_manager.get_components_by_type(filter_type)

            self.table.setRowCount(len(components))

            for row, comp in enumerate(components):
                macros = comp.calculate_macros()

                self.table.setItem(row, 0, QTableWidgetItem(str(comp.id)))
                self.table.setItem(row, 1, QTableWidgetItem(comp.name))
                self.table.setItem(row, 2, QTableWidgetItem(comp.component_type))
                self.table.setItem(row, 3, QTableWidgetItem(f"{macros['calories']:.0f} kcal"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{len(comp.foods)} aliments"))

            logger.info(f"{len(components)} composantes chargées")

        except Exception as e:
            logger.error(f"Erreur lors du chargement des composantes: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les composantes:\n{str(e)}")

    def add_component(self):
        """Ouvre la fenêtre d'ajout d'une composante."""
        dialog = MealComponentDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_components()

    def edit_component(self):
        """Ouvre la fenêtre d'édition de la composante sélectionnée."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Info", "Veuillez sélectionner une composante à modifier.")
            return

        row = selected_rows[0].row()
        comp_id = int(self.table.item(row, 0).text())

        try:
            component = self.db_manager.get_meal_component_by_id(comp_id)
            if component:
                dialog = MealComponentDialog(self.db_manager, component=component, parent=self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_components()
        except Exception as e:
            logger.error(f"Erreur lors de l'édition: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de modifier la composante:\n{str(e)}")

    def delete_component(self):
        """Supprime la composante sélectionnée."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Info", "Veuillez sélectionner une composante à supprimer.")
            return

        row = selected_rows[0].row()
        comp_id = int(self.table.item(row, 0).text())
        comp_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer la composante '{comp_name}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_meal_component(comp_id)
                self.load_components()
                QMessageBox.information(self, "Succès", "Composante supprimée avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression: {e}")
                QMessageBox.warning(self, "Erreur", f"Impossible de supprimer la composante:\n{str(e)}")


class MealComponentDialog(QDialog):
    """
    Dialogue pour créer/éditer une composante de repas.
    """

    def __init__(self, db_manager: DatabaseManager, component=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.component = component
        self.selected_foods = []

        self.setWindowTitle("Ajouter une composante" if component is None else "Modifier une composante")
        self.setMinimumSize(700, 600)
        self.init_ui()

        if component:
            self.load_component_data()

    def init_ui(self):
        """Initialise l'interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Nom de la composante
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nom de la composante:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Salade verte")
        name_layout.addWidget(self.name_input, stretch=1)
        layout.addLayout(name_layout)

        # Type de composante
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["entrée", "plat", "dessert", "accompagnement"])
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Sélection des aliments
        foods_label = QLabel("Aliments de la composante:")
        foods_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(foods_label)

        # Layout horizontal: disponibles | sélectionnés
        selection_layout = QHBoxLayout()

        # Colonne gauche: aliments disponibles
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Aliments disponibles:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un aliment...")
        self.search_input.textChanged.connect(self.filter_foods)
        left_layout.addWidget(self.search_input)

        self.available_list = QListWidget()
        self.available_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        left_layout.addWidget(self.available_list)

        add_food_btn = QPushButton("➡️ Ajouter →")
        add_food_btn.clicked.connect(self.add_food_to_component)
        left_layout.addWidget(add_food_btn)

        selection_layout.addLayout(left_layout, stretch=1)

        # Colonne droite: aliments sélectionnés
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Aliments de la composante:"))

        self.selected_table = QTableWidget()
        self.selected_table.setColumnCount(3)
        self.selected_table.setHorizontalHeaderLabels(["Aliment", "Quantité (g)", ""])
        self.selected_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.selected_table.setColumnWidth(1, 100)
        self.selected_table.setColumnWidth(2, 80)
        right_layout.addWidget(self.selected_table)

        selection_layout.addLayout(right_layout, stretch=1)

        layout.addLayout(selection_layout)

        # Résumé nutritionnel
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            background-color: #e8f4f8;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        """)
        self.update_summary()
        layout.addWidget(self.summary_label)

        # Boutons OK/Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_component)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Charger les aliments disponibles
        self.load_available_foods()

    def load_available_foods(self):
        """Charge tous les aliments disponibles."""
        try:
            self.all_foods = self.db_manager.get_all_foods()
            self.filter_foods()
        except Exception as e:
            logger.error(f"Erreur lors du chargement des aliments: {e}")

    def filter_foods(self):
        """Filtre les aliments selon la recherche."""
        search_text = self.search_input.text().lower()
        self.available_list.clear()

        for food in self.all_foods:
            if search_text in food.name.lower() or search_text in food.category.lower():
                self.available_list.addItem(f"{food.name} ({food.category})")

    def add_food_to_component(self):
        """Ajoute l'aliment sélectionné à la composante."""
        if not self.available_list.currentItem():
            return

        food_text = self.available_list.currentItem().text()
        food_name = food_text.split(" (")[0]

        # Trouver l'aliment correspondant
        food = next((f for f in self.all_foods if f.name == food_name), None)
        if not food:
            return

        # Vérifier s'il n'est pas déjà ajouté
        if any(f.id == food.id for f, _ in self.selected_foods):
            QMessageBox.information(self, "Info", "Cet aliment est déjà dans la composante.")
            return

        # Ajouter avec une quantité par défaut de 100g
        self.selected_foods.append((food, 100.0))
        self.update_selected_table()
        self.update_summary()

    def update_selected_table(self):
        """Met à jour la table des aliments sélectionnés."""
        self.selected_table.setRowCount(len(self.selected_foods))

        for row, (food, quantity) in enumerate(self.selected_foods):
            # Nom de l'aliment
            self.selected_table.setItem(row, 0, QTableWidgetItem(food.name))

            # Quantité éditable
            qty_spinbox = QSpinBox()
            qty_spinbox.setRange(10, 500)
            qty_spinbox.setValue(int(quantity))
            qty_spinbox.setSuffix(" g")
            qty_spinbox.valueChanged.connect(
                lambda val, r=row: self.update_food_quantity(r, val)
            )
            self.selected_table.setCellWidget(row, 1, qty_spinbox)

            # Bouton supprimer
            remove_btn = QPushButton("🗑️")
            remove_btn.setMaximumWidth(60)
            remove_btn.clicked.connect(lambda _, r=row: self.remove_food(r))
            self.selected_table.setCellWidget(row, 2, remove_btn)

    def update_food_quantity(self, row, value):
        """Met à jour la quantité d'un aliment."""
        if 0 <= row < len(self.selected_foods):
            food, _ = self.selected_foods[row]
            self.selected_foods[row] = (food, float(value))
            self.update_summary()

    def remove_food(self, row):
        """Supprime un aliment de la composante."""
        if 0 <= row < len(self.selected_foods):
            del self.selected_foods[row]
            self.update_selected_table()
            self.update_summary()

    def update_summary(self):
        """Met à jour le résumé nutritionnel."""
        if not self.selected_foods:
            self.summary_label.setText("Aucun aliment sélectionné")
            return

        total_calories = 0
        total_proteins = 0
        total_carbs = 0
        total_fats = 0

        for food, quantity in self.selected_foods:
            macros = food.calculate_for_quantity(quantity)
            total_calories += macros["calories"]
            total_proteins += macros["proteins"]
            total_carbs += macros["carbs"]
            total_fats += macros["fats"]

        summary_text = (
            f"<b>Résumé nutritionnel:</b> {len(self.selected_foods)} aliments | "
            f"{total_calories:.0f} kcal | "
            f"P: {total_proteins:.0f}g | "
            f"G: {total_carbs:.0f}g | "
            f"L: {total_fats:.0f}g"
        )
        self.summary_label.setText(summary_text)

    def load_component_data(self):
        """Charge les données de la composante à éditer."""
        if not self.component:
            return

        self.name_input.setText(self.component.name)

        # Trouver l'index du type
        index = self.type_combo.findText(self.component.component_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        # Charger les aliments
        self.selected_foods = list(self.component.foods)
        self.update_selected_table()
        self.update_summary()

    def save_component(self):
        """Sauvegarde la composante."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom de la composante est requis.")
            return

        if not self.selected_foods:
            QMessageBox.warning(self, "Erreur", "La composante doit contenir au moins un aliment.")
            return

        component_type = self.type_combo.currentText()

        try:
            if self.component:
                # Modification
                self.component.name = name
                self.component.component_type = component_type
                self.component.foods = self.selected_foods
                self.db_manager.update_meal_component(self.component)
                QMessageBox.information(self, "Succès", "Composante modifiée avec succès!")
            else:
                # Création
                new_component = MealComponent(
                    name=name,
                    component_type=component_type,
                    foods=self.selected_foods
                )
                self.db_manager.add_meal_component(new_component)
                QMessageBox.information(self, "Succès", "Composante ajoutée avec succès!")

            self.accept()

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")
            QMessageBox.warning(self, "Erreur", f"Impossible de sauvegarder la composante:\n{str(e)}")
