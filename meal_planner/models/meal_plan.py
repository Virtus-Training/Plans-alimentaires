"""
Modèle MealPlan - Représente un plan alimentaire complet
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from collections import defaultdict

from meal_planner.models.meal import Meal
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.config import MACRO_TOLERANCE


@dataclass
class MealPlan:
    """
    Représente un plan alimentaire complet sur plusieurs jours.

    Attributes:
        duration_days: Nombre de jours du plan
        nutrition_target: Objectif nutritionnel quotidien
        meals: Liste des repas du plan
        notes: Notes ou commentaires sur le plan
        id: Identifiant unique en base de données
    """

    duration_days: int
    nutrition_target: NutritionTarget
    meals: List[Meal] = field(default_factory=list)
    notes: str = ""
    id: Optional[int] = None

    def validate(self) -> Dict:
        """
        Valide le plan alimentaire complet.

        Returns:
            Dict contenant les résultats de validation pour chaque jour
        """
        results = {}

        for day in range(1, self.duration_days + 1):
            day_result = self.validate_day(day)
            results[f"day_{day}"] = day_result

        return results

    def validate_day(self, day: int) -> Dict:
        """
        Valide un jour spécifique du plan.

        Args:
            day: Numéro du jour à valider

        Returns:
            Dict contenant les résultats de validation
        """
        daily_totals = self.calculate_daily_totals(day)
        target = self.nutrition_target

        result = {
            "is_valid": True,
            "totals": daily_totals,
            "target": target.to_dict(),
            "deviations": {},
            "messages": []
        }

        # Calculer les écarts
        macros = ["calories", "proteins", "carbs", "fats"]
        for macro in macros:
            actual = daily_totals.get(macro, 0)
            expected = getattr(target, macro)

            if expected > 0:
                deviation = abs(actual - expected) / expected
                result["deviations"][macro] = deviation

                if deviation > MACRO_TOLERANCE:
                    result["is_valid"] = False
                    result["messages"].append(
                        f"{macro.capitalize()}: {actual:.1f} (cible: {expected:.1f}, "
                        f"écart: {deviation * 100:.1f}%)"
                    )

        return result

    def validate_against_target(self, tolerance: float = MACRO_TOLERANCE) -> Dict:
        """
        Valide l'ensemble du plan par rapport aux objectifs.

        Args:
            tolerance: Tolérance acceptable (par défaut: MACRO_TOLERANCE)

        Returns:
            Dict contenant les résultats de validation globaux
        """
        all_valid = True
        days_results = {}

        for day in range(1, self.duration_days + 1):
            day_result = self.validate_day(day)
            days_results[f"day_{day}"] = day_result

            if not day_result["is_valid"]:
                all_valid = False

        return {
            "is_valid": all_valid,
            "days": days_results,
            "total_meals": len(self.meals),
            "duration_days": self.duration_days
        }

    def calculate_daily_totals(self, day: int) -> Dict[str, float]:
        """
        Calcule les totaux nutritionnels pour un jour donné.

        Args:
            day: Numéro du jour

        Returns:
            Dict contenant les totaux: calories, proteins, carbs, fats, fibers
        """
        totals = {
            "calories": 0.0,
            "proteins": 0.0,
            "carbs": 0.0,
            "fats": 0.0,
            "fibers": 0.0
        }

        day_meals = self.get_meals_for_day(day)

        for meal in day_meals:
            meal_macros = meal.calculate_macros()
            for key in totals.keys():
                totals[key] += meal_macros.get(key, 0.0)

        return totals

    def get_meals_for_day(self, day: int) -> List[Meal]:
        """
        Retourne tous les repas pour un jour donné.

        Args:
            day: Numéro du jour

        Returns:
            Liste des repas du jour
        """
        return [meal for meal in self.meals if meal.day_number == day]

    def add_meal(self, meal: Meal) -> None:
        """
        Ajoute un repas au plan.

        Args:
            meal: Le repas à ajouter
        """
        if meal.day_number > self.duration_days:
            raise ValueError(
                f"Le jour du repas ({meal.day_number}) dépasse la durée du plan ({self.duration_days})"
            )

        self.meals.append(meal)

    def remove_meal(self, meal: Meal) -> bool:
        """
        Retire un repas du plan.

        Args:
            meal: Le repas à retirer

        Returns:
            True si le repas a été retiré, False sinon
        """
        original_length = len(self.meals)
        self.meals = [m for m in self.meals if m.id != meal.id]
        return len(self.meals) < original_length

    def get_meals_by_type(self) -> Dict[str, List[Meal]]:
        """
        Regroupe les repas par type.

        Returns:
            Dict avec les types de repas comme clés et listes de repas comme valeurs
        """
        meals_by_type = defaultdict(list)

        for meal in self.meals:
            meals_by_type[meal.meal_type].append(meal)

        return dict(meals_by_type)

    def get_summary(self) -> str:
        """
        Retourne un résumé textuel du plan.

        Returns:
            Chaîne décrivant le plan
        """
        summary_lines = [
            f"Plan alimentaire - {self.duration_days} jour(s)",
            f"Objectif: {self.nutrition_target}",
            f"Nombre de repas: {len(self.meals)}",
            ""
        ]

        for day in range(1, self.duration_days + 1):
            day_meals = self.get_meals_for_day(day)
            day_totals = self.calculate_daily_totals(day)

            summary_lines.append(f"Jour {day}:")
            summary_lines.append(f"  {len(day_meals)} repas")
            summary_lines.append(
                f"  Total: {day_totals['calories']:.0f} kcal - "
                f"P: {day_totals['proteins']:.1f}g, "
                f"C: {day_totals['carbs']:.1f}g, "
                f"F: {day_totals['fats']:.1f}g"
            )

            for meal in day_meals:
                summary_lines.append(f"    - {meal}")

            summary_lines.append("")

        return "\n".join(summary_lines)

    def to_dict(self) -> Dict:
        """
        Convertit le plan en dictionnaire.

        Returns:
            Dict représentant le plan
        """
        return {
            "id": self.id,
            "duration_days": self.duration_days,
            "nutrition_target": self.nutrition_target.to_dict(),
            "meals": [meal.to_dict() for meal in self.meals],
            "notes": self.notes,
            "validation": self.validate_against_target()
        }

    def __str__(self) -> str:
        """Représentation textuelle du plan."""
        return (
            f"Plan alimentaire {self.duration_days} jour(s) - "
            f"{len(self.meals)} repas - "
            f"Objectif: {self.nutrition_target.calories:.0f} kcal/jour"
        )

    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (
            f"MealPlan(id={self.id}, duration={self.duration_days}, "
            f"meals_count={len(self.meals)})"
        )
