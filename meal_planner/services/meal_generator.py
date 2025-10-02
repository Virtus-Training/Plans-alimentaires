"""
Service de génération de plans alimentaires intelligents
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import random
from collections import defaultdict

from meal_planner.models.food import Food
from meal_planner.models.meal import Meal
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MealDistribution:
    """Répartition des calories par type de repas."""
    breakfast: float = 0.25
    lunch: float = 0.40
    dinner: float = 0.30
    snack: float = 0.05


class MealGenerator:
    """
    Générateur intelligent de plans alimentaires.

    Utilise un algorithme d'optimisation pour sélectionner les aliments
    qui correspondent le mieux aux objectifs nutritionnels.
    """

    def __init__(
        self,
        available_foods: List[Food],
        nutrition_target: NutritionTarget,
        distribution: Optional[MealDistribution] = None,
        tolerance: float = 0.15,
        price_level: int = 5,
        health_index: int = 5,
        variety_level: int = 5
    ):
        """
        Initialise le générateur.

        Args:
            available_foods: Liste des aliments disponibles
            nutrition_target: Objectif nutritionnel quotidien
            distribution: Répartition des calories par repas
            tolerance: Tolérance acceptable pour les macros (15% par défaut)
            price_level: Niveau de prix souhaité (1-10)
            health_index: Indice de santé souhaité (1-10)
            variety_level: Niveau de variété souhaité (1-10)
        """
        self.available_foods = available_foods
        self.nutrition_target = nutrition_target
        self.distribution = distribution or MealDistribution()
        self.tolerance = tolerance
        self.price_level = price_level
        self.health_index = health_index
        self.variety_level = variety_level
        self.used_foods: Set[int] = set()  # Pour éviter les répétitions
        self.daily_accumulated_calories: float = 0.0  # Calories accumulées sur la journée

    def generate_meal(
        self,
        meal_type: str,
        day_number: int,
        target_percentage: float,
        is_last_meal_of_day: bool = False,
        min_foods: int = 4,
        max_foods: int = 7
    ) -> Meal:
        """
        Génère un repas optimal pour les objectifs donnés.

        Args:
            meal_type: Type de repas (breakfast, lunch, dinner, snack)
            day_number: Numéro du jour
            target_percentage: Pourcentage des calories quotidiennes
            is_last_meal_of_day: Si c'est le dernier repas de la journée
            min_foods: Nombre minimum d'aliments dans le repas
            max_foods: Nombre maximum d'aliments dans le repas

        Returns:
            Repas généré
        """
        # Calculer l'objectif nutritionnel pour ce repas
        meal_target = self.nutrition_target.scale_for_meal(target_percentage)

        # Ajuster l'objectif du repas selon l'accumulation journalière
        adjusted_target = self._adjust_meal_target(
            meal_target,
            target_percentage,
            is_last_meal_of_day
        )

        logger.info(
            f"Génération repas {meal_type} jour {day_number}: "
            f"cible ajustée {adjusted_target.calories:.0f} kcal "
            f"(objectif initial: {meal_target.calories:.0f} kcal, "
            f"accumulé: {self.daily_accumulated_calories:.0f} kcal)"
        )

        # Sélectionner les aliments
        selected_foods = self._select_foods_for_meal(
            adjusted_target,
            meal_type,
            min_foods,
            max_foods,
            is_last_meal_of_day
        )

        # Créer le repas
        meal = Meal(
            name=self._generate_meal_name(meal_type, day_number),
            meal_type=meal_type,
            target_calories=adjusted_target.calories,
            day_number=day_number
        )

        # Ajouter les aliments
        meal_calories = 0.0
        for food, quantity in selected_foods:
            meal.add_food(food, quantity)
            meal_calories += food.calculate_for_quantity(quantity)["calories"]

        # Mettre à jour l'accumulation journalière
        self.daily_accumulated_calories += meal_calories

        return meal

    def _adjust_meal_target(
        self,
        meal_target: NutritionTarget,
        target_percentage: float,
        is_last_meal: bool
    ) -> NutritionTarget:
        """
        Ajuste l'objectif du repas en fonction de l'accumulation journalière.

        Args:
            meal_target: Objectif calculé pour le repas
            target_percentage: Pourcentage calorique du repas
            is_last_meal: Si c'est le dernier repas de la journée

        Returns:
            Objectif ajusté
        """
        # Calculer combien il reste à consommer sur la journée
        remaining_daily = self.nutrition_target.calories - self.daily_accumulated_calories
        expected_for_meal = self.nutrition_target.calories * target_percentage

        # Si c'est le dernier repas, viser précisément ce qui reste
        if is_last_meal:
            adjusted_calories = max(0, remaining_daily)
            # Calculer un ratio d'ajustement
            if expected_for_meal > 0:
                adjustment_ratio = adjusted_calories / expected_for_meal
            else:
                adjustment_ratio = 1.0

            # Appliquer le ratio aux macros
            return NutritionTarget(
                calories=adjusted_calories,
                proteins=meal_target.proteins * adjustment_ratio,
                carbs=meal_target.carbs * adjustment_ratio,
                fats=meal_target.fats * adjustment_ratio
            )

        # Pour les autres repas, ajuster légèrement pour compenser les écarts
        deviation = self.daily_accumulated_calories - (
            self.nutrition_target.calories * sum([
                self.distribution.breakfast,
                self.distribution.lunch,
                self.distribution.dinner,
                self.distribution.snack
            ]) - self.nutrition_target.calories * (1 - target_percentage)
        )

        # Si on est en avance (trop de calories), réduire légèrement ce repas
        if deviation > 0:
            reduction_factor = 0.95  # Réduire de 5%
            return NutritionTarget(
                calories=meal_target.calories * reduction_factor,
                proteins=meal_target.proteins * reduction_factor,
                carbs=meal_target.carbs * reduction_factor,
                fats=meal_target.fats * reduction_factor
            )
        # Si on est en retard (pas assez de calories), augmenter légèrement
        elif deviation < -expected_for_meal * 0.1:  # Retard de plus de 10%
            increase_factor = 1.05  # Augmenter de 5%
            return NutritionTarget(
                calories=meal_target.calories * increase_factor,
                proteins=meal_target.proteins * increase_factor,
                carbs=meal_target.carbs * increase_factor,
                fats=meal_target.fats * increase_factor
            )

        # Sinon, garder l'objectif initial
        return meal_target

    def _select_foods_for_meal(
        self,
        target: NutritionTarget,
        meal_type: str,
        min_foods: int,
        max_foods: int,
        is_last_meal: bool = False
    ) -> List[Tuple[Food, float]]:
        """
        Sélectionne les aliments et quantités pour un repas.

        Utilise un algorithme glouton (greedy) qui optimise le ratio
        qualité nutritionnelle / calories.

        Args:
            target: Objectif nutritionnel du repas
            meal_type: Type de repas
            min_foods: Nombre minimum d'aliments
            max_foods: Nombre maximum d'aliments
            is_last_meal: Si c'est le dernier repas (tolérance plus stricte)

        Returns:
            Liste de tuples (Food, quantité_en_grammes)
        """
        selected = []
        current_macros = {"calories": 0.0, "proteins": 0.0, "carbs": 0.0, "fats": 0.0}

        # Filtrer les aliments disponibles (exclure ceux récemment utilisés)
        available = [
            f for f in self.available_foods
            if f.id not in self.used_foods
        ]

        # Si trop peu d'aliments disponibles, réinitialiser l'historique
        if len(available) < max_foods * 2:
            self.used_foods.clear()
            available = self.available_foods
            logger.info("Réinitialisation de l'historique des aliments utilisés")

        # Filtrer et prioriser selon le type de repas
        prioritized = self._filter_and_prioritize_by_meal_type(available, meal_type)

        if len(prioritized) < min_foods:
            logger.warning(
                f"Pas assez d'aliments appropriés pour {meal_type} "
                f"({len(prioritized)} disponibles, {min_foods} requis)"
            )
            # Fallback: utiliser tous les aliments disponibles
            prioritized = available

        # Sélectionner les aliments un par un
        for i in range(max_foods):
            if not prioritized:
                break

            # Trouver le meilleur aliment pour compléter les macros
            best_food, best_quantity, best_score = self._find_best_food(
                prioritized,
                target,
                current_macros,
                len(selected),
                is_last_meal
            )

            if best_food is None:
                break

            # Ajouter l'aliment sélectionné
            selected.append((best_food, best_quantity))
            self.used_foods.add(best_food.id)

            # Mettre à jour les macros actuelles
            food_macros = best_food.calculate_for_quantity(best_quantity)
            current_macros["calories"] += food_macros["calories"]
            current_macros["proteins"] += food_macros["proteins"]
            current_macros["carbs"] += food_macros["carbs"]
            current_macros["fats"] += food_macros["fats"]

            # Retirer l'aliment de la liste disponible
            prioritized = [f for f in prioritized if f.id != best_food.id]

            # Arrêter si on a atteint l'objectif avec les bonnes tolérances
            if len(selected) >= min_foods:
                cal_ratio = current_macros["calories"] / target.calories if target.calories > 0 else 0

                # Pour le dernier repas, viser précisément l'objectif
                if is_last_meal and 0.97 <= cal_ratio <= 1.05:
                    break
                # Pour les autres repas, accepter une plage plus large
                elif not is_last_meal and 0.90 <= cal_ratio <= 1.05:
                    break

        logger.info(
            f"Aliments sélectionnés: {len(selected)}, "
            f"Calories: {current_macros['calories']:.0f}/{target.calories:.0f}"
        )

        return selected

    def _find_best_food(
        self,
        available_foods: List[Food],
        target: NutritionTarget,
        current_macros: Dict[str, float],
        current_food_count: int,
        is_last_meal: bool = False
    ) -> Tuple[Optional[Food], float, float]:
        """
        Trouve le meilleur aliment pour compléter les macros actuelles.

        Args:
            available_foods: Aliments disponibles
            target: Objectif nutritionnel
            current_macros: Macros actuellement accumulées
            current_food_count: Nombre d'aliments déjà sélectionnés
            is_last_meal: Si c'est le dernier repas (plus strict)

        Returns:
            Tuple (meilleur_aliment, quantité_optimale, score)
        """
        best_food = None
        best_quantity = 0.0
        best_score = float('inf')

        # Calculer ce qu'il reste à atteindre
        remaining = {
            "calories": max(0, target.calories - current_macros["calories"]),
            "proteins": max(0, target.proteins - current_macros["proteins"]),
            "carbs": max(0, target.carbs - current_macros["carbs"]),
            "fats": max(0, target.fats - current_macros["fats"])
        }

        for food in available_foods:
            # Essayer différentes quantités
            quantities = self._get_reasonable_quantities(food, remaining["calories"])

            for quantity in quantities:
                food_macros = food.calculate_for_quantity(quantity)

                # Calculer le score nutritionnel de base (distance aux objectifs)
                macro_score = self._calculate_macro_distance(
                    food_macros,
                    remaining,
                    target,
                    current_macros
                )

                # Calculer les scores basés sur les critères utilisateur
                price_score = self._calculate_price_score(food, quantity)
                health_score = self._calculate_health_score(food)
                variety_score = self._calculate_variety_score(food)

                # Score composite pondéré
                score = (
                    macro_score * 0.50 +      # 50% priorité aux macros
                    price_score * 0.20 +       # 20% priorité au prix
                    health_score * 0.20 +      # 20% priorité à la santé
                    variety_score * 0.10       # 10% priorité à la variété
                )

                # Pénaliser plus fortement si ça dépasse les objectifs
                new_calories = current_macros["calories"] + food_macros["calories"]
                new_proteins = current_macros["proteins"] + food_macros["proteins"]
                new_fats = current_macros["fats"] + food_macros["fats"]

                # Pénalité si dépassement des calories (tolérance 5%)
                if new_calories > target.calories * 1.05:
                    score *= 5  # Pénalité forte

                # Pénalité si dépassement protéines (tolérance +10g)
                if new_proteins > target.proteins + 10:
                    score *= 3

                # Pénalité si dépassement lipides (tolérance +10g)
                if new_fats > target.fats + 10:
                    score *= 3

                if score < best_score:
                    best_score = score
                    best_food = food
                    best_quantity = quantity

        return best_food, best_quantity, best_score

    def _calculate_macro_distance(
        self,
        food_macros: Dict[str, float],
        remaining: Dict[str, float],
        target: NutritionTarget,
        current_macros: Dict[str, float]
    ) -> float:
        """
        Calcule la distance entre les macros de l'aliment et ce qu'il reste à atteindre.

        Plus le score est bas, meilleur est l'aliment.
        """
        # Distance pondérée pour chaque macro
        weights = {
            "calories": 1.5,  # Augmenter le poids des calories
            "proteins": 2.0,  # Prioriser les protéines
            "carbs": 1.0,
            "fats": 1.5
        }

        total_distance = 0.0

        for macro in ["calories", "proteins", "carbs", "fats"]:
            if target.__dict__[macro] > 0:
                # Normaliser par rapport à la cible
                expected_ratio = remaining[macro] / target.__dict__[macro]
                actual_ratio = food_macros[macro] / target.__dict__[macro]

                # Distance relative
                distance = abs(expected_ratio - actual_ratio)

                # Pénaliser davantage si l'aliment fait dépasser
                new_total = current_macros[macro] + food_macros[macro]
                if new_total > target.__dict__[macro]:
                    overshoot = (new_total - target.__dict__[macro]) / target.__dict__[macro]
                    distance += overshoot * 2  # Pénalité de dépassement

                total_distance += distance * weights[macro]

        return total_distance

    def _get_reasonable_quantities(
        self,
        food: Food,
        remaining_calories: float
    ) -> List[float]:
        """
        Retourne des quantités raisonnables à tester pour un aliment.
        Réduit les portions pour forcer plus d'aliments variés.

        Args:
            food: L'aliment
            remaining_calories: Calories restantes à atteindre

        Returns:
            Liste de quantités en grammes
        """
        # Quantité pour atteindre les calories restantes
        if food.calories > 0:
            optimal = (remaining_calories / food.calories) * 100
            # Réduire la quantité max pour forcer la variété
            optimal = max(20, min(optimal, 150))  # Entre 20g et 150g (réduit de 300g)
        else:
            optimal = 80

        # Catégories avec portions typiques réduites
        category_limits = {
            "huile": 15,  # Max 15g d'huile
            "matières grasses": 15,
            "noix": 30,  # Max 30g de noix
            "fromage": 40,  # Max 40g de fromage
        }

        # Appliquer les limites par catégorie
        for cat_name, max_qty in category_limits.items():
            if cat_name.lower() in food.category.lower():
                optimal = min(optimal, max_qty)

        # Tester quelques variations autour de l'optimal
        # S'assurer que toutes les quantités sont >= 10g (MIN_FOOD_QUANTITY)
        quantities = [
            optimal * 0.6,
            optimal * 0.8,
            optimal,
            optimal * 1.2
        ]

        # Filtrer les quantités trop petites
        return [q for q in quantities if q >= 10]

    def _filter_and_prioritize_by_meal_type(
        self,
        foods: List[Food],
        meal_type: str
    ) -> List[Food]:
        """
        Filtre et priorise les aliments selon le type de repas.
        Utilise les tags de repas si disponibles, sinon fallback sur les catégories.

        Args:
            foods: Liste d'aliments
            meal_type: Type de repas

        Returns:
            Liste d'aliments filtrés et triés par pertinence
        """
        # Définir les tags incompatibles pour chaque type de repas
        incompatible_tags = {
            "breakfast": ["lunch_only", "dinner_only"],
            "lunch": ["breakfast_only", "dinner_only"],
            "dinner": ["breakfast_only", "lunch_only"],
            "snack": [],  # Les collations peuvent inclure tous types d'aliments
            "afternoon_snack": [],
            "morning_snack": [],
            "evening_snack": []
        }

        # Exclure les aliments incompatibles
        excluded_tags = incompatible_tags.get(meal_type, [])
        filtered = [
            f for f in foods
            if not any(f.has_tag(tag) for tag in excluded_tags)
        ]

        # Filtrer par tags de type de repas si disponibles
        with_meal_tag = [f for f in filtered if f.has_tag(meal_type)]

        # Si pas assez d'aliments avec le tag, utiliser tous les aliments filtrés
        if len(with_meal_tag) < 3:
            logger.info(
                f"Peu d'aliments avec tag '{meal_type}' ({len(with_meal_tag)}), "
                f"utilisation de tous les aliments compatibles"
            )
            prioritized = filtered
        else:
            # Mélanger: 70% avec tag, 30% sans tag pour la variété
            without_tag = [f for f in filtered if not f.has_tag(meal_type)]
            prioritized = with_meal_tag.copy()

            # Ajouter quelques aliments sans tag pour la variété
            if without_tag:
                variety_count = max(1, len(with_meal_tag) // 3)
                random.shuffle(without_tag)
                prioritized.extend(without_tag[:variety_count])

        # Trier par catégories prioritaires
        priority_categories = {
            "breakfast": ["céréales", "produits laitiers", "fruits", "œufs"],
            "lunch": ["viandes", "poissons", "légumes", "féculents"],
            "dinner": ["viandes", "poissons", "légumes", "féculents"],
            "snack": ["fruits", "produits laitiers", "noix"],
            "afternoon_snack": ["fruits", "produits laitiers", "noix", "céréales"],
            "morning_snack": ["fruits", "produits laitiers", "noix"],
            "evening_snack": ["produits laitiers", "fruits", "noix"]
        }

        categories = priority_categories.get(meal_type, [])

        def priority_score(food: Food) -> int:
            # Bonus pour les aliments avec le bon tag
            has_tag_bonus = 0 if food.has_tag(meal_type) else 100

            # Score basé sur la catégorie
            for i, cat in enumerate(categories):
                if cat.lower() in food.category.lower():
                    return i + has_tag_bonus
            return len(categories) + has_tag_bonus

        prioritized.sort(key=priority_score)

        # Ajouter un peu de randomisation pour la variété
        for i in range(0, len(prioritized) - 1, 2):
            if random.random() < 0.3:  # 30% de chance d'inverser
                prioritized[i], prioritized[i + 1] = prioritized[i + 1], prioritized[i]

        return prioritized

    def _generate_meal_name(self, meal_type: str, day_number: int) -> str:
        """Génère un nom de repas."""
        type_names = {
            "breakfast": "Petit-déjeuner",
            "lunch": "Déjeuner",
            "dinner": "Dîner",
            "snack": "Collation",
            "afternoon_snack": "Goûter",
            "morning_snack": "Collation matinale",
            "evening_snack": "Collation soirée"
        }

        return f"{type_names.get(meal_type, meal_type)} - Jour {day_number}"

    def reset_used_foods(self) -> None:
        """Réinitialise l'historique des aliments utilisés."""
        self.used_foods.clear()

    def _calculate_price_score(self, food: Food, quantity: float) -> float:
        """
        Calcule le score de prix pour un aliment.
        Plus le score est bas, mieux c'est.

        Args:
            food: L'aliment à évaluer
            quantity: Quantité en grammes

        Returns:
            Score de prix (0-1, plus bas = meilleur)
        """
        # Calculer le prix pour la quantité
        food_price = (food.price_per_100g * quantity) / 100.0

        # Prix de référence moyen (à ajuster selon votre base de données)
        # On suppose un prix moyen de 0.50€ pour 100g
        avg_price = 0.50 * (quantity / 100.0)

        # Calculer l'écart de prix normalisé
        if avg_price > 0:
            price_ratio = food_price / avg_price
        else:
            price_ratio = 1.0

        # Adapter selon le niveau de prix souhaité par l'utilisateur
        # price_level: 1 (très bas) à 10 (premium)
        target_price_ratio = self.price_level / 5.0  # Normaliser 1-10 vers 0.2-2.0

        # Distance entre le prix de l'aliment et le prix souhaité
        distance = abs(price_ratio - target_price_ratio)

        # Normaliser entre 0 et 1
        return min(1.0, distance)

    def _calculate_health_score(self, food: Food) -> float:
        """
        Calcule le score de santé pour un aliment.
        Plus le score est bas, mieux c'est.

        Args:
            food: L'aliment à évaluer

        Returns:
            Score de santé (0-1, plus bas = meilleur)
        """
        # Distance entre l'indice de santé de l'aliment et l'indice souhaité
        distance = abs(food.health_index - self.health_index)

        # Normaliser sur une échelle de 0 à 9 (différence max possible)
        # puis inverser pour que 0 soit le meilleur
        return distance / 9.0

    def _calculate_variety_score(self, food: Food) -> float:
        """
        Calcule le score de variété pour un aliment.
        Plus le score est bas, mieux c'est.

        Args:
            food: L'aliment à évaluer

        Returns:
            Score de variété (0-1, plus bas = meilleur)
        """
        # Distance entre l'indice de variété de l'aliment et le niveau souhaité
        distance = abs(food.variety_index - self.variety_level)

        # Normaliser sur une échelle de 0 à 9 (différence max possible)
        return distance / 9.0
