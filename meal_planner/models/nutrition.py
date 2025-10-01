"""
Modèle NutritionTarget - Représente les objectifs nutritionnels
"""

from dataclasses import dataclass
from typing import Dict, Tuple

from meal_planner.utils.validators import validate_positive_number, validate_macro_values
from meal_planner.config import MACRO_CALORIES


@dataclass
class NutritionTarget:
    """
    Représente les objectifs nutritionnels macronutritionnels.

    Attributes:
        calories: Objectif calorique total (kcal)
        proteins: Objectif en protéines (g)
        carbs: Objectif en glucides (g)
        fats: Objectif en lipides (g)
    """

    calories: float
    proteins: float
    carbs: float
    fats: float

    def validate(self) -> Tuple[bool, str]:
        """
        Valide les objectifs nutritionnels.

        Returns:
            Tuple (bool, str): (est_valide, message_erreur)
        """
        return validate_macro_values(
            self.calories,
            self.proteins,
            self.carbs,
            self.fats
        )

    def get_macro_percentages(self) -> Dict[str, float]:
        """
        Calcule la répartition des macronutriments en pourcentage des calories.

        Returns:
            Dict contenant les pourcentages de chaque macro
        """
        if self.calories == 0:
            return {"proteins": 0.0, "carbs": 0.0, "fats": 0.0}

        total_calories = (
            self.proteins * MACRO_CALORIES["proteins"] +
            self.carbs * MACRO_CALORIES["carbs"] +
            self.fats * MACRO_CALORIES["fats"]
        )

        if total_calories == 0:
            return {"proteins": 0.0, "carbs": 0.0, "fats": 0.0}

        return {
            "proteins": (self.proteins * MACRO_CALORIES["proteins"] / total_calories) * 100,
            "carbs": (self.carbs * MACRO_CALORIES["carbs"] / total_calories) * 100,
            "fats": (self.fats * MACRO_CALORIES["fats"] / total_calories) * 100
        }

    def get_macro_calories(self) -> Dict[str, float]:
        """
        Calcule les calories apportées par chaque macronutriment.

        Returns:
            Dict contenant les calories de chaque macro
        """
        return {
            "proteins": self.proteins * MACRO_CALORIES["proteins"],
            "carbs": self.carbs * MACRO_CALORIES["carbs"],
            "fats": self.fats * MACRO_CALORIES["fats"]
        }

    def to_dict(self) -> Dict[str, float]:
        """
        Convertit les objectifs en dictionnaire.

        Returns:
            Dict représentant les objectifs
        """
        return {
            "calories": self.calories,
            "proteins": self.proteins,
            "carbs": self.carbs,
            "fats": self.fats
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'NutritionTarget':
        """
        Crée un objet NutritionTarget à partir d'un dictionnaire.

        Args:
            data: Dictionnaire contenant les données

        Returns:
            Instance de NutritionTarget
        """
        return cls(
            calories=float(data["calories"]),
            proteins=float(data["proteins"]),
            carbs=float(data["carbs"]),
            fats=float(data["fats"])
        )

    def scale_for_meal(self, percentage: float) -> 'NutritionTarget':
        """
        Crée un nouvel objectif nutritionnel pour un repas (pourcentage du total).

        Args:
            percentage: Pourcentage du total (0.0 à 1.0)

        Returns:
            Nouvel objectif nutritionnel pour le repas
        """
        if percentage < 0 or percentage > 1:
            raise ValueError("Le pourcentage doit être entre 0 et 1")

        return NutritionTarget(
            calories=self.calories * percentage,
            proteins=self.proteins * percentage,
            carbs=self.carbs * percentage,
            fats=self.fats * percentage
        )

    def __str__(self) -> str:
        """Représentation textuelle des objectifs."""
        percentages = self.get_macro_percentages()
        return (
            f"{self.calories:.0f} kcal - "
            f"P: {self.proteins:.0f}g ({percentages['proteins']:.1f}%), "
            f"C: {self.carbs:.0f}g ({percentages['carbs']:.1f}%), "
            f"F: {self.fats:.0f}g ({percentages['fats']:.1f}%)"
        )

    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (
            f"NutritionTarget(calories={self.calories}, proteins={self.proteins}, "
            f"carbs={self.carbs}, fats={self.fats})"
        )
