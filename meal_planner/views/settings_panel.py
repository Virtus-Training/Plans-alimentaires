"""
SettingsPanel - Panneau de configuration des objectifs nutritionnels
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QPushButton, QComboBox, QCheckBox, QGroupBox, QSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator
from typing import Dict, List

from meal_planner.config import (
    CALORIES_CONFIG, PROTEINS_CONFIG, CARBS_CONFIG, FATS_CONFIG,
    MEAL_COUNT_OPTIONS, DEFAULT_MEAL_COUNT, DIETARY_PREFERENCES,
    PLAN_DURATION_CONFIG
)
from meal_planner.models.nutrition import NutritionTarget


class SettingsPanel(QWidget):
    """
    Panneau de configuration des paramètres du plan alimentaire.

    Signals:
        settings_changed: Émis quand les paramètres changent
        generate_requested: Émis quand l'utilisateur demande la génération
    """

    settings_changed = pyqtSignal(dict)
    generate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Titre
        title = QLabel("Paramètres du Plan Alimentaire")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Section Objectifs Macros
        macros_group = self._create_macros_group()
        layout.addWidget(macros_group)

        # Section Options
        options_group = self._create_options_group()
        layout.addWidget(options_group)

        # Section Critères de sélection
        criteria_group = self._create_criteria_group()
        layout.addWidget(criteria_group)

        # Bouton Générer
        self.generate_button = QPushButton("Générer le Plan Alimentaire")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.generate_button.clicked.connect(self.on_generate_clicked)
        layout.addWidget(self.generate_button)

        # Espaceur pour pousser tout vers le haut
        layout.addStretch()

    def _create_macros_group(self) -> QGroupBox:
        """Crée le groupe des sliders de macronutriments."""
        group = QGroupBox("Objectifs Nutritionnels")
        layout = QVBoxLayout()

        # Calories (calculées automatiquement)
        calories_layout = QHBoxLayout()
        calories_layout.addWidget(QLabel("Calories (kcal)"))
        self.calories_display = QLabel()
        self.calories_display.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        calories_layout.addWidget(self.calories_display)
        calories_layout.addStretch()
        layout.addLayout(calories_layout)

        # Protéines
        self.proteins_slider, self.proteins_label = self._create_slider_row(
            "Protéines (g)",
            PROTEINS_CONFIG["min"],
            PROTEINS_CONFIG["max"],
            PROTEINS_CONFIG["step"],
            PROTEINS_CONFIG["default"]
        )
        layout.addLayout(self.proteins_slider)

        # Glucides
        self.carbs_slider, self.carbs_label = self._create_slider_row(
            "Glucides (g)",
            CARBS_CONFIG["min"],
            CARBS_CONFIG["max"],
            CARBS_CONFIG["step"],
            CARBS_CONFIG["default"]
        )
        layout.addLayout(self.carbs_slider)

        # Lipides
        self.fats_slider, self.fats_label = self._create_slider_row(
            "Lipides (g)",
            FATS_CONFIG["min"],
            FATS_CONFIG["max"],
            FATS_CONFIG["step"],
            FATS_CONFIG["default"]
        )
        layout.addLayout(self.fats_slider)

        # Label de répartition
        self.distribution_label = QLabel()
        self.distribution_label.setStyleSheet("font-size: 11px; color: #666;")
        self.distribution_label.setWordWrap(True)
        layout.addWidget(self.distribution_label)

        # Total en pourcentage
        self.total_percentage_label = QLabel()
        self.total_percentage_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(self.total_percentage_label)

        group.setLayout(layout)

        # Initialiser l'affichage après la création de tous les widgets
        self._update_calories_and_distribution()

        return group

    def _create_slider_row(
        self, label_text: str, min_val: int, max_val: int,
        step: int, default: int
    ) -> tuple:
        """
        Crée une ligne avec label, slider et valeur éditable.

        Returns:
            Tuple (layout, value_input)
        """
        row_layout = QHBoxLayout()

        # Label
        label = QLabel(label_text)
        label.setMinimumWidth(120)
        row_layout.addWidget(label)

        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val // step)
        slider.setMaximum(max_val // step)
        slider.setValue(default // step)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval((max_val - min_val) // (step * 10))
        row_layout.addWidget(slider, stretch=3)

        # Input éditable de valeur
        value_input = QLineEdit(str(default))
        value_input.setMinimumWidth(50)
        value_input.setMaximumWidth(70)
        value_input.setStyleSheet("font-weight: bold; padding: 2px;")
        value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Validation pour n'accepter que des entiers
        validator = QIntValidator(min_val, max_val)
        value_input.setValidator(validator)

        row_layout.addWidget(value_input)

        # Connecter le slider à la mise à jour de l'input
        slider.valueChanged.connect(
            lambda v: self._on_macro_slider_changed(slider, value_input, step)
        )

        # Connecter l'input à la mise à jour du slider
        value_input.editingFinished.connect(
            lambda: self._on_macro_input_changed(slider, value_input, step)
        )

        return row_layout, value_input

    def _on_macro_slider_changed(self, slider: QSlider, input_field: QLineEdit, step: int):
        """Gère le changement de valeur d'un slider de macro."""
        value = slider.value() * step
        input_field.blockSignals(True)
        input_field.setText(str(value))
        input_field.blockSignals(False)
        self._update_calories_and_distribution()
        self.settings_changed.emit(self.get_settings())

    def _on_macro_input_changed(self, slider: QSlider, input_field: QLineEdit, step: int):
        """Gère le changement de valeur d'un input de macro."""
        try:
            value = int(input_field.text())
            slider.blockSignals(True)
            slider.setValue(value // step)
            slider.blockSignals(False)
            self._update_calories_and_distribution()
            self.settings_changed.emit(self.get_settings())
        except ValueError:
            # Si la valeur n'est pas valide, remettre la valeur du slider
            value = slider.value() * step
            input_field.setText(str(value))

    def _calculate_calories(self) -> int:
        """Calcule les calories totales basées sur les macros."""
        try:
            proteins = int(self.proteins_label.text())
            carbs = int(self.carbs_label.text())
            fats = int(self.fats_label.text())
            return (proteins * 4) + (carbs * 4) + (fats * 9)
        except (ValueError, AttributeError):
            return 0

    def _update_calories_and_distribution(self):
        """Met à jour l'affichage des calories et de la distribution."""
        calories = self._calculate_calories()
        self.calories_display.setText(f"{calories} kcal")
        self._update_distribution_label()

    def _update_distribution_label(self):
        """Met à jour le label de répartition des macros et le total."""
        target = self.get_nutrition_target()
        percentages = target.get_macro_percentages()

        total = percentages['proteins'] + percentages['carbs'] + percentages['fats']

        text = (
            f"Répartition: Protéines {percentages['proteins']:.1f}% | "
            f"Glucides {percentages['carbs']:.1f}% | "
            f"Lipides {percentages['fats']:.1f}%"
        )
        self.distribution_label.setText(text)

        # Mise à jour du total avec code couleur
        if 95 <= total <= 105:
            color = "#4CAF50"  # Vert si proche de 100%
            status = "✓"
        elif 90 <= total <= 110:
            color = "#FF9800"  # Orange si modérément proche
            status = "⚠"
        else:
            color = "#F44336"  # Rouge si loin de 100%
            status = "✗"

        self.total_percentage_label.setText(f"{status} Total: {total:.1f}%")
        self.total_percentage_label.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color};")

    def _create_options_group(self) -> QGroupBox:
        """Crée le groupe des options."""
        group = QGroupBox("Options")
        layout = QVBoxLayout()

        # Nombre de repas
        meal_count_layout = QHBoxLayout()
        meal_count_layout.addWidget(QLabel("Nombre de repas par jour:"))

        self.meal_count_combo = QComboBox()
        for count in MEAL_COUNT_OPTIONS:
            self.meal_count_combo.addItem(f"{count} repas", count)
        self.meal_count_combo.setCurrentIndex(
            MEAL_COUNT_OPTIONS.index(DEFAULT_MEAL_COUNT)
        )
        self.meal_count_combo.currentIndexChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        meal_count_layout.addWidget(self.meal_count_combo)
        meal_count_layout.addStretch()
        layout.addLayout(meal_count_layout)

        # Durée du plan
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Durée du plan:"))

        self.duration_combo = QComboBox()
        duration_options = [
            (1, "1 semaine"),
            (4, "4 semaines"),
            (8, "8 semaines"),
            (12, "12 semaines")
        ]
        for weeks, label in duration_options:
            self.duration_combo.addItem(label, weeks * 7)  # Stocker en jours
        self.duration_combo.setCurrentIndex(0)  # 1 semaine par défaut
        self.duration_combo.currentIndexChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        duration_layout.addWidget(self.duration_combo)
        duration_layout.addStretch()
        layout.addLayout(duration_layout)

        # Préférences diététiques
        layout.addWidget(QLabel("Préférences alimentaires:"))

        self.preference_checkboxes = {}
        for tag, label_text in DIETARY_PREFERENCES.items():
            checkbox = QCheckBox(label_text)
            checkbox.stateChanged.connect(
                lambda: self.settings_changed.emit(self.get_settings())
            )
            self.preference_checkboxes[tag] = checkbox
            layout.addWidget(checkbox)

        group.setLayout(layout)
        return group

    def _create_criteria_group(self) -> QGroupBox:
        """Crée le groupe des critères de sélection (prix, santé, variété)."""
        group = QGroupBox("Critères de Sélection")
        layout = QVBoxLayout()

        # Slider Prix/repas
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Budget/repas:"))

        self.price_slider = QSlider(Qt.Orientation.Horizontal)
        self.price_slider.setMinimum(1)
        self.price_slider.setMaximum(10)
        self.price_slider.setValue(5)
        self.price_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.price_slider.setTickInterval(1)
        price_layout.addWidget(self.price_slider, stretch=3)

        self.price_label = QLabel("Moyen")
        self.price_label.setMinimumWidth(80)
        self.price_label.setStyleSheet("font-weight: bold;")
        self.price_slider.valueChanged.connect(self._update_price_label)
        price_layout.addWidget(self.price_label)

        layout.addLayout(price_layout)

        # Slider Healthy
        healthy_layout = QHBoxLayout()
        healthy_layout.addWidget(QLabel("Indice santé:"))

        self.healthy_slider = QSlider(Qt.Orientation.Horizontal)
        self.healthy_slider.setMinimum(1)
        self.healthy_slider.setMaximum(10)
        self.healthy_slider.setValue(5)
        self.healthy_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.healthy_slider.setTickInterval(1)
        healthy_layout.addWidget(self.healthy_slider, stretch=3)

        self.healthy_label = QLabel("5/10")
        self.healthy_label.setMinimumWidth(80)
        self.healthy_label.setStyleSheet("font-weight: bold;")
        self.healthy_slider.valueChanged.connect(self._update_healthy_label)
        healthy_layout.addWidget(self.healthy_label)

        layout.addLayout(healthy_layout)

        # Slider Variété
        variety_layout = QHBoxLayout()
        variety_layout.addWidget(QLabel("Variété:"))

        self.variety_slider = QSlider(Qt.Orientation.Horizontal)
        self.variety_slider.setMinimum(1)
        self.variety_slider.setMaximum(10)
        self.variety_slider.setValue(5)
        self.variety_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.variety_slider.setTickInterval(1)
        variety_layout.addWidget(self.variety_slider, stretch=3)

        self.variety_label = QLabel("Équilibré")
        self.variety_label.setMinimumWidth(80)
        self.variety_label.setStyleSheet("font-weight: bold;")
        self.variety_slider.valueChanged.connect(self._update_variety_label)
        variety_layout.addWidget(self.variety_label)

        layout.addLayout(variety_layout)

        # Descriptions
        desc_label = QLabel(
            "<small><i>"
            "• Budget: Contrôle le prix moyen par repas<br>"
            "• Santé: Privilégie les aliments sains (1=peu, 10=très sain)<br>"
            "• Variété: Inclut des aliments rares (1=commun, 10=exotique)"
            "</i></small>"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-top: 5px;")
        layout.addWidget(desc_label)

        # Connecter les sliders aux changements de settings
        self.price_slider.valueChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        self.healthy_slider.valueChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        self.variety_slider.valueChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )

        group.setLayout(layout)
        return group

    def _update_price_label(self, value: int):
        """Met à jour le label du slider de prix."""
        labels = {
            1: "Très bas",
            2: "Bas",
            3: "Économique",
            4: "Raisonnable",
            5: "Moyen",
            6: "Modéré",
            7: "Élevé",
            8: "Cher",
            9: "Très cher",
            10: "Premium"
        }
        self.price_label.setText(labels.get(value, "Moyen"))

    def _update_healthy_label(self, value: int):
        """Met à jour le label du slider de santé."""
        self.healthy_label.setText(f"{value}/10")
        # Changer la couleur selon le niveau
        if value >= 8:
            color = "#4CAF50"  # Vert
        elif value >= 5:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Rouge
        self.healthy_label.setStyleSheet(f"font-weight: bold; color: {color};")

    def _update_variety_label(self, value: int):
        """Met à jour le label du slider de variété."""
        labels = {
            1: "Basique",
            2: "Simple",
            3: "Classique",
            4: "Standard",
            5: "Équilibré",
            6: "Varié",
            7: "Diversifié",
            8: "Original",
            9: "Exotique",
            10: "Aventureux"
        }
        self.variety_label.setText(labels.get(value, "Équilibré"))

    def get_nutrition_target(self) -> NutritionTarget:
        """
        Retourne l'objectif nutritionnel actuel.

        Returns:
            NutritionTarget basé sur les valeurs des inputs
        """
        return NutritionTarget(
            calories=float(self._calculate_calories()),
            proteins=float(self.proteins_label.text()),
            carbs=float(self.carbs_label.text()),
            fats=float(self.fats_label.text())
        )

    def get_settings(self) -> Dict:
        """
        Retourne tous les paramètres actuels.

        Returns:
            Dict contenant tous les paramètres
        """
        return {
            "nutrition_target": self.get_nutrition_target(),
            "meal_count": self.meal_count_combo.currentData(),
            "duration_days": self.duration_combo.currentData(),
            "dietary_preferences": self.get_dietary_preferences(),
            "price_level": self.price_slider.value(),
            "health_index": self.healthy_slider.value(),
            "variety_level": self.variety_slider.value()
        }

    def get_dietary_preferences(self) -> List[str]:
        """
        Retourne la liste des préférences diététiques sélectionnées.

        Returns:
            Liste des tags sélectionnés
        """
        return [
            tag for tag, checkbox in self.preference_checkboxes.items()
            if checkbox.isChecked()
        ]

    def on_generate_clicked(self):
        """Gère le clic sur le bouton Générer."""
        self.generate_requested.emit()

    def set_settings(self, settings: Dict):
        """
        Applique des paramètres au panneau.

        Args:
            settings: Dict contenant les paramètres à appliquer
        """
        if "nutrition_target" in settings:
            target = settings["nutrition_target"]
            if isinstance(target, NutritionTarget):
                self.proteins_slider.children()[1].setValue(
                    int(target.proteins // PROTEINS_CONFIG["step"])
                )
                self.carbs_slider.children()[1].setValue(
                    int(target.carbs // CARBS_CONFIG["step"])
                )
                self.fats_slider.children()[1].setValue(
                    int(target.fats // FATS_CONFIG["step"])
                )
                self._update_calories_and_distribution()

        if "meal_count" in settings:
            index = MEAL_COUNT_OPTIONS.index(settings["meal_count"])
            self.meal_count_combo.setCurrentIndex(index)

        if "duration_days" in settings:
            days = settings["duration_days"]
            # Trouver l'index correspondant
            for i in range(self.duration_combo.count()):
                if self.duration_combo.itemData(i) == days:
                    self.duration_combo.setCurrentIndex(i)
                    break

        if "dietary_preferences" in settings:
            for tag, checkbox in self.preference_checkboxes.items():
                checkbox.setChecked(tag in settings["dietary_preferences"])
