"""
MealPlanDisplay - Affichage du plan alimentaire généré
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGroupBox, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional

from meal_planner.models.meal_plan import MealPlan


class MealPlanDisplay(QWidget):
    """
    Widget d'affichage du plan alimentaire.

    Signals:
        meal_regenerate_requested: Émis quand l'utilisateur veut régénérer un repas
    """

    meal_regenerate_requested = pyqtSignal(int, int)  # day, meal_index

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plan: Optional[MealPlan] = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Titre
        self.title_label = QLabel("Plan Alimentaire")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Zone de scroll pour le contenu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Widget de contenu
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(15)

        # Message initial
        self.empty_label = QLabel(
            "Aucun plan alimentaire généré.\n\n"
            "Configurez vos objectifs et cliquez sur\n"
            "\"Générer le Plan Alimentaire\" pour commencer."
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: #888; font-size: 14px; padding: 50px;"
        )
        self.content_layout.addWidget(self.empty_label)
        self.content_layout.addStretch()

        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)

    def display_meal_plan(self, meal_plan: MealPlan):
        """
        Affiche un plan alimentaire.

        Args:
            meal_plan: Le plan alimentaire à afficher
        """
        self.current_plan = meal_plan

        # Masquer le message vide avant de nettoyer
        if self.empty_label:
            self.empty_label.hide()

        # Effacer le contenu précédent
        self._clear_content()

        # Mettre à jour le titre
        self.title_label.setText(
            f"Plan Alimentaire - {meal_plan.duration_days} jour(s)"
        )

        # Afficher chaque jour
        for day in range(1, meal_plan.duration_days + 1):
            day_widget = self._create_day_widget(day)
            self.content_layout.addWidget(day_widget)

        self.content_layout.addStretch()

    def _clear_content(self):
        """Efface le contenu de l'affichage."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget() and item.widget() != self.empty_label:
                item.widget().deleteLater()

    def _create_day_widget(self, day: int) -> QGroupBox:
        """
        Crée un widget pour un jour du plan.

        Args:
            day: Numéro du jour

        Returns:
            Widget représentant le jour
        """
        if not self.current_plan:
            return QGroupBox()

        day_meals = self.current_plan.get_meals_for_day(day)
        day_totals = self.current_plan.calculate_daily_totals(day)

        # Groupe pour le jour
        group = QGroupBox(f"Jour {day}")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()

        # Afficher chaque repas
        for meal in day_meals:
            meal_widget = self._create_meal_widget(meal)
            layout.addWidget(meal_widget)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Totaux du jour
        totals_label = QLabel(
            f"<b>Total journalier:</b> "
            f"{day_totals['calories']:.0f} kcal | "
            f"P: {day_totals['proteins']:.1f}g | "
            f"G: {day_totals['carbs']:.1f}g | "
            f"L: {day_totals['fats']:.1f}g"
        )
        totals_label.setStyleSheet("color: #2196F3; font-size: 13px; padding: 5px;")
        layout.addWidget(totals_label)

        # Validation
        target = self.current_plan.nutrition_target
        validation_text = self._get_validation_text(day_totals, target)
        if validation_text:
            validation_label = QLabel(validation_text)
            validation_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
            layout.addWidget(validation_label)

        group.setLayout(layout)
        return group

    def _create_meal_widget(self, meal) -> QFrame:
        """
        Crée un widget pour un repas.

        Args:
            meal: Le repas à afficher

        Returns:
            Widget représentant le repas
        """
        # Couleurs et icônes selon le type de repas
        meal_styles = {
            "breakfast": {
                "color": "#FFF3E0",
                "border": "#FF9800",
                "icon": "☀",
                "name": "Petit-déjeuner"
            },
            "lunch": {
                "color": "#E3F2FD",
                "border": "#2196F3",
                "icon": "🍽",
                "name": "Déjeuner"
            },
            "dinner": {
                "color": "#F3E5F5",
                "border": "#9C27B0",
                "icon": "🌙",
                "name": "Dîner"
            },
            "snack": {
                "color": "#E8F5E9",
                "border": "#4CAF50",
                "icon": "🍎",
                "name": "Collation"
            },
            "afternoon_snack": {
                "color": "#FFF9C4",
                "border": "#FBC02D",
                "icon": "☕",
                "name": "Goûter"
            },
            "morning_snack": {
                "color": "#E8F5E9",
                "border": "#66BB6A",
                "icon": "🥐",
                "name": "Collation matinale"
            },
            "evening_snack": {
                "color": "#E0F2F1",
                "border": "#26A69A",
                "icon": "🥛",
                "name": "Collation soirée"
            }
        }

        style = meal_styles.get(meal.meal_type, {
            "color": "#F5F5F5",
            "border": "#9E9E9E",
            "icon": "🍴",
            "name": meal.meal_type
        })

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {style['color']};
                border-left: 4px solid {style['border']};
                border-radius: 8px;
                padding: 12px;
                margin: 5px 0;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        # En-tête du repas avec icône
        header_layout = QHBoxLayout()

        icon_label = QLabel(style['icon'])
        icon_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(icon_label)

        meal_name_label = QLabel(f"<b>{style['name']}</b>")
        meal_name_label.setStyleSheet(f"font-size: 14px; color: {style['border']};")
        header_layout.addWidget(meal_name_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Liste des aliments avec style amélioré
        if meal.foods:
            foods_container = QWidget()
            foods_layout = QVBoxLayout(foods_container)
            foods_layout.setContentsMargins(20, 5, 5, 5)
            foods_layout.setSpacing(4)

            for food, quantity in meal.foods:
                food_macros = food.calculate_for_quantity(quantity)

                # Widget pour chaque aliment
                food_widget = QWidget()
                food_layout = QHBoxLayout(food_widget)
                food_layout.setContentsMargins(0, 0, 0, 0)

                # Nom et quantité
                name_label = QLabel(f"<b>{food.name}</b> · {quantity:.0f}g")
                name_label.setStyleSheet("font-size: 12px; color: #333;")
                food_layout.addWidget(name_label)

                food_layout.addStretch()

                # Macros en badges
                macros_label = QLabel(
                    f"<span style='background-color: #fff; padding: 2px 6px; border-radius: 3px; margin: 0 2px;'>"
                    f"{food_macros['calories']:.0f} kcal</span> "
                    f"<span style='background-color: #fff; padding: 2px 6px; border-radius: 3px; margin: 0 2px;'>"
                    f"P {food_macros['proteins']:.1f}g</span> "
                    f"<span style='background-color: #fff; padding: 2px 6px; border-radius: 3px; margin: 0 2px;'>"
                    f"G {food_macros['carbs']:.1f}g</span> "
                    f"<span style='background-color: #fff; padding: 2px 6px; border-radius: 3px; margin: 0 2px;'>"
                    f"L {food_macros['fats']:.1f}g</span>"
                )
                macros_label.setStyleSheet("font-size: 11px; color: #666;")
                food_layout.addWidget(macros_label)

                foods_layout.addWidget(food_widget)

            layout.addWidget(foods_container)
        else:
            no_foods_label = QLabel("Aucun aliment")
            no_foods_label.setStyleSheet("font-size: 12px; color: #999; font-style: italic; padding-left: 20px;")
            layout.addWidget(no_foods_label)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {style['border']}; max-height: 1px; margin: 5px 0;")
        layout.addWidget(separator)

        # Totaux du repas avec style amélioré
        meal_macros = meal.calculate_macros()
        totals_widget = QWidget()
        totals_layout = QHBoxLayout(totals_widget)
        totals_layout.setContentsMargins(0, 0, 0, 0)

        totals_label = QLabel("TOTAL:")
        totals_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #555;")
        totals_layout.addWidget(totals_label)

        totals_layout.addStretch()

        values_label = QLabel(
            f"<b>{meal_macros['calories']:.0f} kcal</b>  |  "
            f"P: {meal_macros['proteins']:.1f}g  |  "
            f"G: {meal_macros['carbs']:.1f}g  |  "
            f"L: {meal_macros['fats']:.1f}g"
        )
        values_label.setStyleSheet(f"font-size: 12px; color: {style['border']}; font-weight: bold;")
        totals_layout.addWidget(values_label)

        layout.addWidget(totals_widget)

        return frame

    def _get_validation_text(self, totals: dict, target) -> str:
        """
        Génère un texte de validation pour les totaux du jour.

        Args:
            totals: Totaux calculés
            target: Objectif nutritionnel

        Returns:
            Texte de validation ou chaîne vide
        """
        messages = []

        macros = [
            ("Calories", totals["calories"], target.calories),
            ("Protéines", totals["proteins"], target.proteins),
            ("Glucides", totals["carbs"], target.carbs),
            ("Lipides", totals["fats"], target.fats)
        ]

        for name, actual, expected in macros:
            if expected > 0:
                deviation = abs(actual - expected) / expected
                if deviation > 0.05:  # Tolérance de 5%
                    diff = actual - expected
                    sign = "+" if diff > 0 else ""
                    messages.append(
                        f"{name}: {sign}{diff:.1f} ({deviation * 100:.1f}%)"
                    )

        if messages:
            return "Écarts: " + ", ".join(messages)

        return "✓ Objectifs atteints"

    def clear(self):
        """Efface l'affichage et affiche le message initial."""
        self.current_plan = None
        self._clear_content()

        self.empty_label.show()
        self.content_layout.addWidget(self.empty_label)
        self.content_layout.addStretch()

        self.title_label.setText("Plan Alimentaire")
