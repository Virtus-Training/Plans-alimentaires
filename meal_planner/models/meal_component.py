"""
MealComponent - Modèle pour les composantes de repas (entrée/plat/dessert)
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import json

from meal_planner.models.food import Food


@dataclass
class MealComponent:
    """
    Représente une composante de repas (entrée, plat, dessert, accompagnement).

    Attributes:
        id: Identifiant unique (None si pas encore en base)
        name: Nom de la composante
        component_type: Type de composante (entrée, plat, dessert, accompagnement)
        foods: Liste de tuples (Food, quantité_en_grammes)
        description: Description optionnelle
    """
    name: str
    component_type: str
    foods: List[Tuple[Food, float]] = field(default_factory=list)
    id: Optional[int] = None
    description: str = ""

    def calculate_macros(self) -> Dict[str, float]:
        """
        Calcule les macronutriments totaux de la composante.

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
        Valide la composante de repas.

        Returns:
            Tuple (est_valide, message_erreur)
        """
        valid_types = ["entrée", "plat", "dessert", "accompagnement"]

        if not self.name or not self.name.strip():
            return False, "Le nom de la composante est requis"

        if self.component_type not in valid_types:
            return False, f"Type de composante invalide: {self.component_type}"

        if not self.foods:
            return False, "La composante doit contenir au moins un aliment"

        # Vérifier que chaque aliment a une quantité valide
        for food, quantity in self.foods:
            if quantity <= 0:
                return False, f"Quantité invalide pour {food.name}: {quantity}g"

            # Valider l'aliment
            is_valid, msg = food.validate()
            if not is_valid:
                return False, f"Aliment invalide ({food.name}): {msg}"

        # Vérifier que la composante a des calories
        macros = self.calculate_macros()
        if macros["calories"] < 10:
            return False, "La composante doit contenir au moins 10 kcal"

        return True, ""

    def to_dict(self) -> Dict:
        """
        Convertit la composante en dictionnaire.

        Returns:
            Représentation dict de la composante
        """
        return {
            "id": self.id,
            "name": self.name,
            "component_type": self.component_type,
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
    def from_dict(cls, data: Dict, foods_by_id: Dict[int, Food]) -> 'MealComponent':
        """
        Crée un MealComponent depuis un dictionnaire.

        Args:
            data: Dictionnaire avec les données
            foods_by_id: Mapping id -> Food pour récupérer les objets Food

        Returns:
            Instance de MealComponent
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
            component_type=data["component_type"],
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
    def from_db_row(cls, row_data: Dict, foods_by_id: Dict[int, Food]) -> 'MealComponent':
        """
        Crée un MealComponent depuis une ligne de base de données.

        Args:
            row_data: Dict avec id, name, component_type, foods_json, description
            foods_by_id: Mapping id -> Food

        Returns:
            Instance de MealComponent
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
            component_type=row_data["component_type"],
            description=row_data.get("description", ""),
            foods=foods
        )

    def __str__(self) -> str:
        """Représentation textuelle."""
        macros = self.calculate_macros()
        return (
            f"{self.name} ({self.component_type}): "
            f"{len(self.foods)} aliments, "
            f"{macros['calories']:.0f} kcal"
        )
