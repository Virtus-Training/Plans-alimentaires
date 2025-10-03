"""
Filtres pour les régimes alimentaires spécifiques (Keto, Paléo, Méditerranéen)
"""

from typing import List, Dict, Optional
from meal_planner.models.food import Food
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.config import DIET_RULES
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


class DietFilter:
    """Filtre les aliments selon un régime alimentaire spécifique."""

    def __init__(self, diet_type: str):
        """
        Initialise le filtre pour un régime spécifique.

        Args:
            diet_type: Type de régime (keto, paleo, mediterranean)
        """
        self.diet_type = diet_type
        self.rules = DIET_RULES.get(diet_type, {})

        if not self.rules:
            logger.warning(f"Régime '{diet_type}' non reconnu, pas de filtrage appliqué")

    def filter_foods(self, foods: List[Food]) -> List[Food]:
        """
        Filtre les aliments selon les règles du régime.

        Args:
            foods: Liste d'aliments à filtrer

        Returns:
            Liste d'aliments compatibles avec le régime
        """
        if not self.rules:
            return foods

        if self.diet_type == "keto":
            return self._filter_keto(foods)
        elif self.diet_type == "paleo":
            return self._filter_paleo(foods)
        elif self.diet_type == "mediterranean":
            return self._filter_mediterranean(foods)

        return foods

    def _filter_keto(self, foods: List[Food]) -> List[Food]:
        """Filtre pour le régime keto (cétogène) - VERSION SOUPLE."""
        excluded_categories = self.rules.get("excluded_categories", [])
        allowed_low_carb = self.rules.get("allowed_low_carb_foods", [])

        filtered = []

        for food in foods:
            # Exclure strictement uniquement les céréales et féculents (pas tous)
            strict_exclusions = ["pain", "pâtes", "riz", "céréales"]
            is_strict_exclusion = any(
                excl.lower() in food.name.lower()
                for excl in strict_exclusions
            )

            if is_strict_exclusion:
                continue

            # Pour les autres, vérifier le ratio glucides mais être plus tolérant
            if food.calories > 0:
                carb_calories = food.carbs * 4
                carb_ratio = carb_calories / food.calories

                # Exclure seulement si TRÈS riche en glucides (>40%)
                if carb_ratio > 0.40:
                    # Mais autoriser les légumes même riches en glucides
                    if "légume" not in food.category.lower():
                        continue

            filtered.append(food)

        logger.info(f"Keto filter: {len(foods)} → {len(filtered)} aliments")
        return filtered

    def _filter_paleo(self, foods: List[Food]) -> List[Food]:
        """Filtre pour le régime paléo - VERSION SOUPLE."""
        # Exclusions strictes uniquement (vraiment transformés)
        strict_exclusions = ["pain", "pâtes", "riz", "blé", "lait", "yaourt", "fromage"]

        filtered = []

        for food in foods:
            # Exclure seulement les aliments vraiment interdits
            is_strict_exclusion = any(
                excl.lower() in food.name.lower()
                for excl in strict_exclusions
            )

            if is_strict_exclusion:
                # Exception pour patate douce
                if "patate" in food.name.lower():
                    filtered.append(food)
                continue

            filtered.append(food)

        logger.info(f"Paleo filter (souple): {len(foods)} → {len(filtered)} aliments")
        return filtered

    def _filter_mediterranean(self, foods: List[Food]) -> List[Food]:
        """
        Filtre pour le régime méditerranéen.
        Note: Le régime méditerranéen n'exclut pas vraiment d'aliments,
        mais priorise certaines catégories.
        """
        # Le régime méditerranéen ne bannit pas d'aliments,
        # donc tous les aliments passent le filtre
        # La priorisation se fait au niveau du scoring

        logger.info(f"Mediterranean filter: {len(foods)} aliments (pas d'exclusion)")
        return foods

    def prioritize_foods(self, foods: List[Food]) -> List[Food]:
        """
        Réorganise les aliments pour prioriser ceux du régime.

        Args:
            foods: Liste d'aliments

        Returns:
            Liste d'aliments réorganisée par priorité
        """
        if not self.rules:
            return foods

        prioritized_foods = self.rules.get("prioritized_foods", [])
        prioritized_categories = self.rules.get("prioritized_categories", [])
        limited_foods = self.rules.get("limited_foods", [])

        # Séparer en 3 groupes
        high_priority = []
        medium_priority = []
        low_priority = []

        for food in foods:
            # Vérifier si c'est un aliment à limiter
            is_limited = any(
                lim.lower() in food.name.lower() or lim.lower() in food.category.lower()
                for lim in limited_foods
            )

            if is_limited:
                low_priority.append(food)
                continue

            # Vérifier si c'est un aliment prioritaire
            is_prioritized_food = any(
                prio.lower() in food.name.lower() or prio.lower() in food.category.lower()
                for prio in prioritized_foods
            )

            is_prioritized_category = any(
                prio.lower() in food.category.lower()
                for prio in prioritized_categories
            )

            if is_prioritized_food or is_prioritized_category:
                high_priority.append(food)
            else:
                medium_priority.append(food)

        # Combiner dans l'ordre de priorité
        result = high_priority + medium_priority + low_priority

        logger.info(
            f"Diet prioritization ({self.diet_type}): "
            f"{len(high_priority)} high, {len(medium_priority)} medium, "
            f"{len(low_priority)} low priority"
        )

        return result

    def adjust_nutrition_target(self, target: NutritionTarget) -> NutritionTarget:
        """
        Ajuste l'objectif nutritionnel selon les règles du régime.

        Args:
            target: Objectif nutritionnel initial

        Returns:
            Objectif ajusté selon le régime
        """
        if not self.rules:
            return target

        total_calories = target.calories

        if self.diet_type == "keto":
            # Keto: 70% lipides, 20% protéines, 10% glucides
            carbs_max_percent = self.rules.get("carbs_max_percent", 0.10)
            fats_min_percent = self.rules.get("fats_min_percent", 0.70)
            proteins_percent = self.rules.get("proteins_percent", 0.20)

            new_carbs = (total_calories * carbs_max_percent) / 4  # 4 kcal/g
            new_fats = (total_calories * fats_min_percent) / 9   # 9 kcal/g
            new_proteins = (total_calories * proteins_percent) / 4  # 4 kcal/g

            logger.info(
                f"Keto adjustment: C:{new_carbs:.0f}g ({carbs_max_percent*100:.0f}%), "
                f"P:{new_proteins:.0f}g ({proteins_percent*100:.0f}%), "
                f"F:{new_fats:.0f}g ({fats_min_percent*100:.0f}%)"
            )

            return NutritionTarget(
                calories=total_calories,
                proteins=new_proteins,
                carbs=new_carbs,
                fats=new_fats
            )

        elif self.diet_type == "mediterranean":
            # Méditerranéen: 40-50% glucides, 30-40% lipides, 15-20% protéines
            carbs_range = self.rules.get("carbs_range", (0.45, 0.50))
            fats_range = self.rules.get("fats_range", (0.30, 0.35))
            proteins_range = self.rules.get("proteins_range", (0.15, 0.20))

            # Prendre le milieu des ranges
            carbs_percent = (carbs_range[0] + carbs_range[1]) / 2
            fats_percent = (fats_range[0] + fats_range[1]) / 2
            proteins_percent = (proteins_range[0] + proteins_range[1]) / 2

            new_carbs = (total_calories * carbs_percent) / 4
            new_fats = (total_calories * fats_percent) / 9
            new_proteins = (total_calories * proteins_percent) / 4

            logger.info(
                f"Mediterranean adjustment: C:{new_carbs:.0f}g ({carbs_percent*100:.0f}%), "
                f"P:{new_proteins:.0f}g ({proteins_percent*100:.0f}%), "
                f"F:{new_fats:.0f}g ({fats_percent*100:.0f}%)"
            )

            return NutritionTarget(
                calories=total_calories,
                proteins=new_proteins,
                carbs=new_carbs,
                fats=new_fats
            )

        # Pour paléo, pas d'ajustement spécifique des macros
        return target


def apply_diet_filter(
    foods: List[Food],
    diet_type: Optional[str],
    nutrition_target: Optional[NutritionTarget] = None
) -> tuple[List[Food], Optional[NutritionTarget]]:
    """
    Fonction utilitaire pour appliquer un filtre de régime.

    Args:
        foods: Liste d'aliments
        diet_type: Type de régime (keto, paleo, mediterranean, ou None)
        nutrition_target: Objectif nutritionnel à ajuster (optionnel)

    Returns:
        Tuple (aliments filtrés, objectif ajusté)
    """
    if not diet_type or diet_type not in DIET_RULES:
        return foods, nutrition_target

    diet_filter = DietFilter(diet_type)

    # Filtrer les aliments
    filtered_foods = diet_filter.filter_foods(foods)

    # Prioriser les aliments
    prioritized_foods = diet_filter.prioritize_foods(filtered_foods)

    # Ajuster l'objectif nutritionnel si fourni
    adjusted_target = nutrition_target
    if nutrition_target:
        adjusted_target = diet_filter.adjust_nutrition_target(nutrition_target)

    return prioritized_foods, adjusted_target
