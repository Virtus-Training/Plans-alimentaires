"""
Modèle Food - Représente un aliment avec ses valeurs nutritionnelles
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
import json

from meal_planner.utils.validators import (
    validate_positive_number,
    validate_string_not_empty
)


@dataclass
class Food:
    """
    Représente un aliment avec ses informations nutritionnelles (pour 100g).

    Attributes:
        id: Identifiant unique en base de données
        name: Nom de l'aliment
        category: Catégorie (viandes, légumes, etc.)
        calories: Calories pour 100g (kcal)
        proteins: Protéines pour 100g (g)
        carbs: Glucides pour 100g (g)
        fats: Lipides pour 100g (g)
        fibers: Fibres pour 100g (g)
        tags: Liste de tags (vegetarian, vegan, gluten_free, etc.)
    """

    name: str
    category: str
    calories: float
    proteins: float
    carbs: float
    fats: float
    fibers: float = 0.0
    tags: List[str] = field(default_factory=list)
    id: Optional[int] = None

    def validate(self) -> Tuple[bool, str]:
        """
        Valide les données de l'aliment.

        Returns:
            Tuple (bool, str): (est_valide, message_erreur)
        """
        # Valider le nom
        is_valid, msg = validate_string_not_empty(self.name, "Nom de l'aliment")
        if not is_valid:
            return is_valid, msg

        # Valider la catégorie
        is_valid, msg = validate_string_not_empty(self.category, "Catégorie")
        if not is_valid:
            return is_valid, msg

        # Valider les valeurs nutritionnelles
        nutritional_values = [
            (self.calories, "Calories"),
            (self.proteins, "Protéines"),
            (self.carbs, "Glucides"),
            (self.fats, "Lipides"),
            (self.fibers, "Fibres")
        ]

        for value, name in nutritional_values:
            is_valid, msg = validate_positive_number(value, name)
            if not is_valid:
                return is_valid, msg

        # Vérifier la cohérence calorique approximative
        calculated_calories = (self.proteins * 4) + (self.carbs * 4) + (self.fats * 9)
        if self.calories > 0 and calculated_calories > 0:
            # Tolérance de 20% pour tenir compte des arrondis et fibres
            tolerance = 0.20
            if abs(calculated_calories - self.calories) > (calculated_calories * tolerance):
                return False, (
                    f"Les macros ne correspondent pas aux calories. "
                    f"Calculé: {calculated_calories:.1f} kcal, Fourni: {self.calories:.1f} kcal"
                )

        # Valider que les tags sont bien des chaînes
        if not isinstance(self.tags, list):
            return False, "Les tags doivent être une liste"

        for tag in self.tags:
            if not isinstance(tag, str):
                return False, "Tous les tags doivent être des chaînes de caractères"

        return True, ""

    def calculate_for_quantity(self, quantity_grams: float) -> Dict[str, float]:
        """
        Calcule les valeurs nutritionnelles pour une quantité donnée.

        Args:
            quantity_grams: Quantité en grammes

        Returns:
            Dict contenant les valeurs nutritionnelles calculées

        Raises:
            ValueError: Si la quantité est négative
        """
        if quantity_grams < 0:
            raise ValueError("La quantité ne peut pas être négative")

        multiplier = quantity_grams / 100.0

        return {
            "quantity": quantity_grams,
            "calories": self.calories * multiplier,
            "proteins": self.proteins * multiplier,
            "carbs": self.carbs * multiplier,
            "fats": self.fats * multiplier,
            "fibers": self.fibers * multiplier
        }

    def has_tag(self, tag: str) -> bool:
        """
        Vérifie si l'aliment possède un tag donné.

        Args:
            tag: Le tag à vérifier

        Returns:
            True si le tag est présent
        """
        return tag.lower() in [t.lower() for t in self.tags]

    def matches_preferences(self, required_tags: List[str]) -> bool:
        """
        Vérifie si l'aliment correspond aux préférences diététiques.

        Args:
            required_tags: Liste des tags requis (ex: ["vegetarian", "gluten_free"])

        Returns:
            True si l'aliment possède tous les tags requis
        """
        if not required_tags:
            return True

        return all(self.has_tag(tag) for tag in required_tags)

    def to_dict(self) -> Dict:
        """
        Convertit l'aliment en dictionnaire.

        Returns:
            Dict représentant l'aliment
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "calories": self.calories,
            "proteins": self.proteins,
            "carbs": self.carbs,
            "fats": self.fats,
            "fibers": self.fibers,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Food':
        """
        Crée un objet Food à partir d'un dictionnaire.

        Args:
            data: Dictionnaire contenant les données

        Returns:
            Instance de Food
        """
        # Gérer les tags qui pourraient être en JSON string
        tags = data.get("tags", [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                tags = []

        return cls(
            id=data.get("id"),
            name=data["name"],
            category=data["category"],
            calories=float(data["calories"]),
            proteins=float(data["proteins"]),
            carbs=float(data["carbs"]),
            fats=float(data["fats"]),
            fibers=float(data.get("fibers", 0.0)),
            tags=tags if isinstance(tags, list) else []
        )

    def __str__(self) -> str:
        """Représentation textuelle de l'aliment."""
        return f"{self.name} ({self.category}) - {self.calories:.0f} kcal/100g"

    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (
            f"Food(id={self.id}, name='{self.name}', category='{self.category}', "
            f"calories={self.calories}, proteins={self.proteins}, "
            f"carbs={self.carbs}, fats={self.fats})"
        )
