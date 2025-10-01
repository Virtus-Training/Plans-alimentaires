"""
SettingsPanel - Panneau de configuration des objectifs nutritionnels
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QPushButton, QComboBox, QCheckBox, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
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

        # Calories
        self.calories_slider, self.calories_label = self._create_slider_row(
            "Calories (kcal)",
            CALORIES_CONFIG["min"],
            CALORIES_CONFIG["max"],
            CALORIES_CONFIG["step"],
            CALORIES_CONFIG["default"]
        )
        layout.addLayout(self.calories_slider)

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

        group.setLayout(layout)
        self._update_distribution_label()

        return group

    def _create_slider_row(
        self, label_text: str, min_val: int, max_val: int,
        step: int, default: int
    ) -> tuple:
        """
        Crée une ligne avec label, slider et valeur.

        Returns:
            Tuple (layout, value_label)
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

        # Label de valeur
        value_label = QLabel(str(default))
        value_label.setMinimumWidth(50)
        value_label.setStyleSheet("font-weight: bold;")
        row_layout.addWidget(value_label)

        # Connecter le slider à la mise à jour du label
        slider.valueChanged.connect(
            lambda v: self._on_slider_changed(slider, value_label, step)
        )

        return row_layout, value_label

    def _on_slider_changed(self, slider: QSlider, label: QLabel, step: int):
        """Gère le changement de valeur d'un slider."""
        value = slider.value() * step
        label.setText(str(value))
        self._update_distribution_label()
        self.settings_changed.emit(self.get_settings())

    def _update_distribution_label(self):
        """Met à jour le label de répartition des macros."""
        target = self.get_nutrition_target()
        percentages = target.get_macro_percentages()

        text = (
            f"Répartition: Protéines {percentages['proteins']:.1f}% | "
            f"Glucides {percentages['carbs']:.1f}% | "
            f"Lipides {percentages['fats']:.1f}%"
        )
        self.distribution_label.setText(text)

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
        duration_layout.addWidget(QLabel("Durée du plan (jours):"))

        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(PLAN_DURATION_CONFIG["min"])
        self.duration_spinbox.setMaximum(PLAN_DURATION_CONFIG["max"])
        self.duration_spinbox.setValue(PLAN_DURATION_CONFIG["default"])
        self.duration_spinbox.valueChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        duration_layout.addWidget(self.duration_spinbox)
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

    def get_nutrition_target(self) -> NutritionTarget:
        """
        Retourne l'objectif nutritionnel actuel.

        Returns:
            NutritionTarget basé sur les valeurs des sliders
        """
        return NutritionTarget(
            calories=float(self.calories_label.text()),
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
            "duration_days": self.duration_spinbox.value(),
            "dietary_preferences": self.get_dietary_preferences()
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
                self.calories_slider.children()[1].setValue(
                    int(target.calories // CALORIES_CONFIG["step"])
                )
                self.proteins_slider.children()[1].setValue(
                    int(target.proteins // PROTEINS_CONFIG["step"])
                )
                self.carbs_slider.children()[1].setValue(
                    int(target.carbs // CARBS_CONFIG["step"])
                )
                self.fats_slider.children()[1].setValue(
                    int(target.fats // FATS_CONFIG["step"])
                )

        if "meal_count" in settings:
            index = MEAL_COUNT_OPTIONS.index(settings["meal_count"])
            self.meal_count_combo.setCurrentIndex(index)

        if "duration_days" in settings:
            self.duration_spinbox.setValue(settings["duration_days"])

        if "dietary_preferences" in settings:
            for tag, checkbox in self.preference_checkboxes.items():
                checkbox.setChecked(tag in settings["dietary_preferences"])
