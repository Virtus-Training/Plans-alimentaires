"""
SettingsPanel - Panneau de configuration des objectifs nutritionnels
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QPushButton, QComboBox, QCheckBox, QGroupBox, QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator
from typing import Dict, List

from meal_planner.config import (
    CALORIES_CONFIG, PROTEINS_CONFIG, CARBS_CONFIG, FATS_CONFIG,
    MEAL_COUNT_OPTIONS, DEFAULT_MEAL_COUNT, DIETARY_PREFERENCES,
    PLAN_DURATION_CONFIG, GENERATION_MODES
)
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.utils.ui_helpers import create_icon_label


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
        # Définir une largeur minimale pour éviter la compression
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Titre avec icône
        title_layout = QHBoxLayout()
        title_icon = create_icon_label("target", 28)
        title_layout.addWidget(title_icon)

        title = QLabel("Paramètres du Plan")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding-left: 8px;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Section Mode de Génération
        mode_group = self._create_generation_mode_group()
        layout.addWidget(mode_group)

        # Section Objectifs Macros
        macros_group = self._create_macros_group()
        layout.addWidget(macros_group)

        # Section Options
        options_group = self._create_options_group()
        layout.addWidget(options_group)

        # Section Critères de sélection
        criteria_group = self._create_criteria_group()
        layout.addWidget(criteria_group)

        # Bouton Générer (version compacte)
        self.generate_button = QPushButton("✨ Générer le Plan")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 16px;
                border-radius: 6px;
                border: none;
                min-height: 36px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
        """)
        self.generate_button.setToolTip("Générer un plan alimentaire basé sur vos objectifs")
        self.generate_button.clicked.connect(self.on_generate_clicked)
        layout.addWidget(self.generate_button)

        # Espaceur pour pousser tout vers le haut
        layout.addStretch()

    def _create_generation_mode_group(self) -> QGroupBox:
        """Crée le groupe de sélection du mode de génération."""
        group = QGroupBox("🎨 Mode de Génération")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #2c3e50;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Combo de sélection du mode (sans label descriptif pour gagner de la place)
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)

        mode_icon = create_icon_label("lightbulb", 18)
        mode_layout.addWidget(mode_icon)

        mode_label = QLabel("Mode :")
        mode_label.setStyleSheet("font-weight: 600; color: #555; min-width: 60px;")
        mode_layout.addWidget(mode_label)

        self.generation_mode_combo = QComboBox()
        self.generation_mode_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #3498db;
                border-radius: 5px;
                background: white;
                font-size: 12px;
                min-height: 28px;
            }
            QComboBox:hover {
                border: 2px solid #2980b9;
                background: #ecf9ff;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #3498db;
                margin-right: 8px;
            }
        """)

        # Ajouter les modes
        for mode_key, mode_label in GENERATION_MODES.items():
            self.generation_mode_combo.addItem(mode_label, mode_key)

        # Par défaut : mode "Par Aliments"
        self.generation_mode_combo.setCurrentIndex(0)

        self.generation_mode_combo.currentIndexChanged.connect(
            lambda: self._on_generation_mode_changed()
        )
        mode_layout.addWidget(self.generation_mode_combo, stretch=1)

        layout.addLayout(mode_layout)

        # Zone d'info dynamique selon le mode (version compacte)
        self.mode_info_label = QLabel()
        self.mode_info_label.setWordWrap(True)
        self.mode_info_label.setStyleSheet("""
            background-color: #e8f4f8;
            padding: 6px 8px;
            border-radius: 4px;
            border-left: 3px solid #3498db;
            color: #2c3e50;
            font-size: 10px;
        """)
        layout.addWidget(self.mode_info_label)

        # Mettre à jour l'info initiale
        self._update_mode_info()

        group.setLayout(layout)
        return group

    def _on_generation_mode_changed(self):
        """Gère le changement de mode de génération."""
        self._update_mode_info()
        self.settings_changed.emit(self.get_settings())

    def _update_mode_info(self):
        """Met à jour le texte d'information selon le mode sélectionné."""
        mode_key = self.generation_mode_combo.currentData()

        mode_descriptions = {
            "food": (
                "<b>Par Aliments:</b> Sélection optimisée par algorithme (ILP/hybride)."
            ),
            "preset": (
                "<b>Repas Complets:</b> Utilise des repas pré-composés. "
                "<i>(Nécessite des repas prédéfinis)</i>"
            ),
            "components": (
                "<b>Entrée/Plat/Dessert:</b> Structure en 3 composantes pour déjeuner/dîner."
            ),
            "categories": (
                "<b>Par Catégories:</b> Règles de composition personnalisables."
            )
        }

        self.mode_info_label.setText(mode_descriptions.get(mode_key, ""))

    def _create_macros_group(self) -> QGroupBox:
        """Crée le groupe des sliders de macronutriments."""
        group = QGroupBox("🎯 Objectifs Nutritionnels")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #2c3e50;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Calories (calculées automatiquement) avec icône
        calories_layout = QHBoxLayout()
        cal_icon = create_icon_label("fire", 18)
        calories_layout.addWidget(cal_icon)

        cal_label = QLabel("Calories")
        cal_label.setStyleSheet("font-weight: 600; color: #555;")
        cal_label.setToolTip("Calculées automatiquement : (Protéines × 4) + (Glucides × 4) + (Lipides × 9)")
        calories_layout.addWidget(cal_label)

        calories_layout.addStretch()

        self.calories_display = QLabel()
        self.calories_display.setToolTip("Objectif calorique journalier total")
        self.calories_display.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: #e74c3c;
            background-color: #fff;
            padding: 4px 12px;
            border-radius: 4px;
            border: 1px solid #e74c3c;
        """)
        calories_layout.addWidget(self.calories_display)
        layout.addLayout(calories_layout)

        # Protéines avec icône
        self.proteins_slider, self.proteins_label = self._create_slider_row(
            "Protéines",
            PROTEINS_CONFIG["min"],
            PROTEINS_CONFIG["max"],
            PROTEINS_CONFIG["step"],
            PROTEINS_CONFIG["default"],
            icon="protein",
            color="#3498db"
        )
        layout.addLayout(self.proteins_slider)

        # Glucides avec icône
        self.carbs_slider, self.carbs_label = self._create_slider_row(
            "Glucides",
            CARBS_CONFIG["min"],
            CARBS_CONFIG["max"],
            CARBS_CONFIG["step"],
            CARBS_CONFIG["default"],
            icon="carbs",
            color="#f39c12"
        )
        layout.addLayout(self.carbs_slider)

        # Lipides avec icône
        self.fats_slider, self.fats_label = self._create_slider_row(
            "Lipides",
            FATS_CONFIG["min"],
            FATS_CONFIG["max"],
            FATS_CONFIG["step"],
            FATS_CONFIG["default"],
            icon="fat",
            color="#9b59b6"
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
        step: int, default: int, icon: str = None, color: str = "#555"
    ) -> tuple:
        """
        Crée une ligne avec label, slider et valeur éditable.

        Returns:
            Tuple (layout, value_input)
        """
        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        # Icône (si fournie)
        if icon:
            icon_label = create_icon_label(icon, 16)
            row_layout.addWidget(icon_label)

        # Label
        label = QLabel(label_text)
        label.setMinimumWidth(75)
        label.setStyleSheet(f"font-weight: 600; color: {color};")
        row_layout.addWidget(label)

        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val // step)
        slider.setMaximum(max_val // step)
        slider.setValue(default // step)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval((max_val - min_val) // (step * 10))
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #bbb;
                background: #fff;
                height: 8px;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {color};
                border: 2px solid {color};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #fff;
            }}
            QSlider::sub-page:horizontal {{
                background: {color};
                border-radius: 4px;
            }}
        """)
        row_layout.addWidget(slider, stretch=3)

        # Input éditable de valeur
        value_input = QLineEdit(str(default))
        value_input.setMinimumWidth(55)
        value_input.setMaximumWidth(75)
        value_input.setStyleSheet(f"""
            font-weight: bold;
            padding: 6px;
            border: 2px solid {color};
            border-radius: 4px;
            background-color: #fff;
            color: {color};
        """)
        value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Validation pour n'accepter que des entiers
        validator = QIntValidator(min_val, max_val)
        value_input.setValidator(validator)

        row_layout.addWidget(value_input)

        # Unité
        unit_label = QLabel("g")
        unit_label.setStyleSheet("color: #999; font-size: 11px;")
        row_layout.addWidget(unit_label)

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
        group = QGroupBox("⚙️ Options du Plan")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #2c3e50;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Première ligne: Repas/jour et Durée
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)

        # Repas/jour
        meal_icon = create_icon_label("plate", 16)
        row1_layout.addWidget(meal_icon)

        meal_label = QLabel("Repas/jour:")
        meal_label.setStyleSheet("font-weight: 600; color: #555;")
        meal_label.setMinimumWidth(75)
        row1_layout.addWidget(meal_label)

        self.meal_count_combo = QComboBox()
        self.meal_count_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
        """)
        for count in MEAL_COUNT_OPTIONS:
            self.meal_count_combo.addItem(f"{count} repas", count)
        self.meal_count_combo.setCurrentIndex(
            MEAL_COUNT_OPTIONS.index(DEFAULT_MEAL_COUNT)
        )
        self.meal_count_combo.currentIndexChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        row1_layout.addWidget(self.meal_count_combo)

        # Espaceur
        row1_layout.addSpacing(20)

        # Durée
        duration_icon = create_icon_label("calendar", 16)
        row1_layout.addWidget(duration_icon)

        duration_label = QLabel("Durée:")
        duration_label.setStyleSheet("font-weight: 600; color: #555;")
        duration_label.setMinimumWidth(50)
        row1_layout.addWidget(duration_label)

        self.duration_combo = QComboBox()
        self.duration_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
        """)
        duration_options = [
            (1, "1 semaine"),
            (4, "4 semaines"),
            (8, "8 semaines"),
            (12, "12 semaines")
        ]
        for weeks, label in duration_options:
            self.duration_combo.addItem(label, weeks * 7)
        self.duration_combo.setCurrentIndex(0)
        self.duration_combo.currentIndexChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        row1_layout.addWidget(self.duration_combo)
        row1_layout.addStretch()

        layout.addLayout(row1_layout)

        # Deuxième ligne: Objectif et Whey
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)

        # Objectif
        goal_icon = create_icon_label("target", 16)
        row2_layout.addWidget(goal_icon)

        goal_label = QLabel("Objectif:")
        goal_label.setStyleSheet("font-weight: 600; color: #555;")
        goal_label.setMinimumWidth(75)
        row2_layout.addWidget(goal_label)

        self.goal_combo = QComboBox()
        self.goal_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
        """)
        self.goal_combo.addItem("Prise de poids", "gain")
        self.goal_combo.addItem("Perte de poids", "loss")
        self.goal_combo.addItem("Rééquilibrage", "balance")
        self.goal_combo.setCurrentIndex(2)
        self.goal_combo.currentIndexChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        row2_layout.addWidget(self.goal_combo)

        # Espaceur
        row2_layout.addSpacing(20)

        # Whey
        whey_icon = create_icon_label("protein", 16)
        row2_layout.addWidget(whey_icon)

        whey_label = QLabel("Whey:")
        whey_label.setStyleSheet("font-weight: 600; color: #555;")
        whey_label.setMinimumWidth(50)
        row2_layout.addWidget(whey_label)

        self.whey_combo = QComboBox()
        self.whey_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
        """)
        self.whey_combo.addItem("Oui", True)
        self.whey_combo.addItem("Non", False)
        self.whey_combo.setCurrentIndex(1)
        self.whey_combo.currentIndexChanged.connect(
            lambda: self.settings_changed.emit(self.get_settings())
        )
        row2_layout.addWidget(self.whey_combo)
        row2_layout.addStretch()

        layout.addLayout(row2_layout)

        # Préférences diététiques avec icône
        pref_header = QHBoxLayout()
        apple_icon = create_icon_label("apple", 16)
        pref_header.addWidget(apple_icon)

        pref_label = QLabel("Préférences alimentaires:")
        pref_label.setStyleSheet("font-weight: 600; color: #555; padding-top: 5px;")
        pref_header.addWidget(pref_label)
        pref_header.addStretch()
        layout.addLayout(pref_header)

        # Organisation des préférences en grille (3 colonnes)
        self.preference_checkboxes = {}
        prefs_list = list(DIETARY_PREFERENCES.items())

        # Créer une grille pour les préférences
        prefs_grid = QGridLayout()
        prefs_grid.setSpacing(10)
        prefs_grid.setColumnStretch(0, 1)
        prefs_grid.setColumnStretch(1, 1)
        prefs_grid.setColumnStretch(2, 1)

        # Distribuer les préférences sur 3 colonnes
        for idx, (tag, label_text) in enumerate(prefs_list):
            row = idx // 3
            col = idx % 3

            checkbox = QCheckBox(label_text)
            checkbox.setStyleSheet("""
                QCheckBox {
                    padding: 4px;
                    spacing: 6px;
                    font-size: 12px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 2px solid #bbb;
                }
                QCheckBox::indicator:checked {
                    background-color: #27ae60;
                    border: 2px solid #27ae60;
                }
            """)
            checkbox.stateChanged.connect(
                lambda: self.settings_changed.emit(self.get_settings())
            )
            self.preference_checkboxes[tag] = checkbox
            prefs_grid.addWidget(checkbox, row, col)

        layout.addLayout(prefs_grid)

        group.setLayout(layout)
        return group

    def _create_criteria_group(self) -> QGroupBox:
        """Crée le groupe des critères de sélection (prix, santé, variété)."""
        group = QGroupBox("📊 Critères de Sélection")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #2c3e50;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Slider Prix/repas avec icône
        price_layout = QHBoxLayout()
        price_icon = create_icon_label("energy", 16)
        price_layout.addWidget(price_icon)

        price_text_label = QLabel("Budget:")
        price_text_label.setStyleSheet("font-weight: 600; color: #555; min-width: 85px;")
        price_layout.addWidget(price_text_label)

        self.price_slider = QSlider(Qt.Orientation.Horizontal)
        self.price_slider.setMinimum(1)
        self.price_slider.setMaximum(10)
        self.price_slider.setValue(5)
        self.price_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.price_slider.setTickInterval(1)
        self.price_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #fff;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #f39c12;
                border: 2px solid #f39c12;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #fff;
            }
            QSlider::sub-page:horizontal {
                background: #f39c12;
                border-radius: 4px;
            }
        """)
        price_layout.addWidget(self.price_slider, stretch=3)

        self.price_label = QLabel("Moyen")
        self.price_label.setMinimumWidth(90)
        self.price_label.setStyleSheet("""
            font-weight: bold;
            color: #f39c12;
            background: white;
            padding: 4px 10px;
            border: 2px solid #f39c12;
            border-radius: 4px;
        """)
        self.price_slider.valueChanged.connect(self._update_price_label)
        price_layout.addWidget(self.price_label)

        layout.addLayout(price_layout)

        # Slider Healthy avec icône
        healthy_layout = QHBoxLayout()
        healthy_icon = create_icon_label("nutrition", 16)
        healthy_layout.addWidget(healthy_icon)

        healthy_text_label = QLabel("Santé:")
        healthy_text_label.setStyleSheet("font-weight: 600; color: #555; min-width: 85px;")
        healthy_layout.addWidget(healthy_text_label)

        self.healthy_slider = QSlider(Qt.Orientation.Horizontal)
        self.healthy_slider.setMinimum(1)
        self.healthy_slider.setMaximum(10)
        self.healthy_slider.setValue(5)
        self.healthy_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.healthy_slider.setTickInterval(1)
        self.healthy_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #fff;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #27ae60;
                border: 2px solid #27ae60;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #fff;
            }
            QSlider::sub-page:horizontal {
                background: #27ae60;
                border-radius: 4px;
            }
        """)
        healthy_layout.addWidget(self.healthy_slider, stretch=3)

        self.healthy_label = QLabel("5/10")
        self.healthy_label.setMinimumWidth(90)
        self.healthy_label.setStyleSheet("""
            font-weight: bold;
            background: white;
            padding: 4px 10px;
            border: 2px solid #27ae60;
            border-radius: 4px;
        """)
        self.healthy_slider.valueChanged.connect(self._update_healthy_label)
        healthy_layout.addWidget(self.healthy_label)

        layout.addLayout(healthy_layout)

        # Slider Variété avec icône
        variety_layout = QHBoxLayout()
        variety_icon = create_icon_label("lightbulb", 16)
        variety_layout.addWidget(variety_icon)

        variety_text_label = QLabel("Variété:")
        variety_text_label.setStyleSheet("font-weight: 600; color: #555; min-width: 85px;")
        variety_layout.addWidget(variety_text_label)

        self.variety_slider = QSlider(Qt.Orientation.Horizontal)
        self.variety_slider.setMinimum(1)
        self.variety_slider.setMaximum(10)
        self.variety_slider.setValue(5)
        self.variety_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.variety_slider.setTickInterval(1)
        self.variety_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #fff;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #9b59b6;
                border: 2px solid #9b59b6;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #fff;
            }
            QSlider::sub-page:horizontal {
                background: #9b59b6;
                border-radius: 4px;
            }
        """)
        variety_layout.addWidget(self.variety_slider, stretch=3)

        self.variety_label = QLabel("Équilibré")
        self.variety_label.setMinimumWidth(90)
        self.variety_label.setStyleSheet("""
            font-weight: bold;
            color: #9b59b6;
            background: white;
            padding: 4px 10px;
            border: 2px solid #9b59b6;
            border-radius: 4px;
        """)
        self.variety_slider.valueChanged.connect(self._update_variety_label)
        variety_layout.addWidget(self.variety_label)

        layout.addLayout(variety_layout)

        # Descriptions compactes
        desc_label = QLabel("<small><i>Budget • Santé • Variété (commun↔rare)</i></small>")
        desc_label.setStyleSheet("color: #666; margin-top: 3px; font-size: 9px;")
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
            "variety_level": self.variety_slider.value(),
            "goal": self.goal_combo.currentData(),
            "include_whey": self.whey_combo.currentData(),
            "generation_mode": self.generation_mode_combo.currentData()
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
