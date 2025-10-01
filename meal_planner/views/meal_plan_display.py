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

        # Effacer le contenu précédent
        self._clear_content()

        # Masquer le message vide
        self.empty_label.hide()

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
            if item.widget():
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
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border-radius: 3px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(5)

        # Nom et type du repas
        header_layout = QHBoxLayout()
        meal_name_label = QLabel(f"<b>{meal.name}</b> ({meal.meal_type})")
        header_layout.addWidget(meal_name_label)
        header_layout.addStretch()

        # Bouton régénérer (pour Phase 2)
        # regenerate_btn = QPushButton("Régénérer")
        # regenerate_btn.setMaximumWidth(100)
        # regenerate_btn.clicked.connect(
        #     lambda: self.meal_regenerate_requested.emit(meal.day_number, 0)
        # )
        # header_layout.addWidget(regenerate_btn)

        layout.addLayout(header_layout)

        # Liste des aliments
        if meal.foods:
            for food, quantity in meal.foods:
                food_macros = food.calculate_for_quantity(quantity)
                food_text = (
                    f"• {food.name}: {quantity:.0f}g "
                    f"({food_macros['calories']:.0f} kcal, "
                    f"P: {food_macros['proteins']:.1f}g, "
                    f"G: {food_macros['carbs']:.1f}g, "
                    f"L: {food_macros['fats']:.1f}g)"
                )
                food_label = QLabel(food_text)
                food_label.setStyleSheet("font-size: 12px; color: #333;")
                layout.addWidget(food_label)
        else:
            no_foods_label = QLabel("Aucun aliment")
            no_foods_label.setStyleSheet("font-size: 12px; color: #999; font-style: italic;")
            layout.addWidget(no_foods_label)

        # Totaux du repas
        meal_macros = meal.calculate_macros()
        totals_text = (
            f"Total: {meal_macros['calories']:.0f} kcal | "
            f"P: {meal_macros['proteins']:.1f}g | "
            f"G: {meal_macros['carbs']:.1f}g | "
            f"L: {meal_macros['fats']:.1f}g"
        )
        totals_label = QLabel(totals_text)
        totals_label.setStyleSheet("font-size: 11px; color: #666; font-weight: bold;")
        layout.addWidget(totals_label)

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
