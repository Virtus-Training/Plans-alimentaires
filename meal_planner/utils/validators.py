"""
Fonctions de validation pour les données utilisateur
"""

from typing import Tuple


def validate_positive_number(value: float, field_name: str = "Valeur") -> Tuple[bool, str]:
    """
    Valide qu'un nombre est positif.

    Args:
        value: La valeur à valider
        field_name: Le nom du champ (pour le message d'erreur)

    Returns:
        Tuple (bool, str): (est_valide, message_erreur)
    """
    if not isinstance(value, (int, float)):
        return False, f"{field_name} doit être un nombre"

    if value < 0:
        return False, f"{field_name} doit être positif"

    return True, ""


def validate_range(value: float, min_val: float, max_val: float, field_name: str = "Valeur") -> Tuple[bool, str]:
    """
    Valide qu'une valeur est dans un intervalle donné.

    Args:
        value: La valeur à valider
        min_val: Valeur minimale
        max_val: Valeur maximale
        field_name: Le nom du champ

    Returns:
        Tuple (bool, str): (est_valide, message_erreur)
    """
    is_valid, msg = validate_positive_number(value, field_name)
    if not is_valid:
        return is_valid, msg

    if value < min_val or value > max_val:
        return False, f"{field_name} doit être entre {min_val} et {max_val}"

    return True, ""


def validate_macro_values(calories: float, proteins: float, carbs: float, fats: float) -> Tuple[bool, str]:
    """
    Valide la cohérence des valeurs macronutritionnelles.

    Vérifie que les calories calculées à partir des macros correspondent
    approximativement aux calories fournies.

    Args:
        calories: Calories totales (kcal)
        proteins: Protéines (g)
        carbs: Glucides (g)
        fats: Lipides (g)

    Returns:
        Tuple (bool, str): (est_valide, message_erreur)
    """
    # Valider que toutes les valeurs sont positives
    for value, name in [(calories, "Calories"), (proteins, "Protéines"),
                        (carbs, "Glucides"), (fats, "Lipides")]:
        is_valid, msg = validate_positive_number(value, name)
        if not is_valid:
            return is_valid, msg

    # Calculer les calories à partir des macros
    # Protéines: 4 kcal/g, Glucides: 4 kcal/g, Lipides: 9 kcal/g
    calculated_calories = (proteins * 4) + (carbs * 4) + (fats * 9)

    # Vérifier la cohérence (tolérance de 10%)
    tolerance = 0.10
    if abs(calculated_calories - calories) > (calories * tolerance):
        return False, (
            f"Les macros ne correspondent pas aux calories. "
            f"Calculé: {calculated_calories:.0f} kcal, Fourni: {calories:.0f} kcal"
        )

    return True, ""


def validate_string_not_empty(value: str, field_name: str = "Champ") -> Tuple[bool, str]:
    """
    Valide qu'une chaîne n'est pas vide.

    Args:
        value: La valeur à valider
        field_name: Le nom du champ

    Returns:
        Tuple (bool, str): (est_valide, message_erreur)
    """
    if not isinstance(value, str):
        return False, f"{field_name} doit être une chaîne de caractères"

    if not value or not value.strip():
        return False, f"{field_name} ne peut pas être vide"

    return True, ""


def validate_food_quantity(quantity: float) -> Tuple[bool, str]:
    """
    Valide la quantité d'un aliment (en grammes).

    Args:
        quantity: Quantité en grammes

    Returns:
        Tuple (bool, str): (est_valide, message_erreur)
    """
    from meal_planner.config import MIN_FOOD_QUANTITY, MAX_FOOD_QUANTITY

    return validate_range(
        quantity,
        MIN_FOOD_QUANTITY,
        MAX_FOOD_QUANTITY,
        "Quantité d'aliment"
    )
