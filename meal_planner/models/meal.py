"""
Modèle Meal - Représente un repas composé de plusieurs aliments
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict

from meal_planner.models.food import Food
from meal_planner.utils.validators import validate_string_not_empty, validate_food_quantity


@dataclass
class Meal:
    """
    Représente un repas composé de plusieurs aliments avec leurs quantités.

    Attributes:
        name: Nom du repas
        meal_type: Type de repas (breakfast, lunch, dinner, snack)
        foods: Liste de tuples (Food, quantité_en_grammes)
        target_calories: Objectif calorique pour ce repas
        day_number: Numéro du jour dans le plan (1-based)
        id: Identifiant unique en base de données
    """

    name: str
    meal_type: str
    target_calories: float
    day_number: int = 1
    foods: List[Tuple[Food, float]] = field(default_factory=list)
    id: Optional[int] = None

    def validate(self) -> Tuple[bool, str]:
        """
        Valide les données du repas.

        Returns:
            Tuple (bool, str): (est_valide, message_erreur)
        """
        # Valider le nom
        is_valid, msg = validate_string_not_empty(self.name, "Nom du repas")
        if not is_valid:
            return is_valid, msg

        # Valider le type de repas
        is_valid, msg = validate_string_not_empty(self.meal_type, "Type de repas")
        if not is_valid:
            return is_valid, msg

        # Valider le jour
        if self.day_number < 1:
            return False, "Le numéro du jour doit être >= 1"

        # Valider les quantités d'aliments
        for food, quantity in self.foods:
            is_valid, msg = validate_food_quantity(quantity)
            if not is_valid:
                return False, f"{food.name}: {msg}"

        return True, ""

    def add_food(self, food: Food, quantity: float) -> None:
        """
        Ajoute un aliment au repas.

        Args:
            food: L'aliment à ajouter
            quantity: Quantité en grammes

        Raises:
            ValueError: Si la quantité est invalide
        """
        is_valid, msg = validate_food_quantity(quantity)
        if not is_valid:
            raise ValueError(msg)

        self.foods.append((food, quantity))

    def remove_food(self, food: Food) -> bool:
        """
        Retire un aliment du repas.

        Args:
            food: L'aliment à retirer

        Returns:
            True si l'aliment a été retiré, False sinon
        """
        original_length = len(self.foods)
        self.foods = [(f, q) for f, q in self.foods if f.id != food.id]
        return len(self.foods) < original_length

    def calculate_macros(self) -> Dict[str, float]:
        """
        Calcule les macronutriments totaux du repas.

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

        for food, quantity in self.foods:
            food_macros = food.calculate_for_quantity(quantity)
            totals["calories"] += food_macros["calories"]
            totals["proteins"] += food_macros["proteins"]
            totals["carbs"] += food_macros["carbs"]
            totals["fats"] += food_macros["fats"]
            totals["fibers"] += food_macros["fibers"]

        return totals

    def get_total_weight(self) -> float:
        """
        Calcule le poids total du repas en grammes.

        Returns:
            Poids total en grammes
        """
        return sum(quantity for _, quantity in self.foods)

    def get_food_count(self) -> int:
        """
        Retourne le nombre d'aliments dans le repas.

        Returns:
            Nombre d'aliments
        """
        return len(self.foods)

    def to_dict(self) -> Dict:
        """
        Convertit le repas en dictionnaire.

        Returns:
            Dict représentant le repas
        """
        return {
            "id": self.id,
            "name": self.name,
            "meal_type": self.meal_type,
            "target_calories": self.target_calories,
            "day_number": self.day_number,
            "foods": [
                {
                    "food_id": food.id,
                    "food_name": food.name,
                    "quantity": quantity
                }
                for food, quantity in self.foods
            ],
            "macros": self.calculate_macros()
        }

    def get_summary(self) -> str:
        """
        Retourne un résumé textuel du repas.

        Returns:
            Chaîne décrivant le repas
        """
        macros = self.calculate_macros()
        foods_list = ", ".join([f"{food.name} ({quantity}g)" for food, quantity in self.foods])

        return (
            f"{self.name} - Jour {self.day_number}\n"
            f"Type: {self.meal_type}\n"
            f"Aliments: {foods_list}\n"
            f"Total: {macros['calories']:.0f} kcal - "
            f"P: {macros['proteins']:.1f}g, C: {macros['carbs']:.1f}g, F: {macros['fats']:.1f}g"
        )

    def __str__(self) -> str:
        """Représentation textuelle du repas."""
        macros = self.calculate_macros()
        return (
            f"{self.name} ({self.meal_type}) - "
            f"{macros['calories']:.0f} kcal, {len(self.foods)} aliments"
        )

    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (
            f"Meal(id={self.id}, name='{self.name}', type='{self.meal_type}', "
            f"day={self.day_number}, foods_count={len(self.foods)})"
        )
