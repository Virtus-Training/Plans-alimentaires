"""
PresetMeal - Modèle pour les repas pré-composés
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import json

from meal_planner.models.food import Food


@dataclass
class PresetMeal:
    """
    Représente un repas pré-composé avec ses aliments et quantités.

    Attributes:
        id: Identifiant unique (None si pas encore en base)
        name: Nom du repas prédéfini
        meal_type: Type de repas (breakfast, lunch, dinner, snack)
        foods: Liste de tuples (Food, quantité_en_grammes)
        description: Description optionnelle du repas
    """
    name: str
    meal_type: str
    foods: List[Tuple[Food, float]] = field(default_factory=list)
    id: Optional[int] = None
    description: str = ""

    def calculate_macros(self) -> Dict[str, float]:
        """
        Calcule les macronutriments totaux du repas.

        Returns:
            Dict avec calories, protéines, glucides, lipides
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
            for key in totals:
                totals[key] += food_macros[key]

        return totals

    def validate(self) -> Tuple[bool, str]:
        """
        Valide le repas prédéfini.

        Returns:
            Tuple (est_valide, message_erreur)
        """
        if not self.name or not self.name.strip():
            return False, "Le nom du repas est requis"

        if self.meal_type not in ["breakfast", "lunch", "dinner", "snack",
                                   "afternoon_snack", "morning_snack", "evening_snack"]:
            return False, f"Type de repas invalide: {self.meal_type}"

        if not self.foods:
            return False, "Le repas doit contenir au moins un aliment"

        # Vérifier que chaque aliment a une quantité valide
        for food, quantity in self.foods:
            if quantity <= 0:
                return False, f"Quantité invalide pour {food.name}: {quantity}g"

            # Valider l'aliment
            is_valid, msg = food.validate()
            if not is_valid:
                return False, f"Aliment invalide ({food.name}): {msg}"

        # Vérifier que le repas a des calories
        macros = self.calculate_macros()
        if macros["calories"] < 50:
            return False, "Le repas doit contenir au moins 50 kcal"

        return True, ""

    def to_dict(self) -> Dict:
        """
        Convertit le repas en dictionnaire.

        Returns:
            Représentation dict du repas
        """
        return {
            "id": self.id,
            "name": self.name,
            "meal_type": self.meal_type,
            "description": self.description,
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

    @classmethod
    def from_dict(cls, data: Dict, foods_by_id: Dict[int, Food]) -> 'PresetMeal':
        """
        Crée un PresetMeal depuis un dictionnaire.

        Args:
            data: Dictionnaire avec les données
            foods_by_id: Mapping id -> Food pour récupérer les objets Food

        Returns:
            Instance de PresetMeal
        """
        foods = []
        for food_data in data.get("foods", []):
            food_id = food_data["food_id"]
            quantity = food_data["quantity"]

            if food_id in foods_by_id:
                foods.append((foods_by_id[food_id], quantity))

        return cls(
            id=data.get("id"),
            name=data["name"],
            meal_type=data["meal_type"],
            description=data.get("description", ""),
            foods=foods
        )

    def to_json_string(self) -> str:
        """
        Sérialise les aliments en JSON pour stockage en base.

        Returns:
            Chaîne JSON
        """
        foods_data = [
            {"food_id": food.id, "quantity": quantity}
            for food, quantity in self.foods
        ]
        return json.dumps(foods_data)

    @classmethod
    def from_db_row(cls, row_data: Dict, foods_by_id: Dict[int, Food]) -> 'PresetMeal':
        """
        Crée un PresetMeal depuis une ligne de base de données.

        Args:
            row_data: Dict avec id, name, meal_type, foods_json, description
            foods_by_id: Mapping id -> Food

        Returns:
            Instance de PresetMeal
        """
        foods_json = json.loads(row_data["foods_json"])
        foods = []

        for food_data in foods_json:
            food_id = food_data["food_id"]
            quantity = food_data["quantity"]

            if food_id in foods_by_id:
                foods.append((foods_by_id[food_id], quantity))

        return cls(
            id=row_data["id"],
            name=row_data["name"],
            meal_type=row_data["meal_type"],
            description=row_data.get("description", ""),
            foods=foods
        )

    def __str__(self) -> str:
        """Représentation textuelle."""
        macros = self.calculate_macros()
        return (
            f"{self.name} ({self.meal_type}): "
            f"{len(self.foods)} aliments, "
            f"{macros['calories']:.0f} kcal"
        )
