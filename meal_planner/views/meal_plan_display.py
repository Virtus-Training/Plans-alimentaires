"""
MealPlanDisplay - Affichage du plan alimentaire généré
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QGroupBox, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QBrush, QFont
from typing import Optional
import math

from meal_planner.models.meal_plan import MealPlan
from meal_planner.utils.ui_helpers import create_icon_label, create_shadow_effect


class CircularProgressBar(QWidget):
    """Widget de barre de progression circulaire pour les macros."""

    def __init__(self, value: float, max_value: float, color: str, label: str, parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.color = QColor(color)
        self.label = label
        self.setMinimumSize(120, 120)
        self.setMaximumSize(140, 140)

    def paintEvent(self, event):
        """Dessine la barre circulaire."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dimensions
        width = self.width()
        height = self.height()
        side = min(width, height)

        # Rectangle pour le cercle
        rect = QRectF(10, 10, side - 20, side - 20)

        # Fond du cercle (gris clair)
        painter.setPen(QPen(QColor("#ecf0f1"), 8, Qt.PenStyle.SolidLine))
        painter.drawArc(rect, 0, 360 * 16)

        # Calculer le pourcentage
        percentage = (self.value / self.max_value * 100) if self.max_value > 0 else 0
        angle = int(percentage * 360 / 100 * 16)

        # Couleur selon le pourcentage
        if 95 <= percentage <= 105:
            progress_color = QColor("#27ae60")
        elif 90 <= percentage <= 110:
            progress_color = self.color
        else:
            progress_color = QColor("#e67e22")

        # Arc de progression
        painter.setPen(QPen(progress_color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, 90 * 16, -angle)

        # Texte au centre (pourcentage)
        painter.setPen(QColor("#2c3e50"))
        font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{percentage:.0f}%")

        # Label en dessous
        label_rect = QRectF(0, side - 25, side, 20)
        font_small = QFont("Segoe UI", 9)
        painter.setFont(font_small)
        painter.setPen(QColor("#7f8c8d"))
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self.label)


class MealPlanDisplay(QWidget):
    """
    Widget d'affichage du plan alimentaire.

    Signals:
        meal_regenerate_requested: Émis quand l'utilisateur veut régénérer un repas
        save_requested: Émis quand l'utilisateur veut sauvegarder le plan
    """

    meal_regenerate_requested = pyqtSignal(int, int)  # day, meal_index
    save_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plan: Optional[MealPlan] = None
        self.save_button = None
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Titre avec icône
        title_layout = QHBoxLayout()
        title_icon = create_icon_label("plate", 28)
        title_layout.addWidget(title_icon)

        self.title_label = QLabel("Plan Alimentaire")
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            padding-left: 10px;
            letter-spacing: -0.5px;
        """)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # Zone de scroll pour le contenu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Widget de contenu
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)

        # Message initial stylisé
        empty_container = QWidget()
        empty_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 20px;
            padding: 50px;
        """)
        empty_layout = QVBoxLayout(empty_container)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(20)

        # Icône
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        plate_icon = create_icon_label("plate", 80)
        icon_layout.addWidget(plate_icon)
        empty_layout.addWidget(icon_container)

        # Titre
        title_label = QLabel("🍽️ Aucun Plan Généré")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        """)
        empty_layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Configurez vos objectifs nutritionnels\n"
            "et cliquez sur le bouton de génération\n"
            "pour créer votre plan personnalisé !"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.95);
            font-size: 16px;
            line-height: 1.7;
            font-weight: 400;
        """)
        empty_layout.addWidget(desc_label)

        # Badge indicatif
        badge = QLabel("👈 Commencez ici")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 13px;
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 10px;
        """)
        empty_layout.addWidget(badge)

        self.empty_label = empty_container
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

        # Ajouter une carte de statistiques globales
        stats_widget = self._create_global_stats_widget()
        self.content_layout.addWidget(stats_widget)

        # Ajouter les boutons d'action rapide
        actions_widget = self._create_actions_widget()
        self.content_layout.addWidget(actions_widget)

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

    def _create_global_stats_widget(self) -> QWidget:
        """
        Crée un widget avec les statistiques globales du plan.

        Returns:
            Widget des statistiques
        """
        if not self.current_plan:
            return QWidget()

        stats_container = QWidget()
        stats_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 16px;
            padding: 24px;
        """)
        stats_container.setGraphicsEffect(create_shadow_effect(15, 0.25))
        main_layout = QVBoxLayout(stats_container)
        main_layout.setSpacing(18)

        # Titre
        title_layout = QHBoxLayout()
        title_icon = create_icon_label("chart", 24)
        title_layout.addWidget(title_icon)

        title = QLabel("<b>📊 Vue d'ensemble du Plan</b>")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: 600; padding-left: 8px;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Grille de statistiques
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(18)

        # Calculer les moyennes
        total_days = self.current_plan.duration_days
        avg_calories = sum(self.current_plan.calculate_daily_totals(d)['calories']
                          for d in range(1, total_days + 1)) / total_days
        avg_proteins = sum(self.current_plan.calculate_daily_totals(d)['proteins']
                          for d in range(1, total_days + 1)) / total_days
        avg_carbs = sum(self.current_plan.calculate_daily_totals(d)['carbs']
                       for d in range(1, total_days + 1)) / total_days
        avg_fats = sum(self.current_plan.calculate_daily_totals(d)['fats']
                      for d in range(1, total_days + 1)) / total_days

        # Compter les repas
        total_meals = sum(len(self.current_plan.get_meals_for_day(d))
                         for d in range(1, total_days + 1))

        stats_data = [
            ("🗓️", "Jours", str(total_days), ""),
            ("🍽️", "Repas", str(total_meals), ""),
            ("🔥", "Kcal/jour", f"{avg_calories:.0f}", "kcal"),
            ("💪", "Protéines", f"{avg_proteins:.1f}", "g/jour"),
            ("🍞", "Glucides", f"{avg_carbs:.1f}", "g/jour"),
            ("🥑", "Lipides", f"{avg_fats:.1f}", "g/jour")
        ]

        for emoji, label, value, unit in stats_data:
            stat_card = self._create_stat_card(emoji, label, value, unit)
            grid_layout.addWidget(stat_card)

        main_layout.addLayout(grid_layout)

        return stats_container

    def _create_stat_card(self, emoji: str, label: str, value: str, unit: str) -> QWidget:
        """
        Crée une carte de statistique.

        Args:
            emoji: Emoji représentatif
            label: Label de la stat
            value: Valeur
            unit: Unité

        Returns:
            Widget de la carte
        """
        card = QWidget()
        card.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 16px;
        """)
        card.setGraphicsEffect(create_shadow_effect(8, 0.15))
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        # Emoji
        emoji_label = QLabel(emoji)
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(emoji_label)

        # Valeur
        value_text = f"{value} {unit}" if unit else value
        value_label = QLabel(f"<b>{value_text}</b>")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: white; font-size: 18px; font-weight: 700;")
        layout.addWidget(value_label)

        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 12px; font-weight: 500;")
        layout.addWidget(label_widget)

        return card

    def _create_actions_widget(self) -> QWidget:
        """
        Crée un widget avec les boutons d'action rapide.

        Returns:
            Widget des actions
        """
        actions_container = QWidget()
        actions_container.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 12px;
            padding: 18px;
        """)
        actions_container.setGraphicsEffect(create_shadow_effect(5, 0.1))
        layout = QHBoxLayout(actions_container)
        layout.setSpacing(10)

        # Bouton Sauvegarder (activé)
        self.save_button = QPushButton("💾 Sauvegarder")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
            QPushButton:disabled {
                background-color: #ecf0f1;
                color: #bdc3c7;
                border-color: #bdc3c7;
            }
        """)
        self.save_button.setGraphicsEffect(create_shadow_effect(6, 0.15))
        self.save_button.setEnabled(True)
        self.save_button.setToolTip("Sauvegarder le plan au format JSON")
        self.save_button.clicked.connect(self._on_save_clicked)
        layout.addWidget(self.save_button)

        # Autres boutons (désactivés pour l'instant)
        buttons_data = [
            ("📊", "Exporter PDF", "#9b59b6"),
            ("📧", "Envoyer", "#1abc9c"),
            ("🔄", "Régénérer", "#e67e22"),
        ]

        for emoji, text, color in buttons_data:
            btn = QPushButton(f"{emoji} {text}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {color};
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: #2c3e50;
                }}
                QPushButton:disabled {{
                    background-color: #ecf0f1;
                    color: #bdc3c7;
                    border-color: #bdc3c7;
                }}
            """)
            btn.setGraphicsEffect(create_shadow_effect(6, 0.15))
            btn.setEnabled(False)
            btn.setToolTip(f"{text} (Disponible en Phase 2)")
            layout.addWidget(btn)

        layout.addStretch()

        # Badge "Bientôt disponible"
        badge = QLabel("⏳ Autres fonctionnalités à venir")
        badge.setStyleSheet("""
            color: #7f8c8d;
            font-size: 11px;
            font-style: italic;
            padding: 5px 10px;
            background-color: white;
            border-radius: 10px;
        """)
        layout.addWidget(badge)

        return actions_container

    def _on_save_clicked(self):
        """Gère le clic sur le bouton Sauvegarder."""
        self.save_requested.emit()

    def _create_conformity_badge(self, day_totals: dict) -> QLabel:
        """
        Crée un badge indiquant la conformité aux objectifs.

        Args:
            day_totals: Totaux du jour

        Returns:
            Badge de conformité
        """
        if not self.current_plan:
            return QLabel()

        target = self.current_plan.nutrition_target

        # Calculer l'écart moyen
        deviations = []
        for key in ['calories', 'proteins', 'carbs', 'fats']:
            expected = getattr(target, key)
            if expected > 0:
                actual = day_totals[key]
                deviation = abs(actual - expected) / expected
                deviations.append(deviation)

        avg_deviation = sum(deviations) / len(deviations) if deviations else 0

        # Déterminer le badge
        if avg_deviation <= 0.05:  # ≤ 5%
            emoji = "🎯"
            text = "Parfait"
            color = "#27ae60"
        elif avg_deviation <= 0.10:  # ≤ 10%
            emoji = "✅"
            text = "Excellent"
            color = "#2ecc71"
        elif avg_deviation <= 0.15:  # ≤ 15%
            emoji = "👍"
            text = "Bon"
            color = "#f39c12"
        else:
            emoji = "⚠️"
            text = "À ajuster"
            color = "#e67e22"

        badge = QLabel(f"{emoji} {text}")
        badge.setStyleSheet(f"""
            font-size: 12px;
            color: white;
            background-color: {color};
            padding: 6px 14px;
            border-radius: 14px;
            font-weight: 600;
        """)
        badge.setToolTip(f"Écart moyen: {avg_deviation * 100:.1f}%")

        return badge

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

        # Groupe pour le jour avec style amélioré
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #e3e8ed;
                border-radius: 16px;
                margin-top: 8px;
                padding: 20px;
            }
        """)
        group.setGraphicsEffect(create_shadow_effect(12, 0.15))

        layout = QVBoxLayout()
        layout.setSpacing(16)

        # En-tête du jour avec style moderne
        day_header = QWidget()
        day_header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 8px;
            padding: 12px;
        """)
        day_header_layout = QHBoxLayout(day_header)

        # Icône calendrier
        calendar_icon = create_icon_label("calendar", 24)
        day_header_layout.addWidget(calendar_icon)

        # Titre jour
        day_title = QLabel(f"<b>JOUR {day}</b>")
        day_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: white;
            padding-left: 10px;
            letter-spacing: 1px;
        """)
        day_header_layout.addWidget(day_title)
        day_header_layout.addStretch()

        # Nombre de repas
        meals_count = QLabel(f"{len(day_meals)} repas")
        meals_count.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.95);
            background-color: rgba(255, 255, 255, 0.25);
            padding: 6px 14px;
            border-radius: 14px;
        """)
        day_header_layout.addWidget(meals_count)

        # Indicateur de conformité
        conformity_badge = self._create_conformity_badge(day_totals)
        day_header_layout.addWidget(conformity_badge)

        layout.addWidget(day_header)

        # Container pour les repas avec grille
        meals_container = QWidget()
        meals_layout = QVBoxLayout(meals_container)
        meals_layout.setSpacing(12)
        meals_layout.setContentsMargins(8, 12, 8, 12)

        # Afficher chaque repas
        for meal in day_meals:
            meal_widget = self._create_meal_widget(meal)
            meals_layout.addWidget(meal_widget)

        layout.addWidget(meals_container)

        # Totaux du jour avec style moderne et barres de progression
        totals_widget = self._create_totals_widget(day_totals)
        layout.addWidget(totals_widget)

        # Validation
        target = self.current_plan.nutrition_target
        validation_text = self._get_validation_text(day_totals, target)
        if validation_text:
            validation_label = QLabel(validation_text)
            validation_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
            layout.addWidget(validation_label)

        group.setLayout(layout)
        return group

    def _create_totals_widget(self, day_totals: dict) -> QWidget:
        """
        Crée un widget stylisé pour les totaux avec barres de progression.

        Args:
            day_totals: Totaux des macros du jour

        Returns:
            Widget des totaux
        """
        totals_container = QWidget()
        totals_container.setStyleSheet("""
            background: white;
            border: 1px solid #e8ecef;
            border-radius: 12px;
            padding: 18px;
        """)
        totals_container.setGraphicsEffect(create_shadow_effect(8, 0.12))
        container_layout = QVBoxLayout(totals_container)
        container_layout.setSpacing(16)

        # En-tête avec icône
        header_layout = QHBoxLayout()
        chart_icon = create_icon_label("chart", 22)
        header_layout.addWidget(chart_icon)

        header_label = QLabel("<b>📊 Résumé Nutritionnel</b>")
        header_label.setStyleSheet("font-size: 15px; color: #2c3e50; padding-left: 8px; font-weight: 600;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        container_layout.addLayout(header_layout)

        # Grille des macros avec barres de progression
        target = self.current_plan.nutrition_target if self.current_plan else None

        # Barres circulaires pour une vue d'ensemble
        circular_container = QWidget()
        circular_layout = QHBoxLayout(circular_container)
        circular_layout.setSpacing(20)

        macros_circular = [
            ("Calories", day_totals['calories'], target.calories if target else 0, "#e74c3c"),
            ("Protéines", day_totals['proteins'], target.proteins if target else 0, "#3498db"),
            ("Glucides", day_totals['carbs'], target.carbs if target else 0, "#f39c12"),
            ("Lipides", day_totals['fats'], target.fats if target else 0, "#9b59b6")
        ]

        for name, actual, expected, color in macros_circular:
            circular_progress = CircularProgressBar(actual, expected, color, name)
            circular_layout.addWidget(circular_progress)

        circular_layout.addStretch()
        container_layout.addWidget(circular_container)

        # Barres horizontales détaillées
        macros_data = [
            ("Calories", day_totals['calories'], target.calories if target else 0, "#e74c3c", "fire"),
            ("Protéines", day_totals['proteins'], target.proteins if target else 0, "#3498db", "protein"),
            ("Glucides", day_totals['carbs'], target.carbs if target else 0, "#f39c12", "carbs"),
            ("Lipides", day_totals['fats'], target.fats if target else 0, "#9b59b6", "fat")
        ]

        for name, actual, expected, color, icon in macros_data:
            macro_widget = self._create_macro_progress_bar(name, actual, expected, color, icon)
            container_layout.addWidget(macro_widget)

        return totals_container

    def _create_macro_progress_bar(self, name: str, actual: float, expected: float, color: str, icon_name: str) -> QWidget:
        """
        Crée une barre de progression pour une macro.

        Args:
            name: Nom de la macro
            actual: Valeur actuelle
            expected: Valeur cible
            color: Couleur de la barre
            icon_name: Nom de l'icône

        Returns:
            Widget de la barre de progression
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Ligne supérieure: icône, nom, valeurs
        top_layout = QHBoxLayout()

        # Icône
        icon_label = create_icon_label(icon_name, 16)
        top_layout.addWidget(icon_label)

        # Nom
        name_label = QLabel(f"<b>{name}</b>")
        name_label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 600; padding-left: 5px;")
        top_layout.addWidget(name_label)

        top_layout.addStretch()

        # Valeurs
        unit = "kcal" if name == "Calories" else "g"
        percentage = (actual / expected * 100) if expected > 0 else 0
        values_label = QLabel(f"<b>{actual:.0f}</b> / {expected:.0f} {unit} <span style='color: #95a5a6;'>({percentage:.0f}%)</span>")
        values_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        top_layout.addWidget(values_label)

        layout.addLayout(top_layout)

        # Barre de progression stylisée
        progress_container = QWidget()
        progress_container.setFixedHeight(8)
        progress_container.setStyleSheet(f"""
            background-color: #ecf0f1;
            border-radius: 4px;
        """)

        # Barre de remplissage
        fill_percentage = min(percentage, 100)
        progress_fill = QWidget(progress_container)
        progress_fill.setGeometry(0, 0, int(progress_container.width() * fill_percentage / 100), 8)

        # Couleur selon le pourcentage
        if 95 <= percentage <= 105:
            fill_color = "#27ae60"  # Vert si proche de l'objectif
        elif 90 <= percentage <= 110:
            fill_color = color  # Couleur de la macro
        else:
            fill_color = "#e67e22"  # Orange si éloigné

        progress_fill.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {fill_color}, stop:1 {color});
            border-radius: 4px;
        """)

        layout.addWidget(progress_container)

        return widget

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
                "color": "#fff8e1",
                "border": "#ffa726",
                "icon_name": "clock",
                "emoji": "☀️",
                "name": "Petit-déjeuner"
            },
            "lunch": {
                "color": "#e3f2fd",
                "border": "#42a5f5",
                "icon_name": "plate",
                "emoji": "🍽️",
                "name": "Déjeuner"
            },
            "dinner": {
                "color": "#f3e5f5",
                "border": "#ab47bc",
                "icon_name": "sleep",
                "emoji": "🌙",
                "name": "Dîner"
            },
            "snack": {
                "color": "#e8f5e9",
                "border": "#66bb6a",
                "icon_name": "apple",
                "emoji": "🍎",
                "name": "Collation"
            },
            "afternoon_snack": {
                "color": "#fff9c4",
                "border": "#ffca28",
                "icon_name": "glass",
                "emoji": "☕",
                "name": "Goûter"
            },
            "morning_snack": {
                "color": "#e8f5e9",
                "border": "#66bb6a",
                "icon_name": "apple",
                "emoji": "🥐",
                "name": "Collation matinale"
            },
            "evening_snack": {
                "color": "#e0f2f1",
                "border": "#26a69a",
                "icon_name": "glass",
                "emoji": "🥛",
                "name": "Collation soirée"
            }
        }

        style = meal_styles.get(meal.meal_type, {
            "color": "#F5F5F5",
            "border": "#9E9E9E",
            "icon_name": "plate",
            "emoji": "🍴",
            "name": meal.meal_type
        })

        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {style['border']};
                border-left: 5px solid {style['border']};
                border-radius: 14px;
                padding: 18px;
                margin: 6px 0;
            }}
            QFrame:hover {{
                background: {style['color']};
                border: 2px solid {style['border']};
                border-left: 5px solid {style['border']};
            }}
        """)
        frame.setGraphicsEffect(create_shadow_effect(10, 0.12))

        layout = QVBoxLayout(frame)
        layout.setSpacing(14)

        # En-tête du repas avec icône
        header_layout = QHBoxLayout()

        # Icône PNG
        icon_widget = create_icon_label(style['icon_name'], 24)
        header_layout.addWidget(icon_widget)

        # Emoji
        emoji_label = QLabel(style['emoji'])
        emoji_label.setStyleSheet("font-size: 22px; padding: 0 5px;")
        header_layout.addWidget(emoji_label)

        meal_name_label = QLabel(f"<b>{style['name']}</b>")
        meal_name_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {style['border']};
            padding-left: 5px;
        """)
        header_layout.addWidget(meal_name_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Liste des aliments avec style amélioré
        if meal.foods:
            foods_container = QWidget()
            foods_layout = QVBoxLayout(foods_container)
            foods_layout.setContentsMargins(20, 8, 8, 8)
            foods_layout.setSpacing(8)

            for food, quantity in meal.foods:
                food_macros = food.calculate_for_quantity(quantity)

                # Widget pour chaque aliment
                food_widget = QWidget()
                food_layout = QHBoxLayout(food_widget)
                food_layout.setContentsMargins(0, 0, 0, 0)

                # Emoji catégorie
                category_emoji = self._get_category_emoji(food.category if hasattr(food, 'category') else "autre")
                category_label = QLabel(category_emoji)
                category_label.setStyleSheet("font-size: 14px;")
                category_label.setToolTip(food.category if hasattr(food, 'category') else "Autre")
                food_layout.addWidget(category_label)

                # Nom et quantité
                name_label = QLabel(f"<b>{food.name}</b>")
                name_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #2c3e50; padding-left: 5px;")

                # Tooltip détaillé
                tooltip_text = f"<b>{food.name}</b><br>"
                tooltip_text += f"Quantité: {quantity:.0f}g<br>"
                tooltip_text += f"<br><b>Valeurs nutritionnelles:</b><br>"
                tooltip_text += f"Calories: {food_macros['calories']:.0f} kcal<br>"
                tooltip_text += f"Protéines: {food_macros['proteins']:.1f}g<br>"
                tooltip_text += f"Glucides: {food_macros['carbs']:.1f}g<br>"
                tooltip_text += f"Lipides: {food_macros['fats']:.1f}g"
                if hasattr(food, 'category'):
                    tooltip_text += f"<br><br>Catégorie: {food.category}"

                name_label.setToolTip(tooltip_text)
                food_layout.addWidget(name_label)

                # Quantité badge
                qty_label = QLabel(f"{quantity:.0f}g")
                qty_label.setStyleSheet(f"""
                    font-size: 11px;
                    color: #7f8c8d;
                    background-color: #ecf0f1;
                    padding: 2px 8px;
                    border-radius: 10px;
                    margin-left: 8px;
                """)
                food_layout.addWidget(qty_label)

                food_layout.addStretch()

                # Macros en badges plus compacts
                macros_label = QLabel(
                    f"<span style='background-color: #ffebee; color: #e74c3c; padding: 2px 6px; border-radius: 3px; margin: 0 2px; font-weight: bold;'>"
                    f"{food_macros['calories']:.0f}</span> "
                    f"<span style='background-color: #e3f2fd; color: #3498db; padding: 2px 6px; border-radius: 3px; margin: 0 2px; font-weight: bold;'>"
                    f"P {food_macros['proteins']:.1f}</span> "
                    f"<span style='background-color: #fff3e0; color: #f39c12; padding: 2px 6px; border-radius: 3px; margin: 0 2px; font-weight: bold;'>"
                    f"G {food_macros['carbs']:.1f}</span> "
                    f"<span style='background-color: #f3e5f5; color: #9b59b6; padding: 2px 6px; border-radius: 3px; margin: 0 2px; font-weight: bold;'>"
                    f"L {food_macros['fats']:.1f}</span>"
                )
                macros_label.setStyleSheet("font-size: 10px;")
                food_layout.addWidget(macros_label)

                foods_layout.addWidget(food_widget)

            layout.addWidget(foods_container)
        else:
            no_foods_label = QLabel("Aucun aliment")
            no_foods_label.setStyleSheet("font-size: 12px; color: #999; font-style: italic; padding-left: 20px;")
            layout.addWidget(no_foods_label)

        # Totaux du repas avec style amélioré et icône
        meal_macros = meal.calculate_macros()
        totals_widget = QWidget()
        totals_widget.setStyleSheet(f"""
            background-color: {style['color']};
            border-radius: 8px;
            padding: 10px;
            margin-top: 8px;
        """)
        totals_layout = QHBoxLayout(totals_widget)
        totals_layout.setContentsMargins(0, 0, 0, 0)

        # Icône nutritionnelle
        nutrition_icon = create_icon_label("nutrition", 18)
        totals_layout.addWidget(nutrition_icon)

        totals_label = QLabel("<b>Total:</b>")
        totals_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {style['border']}; padding-left: 8px;")
        totals_layout.addWidget(totals_label)

        totals_layout.addStretch()

        values_label = QLabel(
            f"<span style='background-color: white; padding: 3px 8px; border-radius: 4px; margin: 0 3px;'>"
            f"<b>{meal_macros['calories']:.0f}</b> kcal</span>  "
            f"<span style='background-color: white; padding: 3px 8px; border-radius: 4px; margin: 0 3px;'>"
            f"P <b>{meal_macros['proteins']:.1f}</b>g</span>  "
            f"<span style='background-color: white; padding: 3px 8px; border-radius: 4px; margin: 0 3px;'>"
            f"G <b>{meal_macros['carbs']:.1f}</b>g</span>  "
            f"<span style='background-color: white; padding: 3px 8px; border-radius: 4px; margin: 0 3px;'>"
            f"L <b>{meal_macros['fats']:.1f}</b>g</span>"
        )
        values_label.setStyleSheet(f"font-size: 11px; color: {style['border']};")
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

    def _get_category_emoji(self, category: str) -> str:
        """
        Retourne un emoji selon la catégorie d'aliment.

        Args:
            category: Catégorie de l'aliment

        Returns:
            Emoji correspondant
        """
        category_emojis = {
            "viande": "🥩",
            "poisson": "🐟",
            "légume": "🥬",
            "fruit": "🍎",
            "céréale": "🌾",
            "produit laitier": "🥛",
            "œuf": "🥚",
            "légumineuse": "🫘",
            "noix": "🥜",
            "huile": "🫒",
            "boisson": "🥤",
            "snack": "🍪",
            "autre": "🍴"
        }

        # Recherche insensible à la casse
        category_lower = category.lower()
        for key, emoji in category_emojis.items():
            if key in category_lower:
                return emoji

        return "🍴"

    def clear(self):
        """Efface l'affichage et affiche le message initial."""
        self.current_plan = None
        self._clear_content()

        self.empty_label.show()
        self.content_layout.addWidget(self.empty_label)
        self.content_layout.addStretch()

        self.title_label.setText("Plan Alimentaire")
