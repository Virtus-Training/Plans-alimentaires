"""
Service de génération de plans alimentaires avec architecture modulaire.

Ce module fournit une architecture extensible pour différentes stratégies
de génération de repas:
- Par aliments individuels (FoodBasedGenerator)
- Par repas prédéfinis (PresetMealGenerator)
- Par composants entrée/plat/dessert (ComponentBasedGenerator)
- Par règles de catégories (CategoryBasedGenerator)
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod
import random
from collections import defaultdict
from pathlib import Path
import sys

from meal_planner.models.food import Food
from meal_planner.models.meal import Meal
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.utils.logger import get_logger

# Importer le module de compatibilité alimentaire
try:
    from meal_planner.data.food_compatibility import (
        calculate_meal_palatability,
        get_compatibility_score
    )
    COMPATIBILITY_AVAILABLE = True
except ImportError:
    COMPATIBILITY_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Module de compatibilité alimentaire non disponible")

# Importer l'optimiseur ILP
try:
    from meal_planner.services.ilp_optimizer import ILPMealOptimizer
    ILP_AVAILABLE = True
except ImportError:
    ILP_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Module ILP non disponible (PuLP non installé)")

# Importer la gestion de saisonnalité
try:
    from meal_planner.data.seasonal_foods import (
        get_seasonal_bonus,
        get_current_season,
        get_season_name
    )
    SEASONAL_AVAILABLE = True
except ImportError:
    SEASONAL_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Module de saisonnalité non disponible")

# Importer les règles de cohérence de repas
try:
    from meal_planner.data.meal_coherence_rules import (
        get_meal_coherence_score,
        get_combination_penalty
    )
    COHERENCE_RULES_AVAILABLE = True
except ImportError:
    COHERENCE_RULES_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Module de règles de cohérence non disponible")

logger = get_logger(__name__)


@dataclass
class MealDistribution:
    """Répartition des calories par type de repas."""
    breakfast: float = 0.25
    lunch: float = 0.40
    dinner: float = 0.30
    snack: float = 0.05


class MealGeneratorBase(ABC):
    """
    Classe de base abstraite pour tous les générateurs de repas.

    Contient les méthodes communes à tous les types de générateurs.
    """

    def __init__(
        self,
        available_foods: List[Food],
        nutrition_target: NutritionTarget,
        distribution: Optional[MealDistribution] = None,
        tolerance: float = 0.10,  # CORRECTION: Réduit de 0.15 à 0.10 (15% → 10%)
        price_level: int = 5,
        health_index: int = 5,
        variety_level: int = 5,
        feedback_system=None,
        use_ilp: bool = True
    ):
        """
        Initialise le générateur de base.

        Args:
            available_foods: Liste des aliments disponibles
            nutrition_target: Objectif nutritionnel quotidien
            distribution: Répartition des calories par repas
            tolerance: Tolérance acceptable pour les macros (15% par défaut)
            price_level: Niveau de prix souhaité (1-10)
            health_index: Indice de santé souhaité (1-10)
            variety_level: Niveau de variété souhaité (1-10)
            feedback_system: Système de feedback utilisateur optionnel
            use_ilp: Utiliser ILP si disponible
        """
        self.available_foods = available_foods
        self.nutrition_target = nutrition_target
        self.distribution = distribution or MealDistribution()
        self.tolerance = tolerance
        self.price_level = price_level
        self.health_index = health_index
        self.variety_level = variety_level
        self.used_foods: Set[int] = set()
        self.daily_accumulated_calories: float = 0.0
        self.feedback_system = feedback_system
        self.use_ilp = use_ilp and ILP_AVAILABLE

        # Créer l'optimiseur ILP si activé
        if self.use_ilp:
            self.ilp_optimizer = ILPMealOptimizer(
                min_quantity=10.0,
                max_quantity=500.0,
                tolerance=tolerance
            )
            logger.info(f"{self.__class__.__name__} initialisé avec optimisation ILP")
        else:
            self.ilp_optimizer = None
            logger.info(f"{self.__class__.__name__} initialisé avec algorithme hybride")

    @abstractmethod
    def generate_meal(
        self,
        meal_type: str,
        day_number: int,
        target_percentage: float,
        is_last_meal_of_day: bool = False,
        min_foods: int = 5,
        max_foods: int = 9
    ) -> Meal:
        """
        Génère un repas optimal pour les objectifs donnés.

        Cette méthode doit être implémentée par chaque sous-classe.

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
        pass

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

    def _calculate_solution_macros(self, solution: List[Tuple[Food, float]]) -> Dict[str, float]:
        """Calcule les macros totales d'une solution."""
        macros = {"calories": 0.0, "proteins": 0.0, "carbs": 0.0, "fats": 0.0}
        for food, qty in solution:
            food_macros = food.calculate_for_quantity(qty)
            for key in macros:
                macros[key] += food_macros[key]
        return macros

    def _round_to_practical_portion(self, quantity: float, food: Food) -> float:
        """
        Arrondit une quantité à une portion pratique et réaliste.
        Si l'aliment a un poids unitaire défini, arrondit au multiple d'unités le plus proche.

        Args:
            quantity: Quantité brute en grammes
            food: L'aliment concerné

        Returns:
            Quantité arrondie en grammes
        """
        # Si l'aliment a un poids unitaire défini, arrondir au nombre d'unités
        if food.unit_weight and food.unit_weight > 0:
            # Calculer le nombre d'unités nécessaires
            num_units = quantity / food.unit_weight

            # Arrondir au nombre entier d'unités le plus proche (min 1 unité)
            rounded_units = max(1, round(num_units))

            # LIMITE IMPORTANTE: Ne pas dépasser 3 unités pour éviter portions aberrantes
            # Ex: éviter 500g de poivron (3+ unités), préférer max 2 unités = 300g
            max_units = 3
            if rounded_units > max_units:
                rounded_units = max_units

            # Retourner le poids total pour ce nombre d'unités
            return rounded_units * food.unit_weight

        # Sinon, utiliser la logique par catégorie
        category_lower = food.category.lower()

        # Portions minimales selon la catégorie
        if any(cat in category_lower for cat in ["huile", "matières grasses"]):
            min_portion = 10  # Minimum 10g d'huile (environ 1 cuillère à soupe)
            if quantity < min_portion:
                return min_portion
            return round(quantity / 5) * 5  # Arrondir à 5g

        elif any(cat in category_lower for cat in ["épices", "condiments"]):
            min_portion = 5  # Minimum 5g pour épices
            if quantity < min_portion:
                return min_portion
            return round(quantity / 5) * 5

        elif any(cat in category_lower for cat in ["fromage", "beurre"]):
            min_portion = 20  # Minimum 20g de fromage/beurre
            if quantity < min_portion:
                return min_portion
            return round(quantity / 10) * 10  # Arrondir à 10g

        elif any(cat in category_lower for cat in ["lait", "boisson"]):
            min_portion = 100  # Minimum 100ml de lait
            if quantity < min_portion:
                return min_portion
            return round(quantity / 50) * 50  # Arrondir à 50ml

        elif any(cat in category_lower for cat in ["œuf"]):
            min_portion = 50  # Minimum 50g (1 œuf)
            if quantity < min_portion:
                return min_portion
            return round(quantity / 50) * 50  # Arrondir à 50g (par œuf)

        # Pour tous les autres aliments (viandes, légumes, féculents, etc.)
        min_portion = 30  # Minimum 30g pour portion visible

        if quantity < min_portion:
            return min_portion
        elif quantity < 50:
            return round(quantity / 10) * 10
        elif quantity < 100:
            return round(quantity / 20) * 20
        elif quantity < 200:
            return round(quantity / 25) * 25
        else:
            return round(quantity / 50) * 50


class FoodBasedGenerator(MealGeneratorBase):
    """
    Générateur de repas basé sur la sélection d'aliments individuels.

    C'est l'implémentation originale du MealGenerator qui utilise
    un algorithme d'optimisation pour sélectionner les aliments
    qui correspondent le mieux aux objectifs nutritionnels.
    """

    def generate_meal(
        self,
        meal_type: str,
        day_number: int,
        target_percentage: float,
        is_last_meal_of_day: bool = False,
        min_foods: int = 5,
        max_foods: int = 9
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
        # CORRECTION CRITIQUE: Ajuster min/max_foods pour les collations
        # Problème identifié : collations avec 9 aliments dépassent massivement la cible (+200-500%)
        if "snack" in meal_type.lower():
            min_foods = 2  # Minimum 2 aliments pour une collation
            max_foods = 4  # Maximum 4 aliments pour rester léger

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

        # Sélectionner les aliments avec le type de repas
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

        Utilise un algorithme hybride:
        1. Sélection gloutonne avec backtracking
        2. Score de compatibilité alimentaire
        3. Optimisation par recherche locale

        Args:
            target: Objectif nutritionnel du repas
            meal_type: Type de repas
            min_foods: Nombre minimum d'aliments
            max_foods: Nombre maximum d'aliments
            is_last_meal: Si c'est le dernier repas (tolérance plus stricte)

        Returns:
            Liste de tuples (Food, quantité_en_grammes)
        """
        # Filtrer les aliments disponibles (exclure ceux récemment utilisés)
        available = [
            f for f in self.available_foods
            if f.id not in self.used_foods
        ]

        # CORRECTION: Augmenter le seuil de réinitialisation pour plus de variété
        # Problème identifié : aliments répétés jusqu'à 10× sur 7 jours
        # Anciennement: max_foods * 3, maintenant: max_foods * 5 pour plus de variété
        if len(available) < max_foods * 5:
            self.used_foods.clear()
            available = self.available_foods
            logger.info("Réinitialisation de l'historique des aliments utilisés")

        # CORRECTION CRITIQUE: Filtrer les aliments trop riches en glucides pour profils low-carb
        # Problème identifié : Pois cassés (41g glucides) systématiquement sélectionnés
        if target.carbs < 150:  # Profil faible en glucides
            # Calculer le seuil acceptable de glucides par aliment (pour 100g)
            # Si cible totale = 100g, un aliment ne devrait pas avoir >15g/100g
            max_carbs_per_100g = target.carbs * 0.15  # 15% de la cible quotidienne

            carb_filtered = []
            for food in available:
                # Exclure les aliments dont les glucides dépassent le seuil
                # SAUF s'ils sont très faibles en calories (légumes verts)
                if food.carbs <= max_carbs_per_100g or food.calories < 50:
                    carb_filtered.append(food)
                else:
                    logger.debug(f"Aliment exclu (low-carb): {food.name} ({food.carbs:.1f}g glucides/100g)")

            if len(carb_filtered) >= min_foods:
                available = carb_filtered
                logger.info(f"Filtrage low-carb: {len(carb_filtered)}/{len(available)} aliments conservés")
            else:
                logger.warning(f"Filtrage low-carb trop strict, conservé tous les aliments")

        # Filtrer et prioriser selon le type de repas
        prioritized = self._filter_and_prioritize_by_meal_type(available, meal_type)

        if len(prioritized) < min_foods:
            logger.warning(
                f"Pas assez d'aliments appropriés pour {meal_type} "
                f"({len(prioritized)} disponibles, {min_foods} requis)"
            )
            prioritized = available

        # Essayer d'abord ILP si disponible
        if self.use_ilp and self.ilp_optimizer and len(prioritized) >= min_foods:
            logger.info(f"Tentative d'optimisation ILP pour {meal_type}")

            # Préparer les scores de compatibilité INCLUANT le variety_level
            # CRUCIAL: Intégrer le variety_level dans les scores ILP
            compatibility_scores = {}
            for food in prioritized:
                # Score de base: préférence utilisateur
                base_score = 0.5
                if COMPATIBILITY_AVAILABLE and self.feedback_system:
                    base_score = self.feedback_system.get_food_preference_score(food.id)

                # AJOUT: Bonus/malus TRÈS FORT en fonction du variety_level
                # Plus l'aliment est proche du variety_level souhaité, meilleur est le score
                variety_distance = abs(food.variety_index - self.variety_level)

                # Pénalité exponentielle pour forcer le respect du variety_level dans ILP
                # distance=0 -> pénalité=0 (parfait)
                # distance=1 -> pénalité=-0.2
                # distance=2 -> pénalité=-0.5
                # distance=3 -> pénalité=-1.0
                # distance=4+ -> pénalité=-2.0 (quasi-éliminé)
                if variety_distance == 0:
                    variety_penalty = 0.0
                elif variety_distance == 1:
                    variety_penalty = -0.2
                elif variety_distance == 2:
                    variety_penalty = -0.5
                elif variety_distance == 3:
                    variety_penalty = -1.0
                else:
                    variety_penalty = -2.0

                # Score final combiné
                compatibility_scores[food.id] = base_score + variety_penalty

            # Essayer l'optimisation ILP
            ilp_solution, is_optimal = self.ilp_optimizer.optimize_with_fallback(
                prioritized,
                target,
                min_foods,
                max_foods,
                compatibility_scores
            )

            if ilp_solution:
                # Marquer les aliments utilisés
                for food, _ in ilp_solution:
                    self.used_foods.add(food.id)

                current_macros = self._calculate_solution_macros(ilp_solution)
                logger.info(
                    f"ILP {'optimal' if is_optimal else 'sous-optimal'}: "
                    f"{len(ilp_solution)} aliments, "
                    f"{current_macros['calories']:.0f}/{target.calories:.0f} kcal"
                )
                return ilp_solution

            logger.info("ILP a échoué, fallback sur algorithme hybride")

        # Générer plusieurs solutions candidates avec l'algorithme hybride
        best_solution = None
        best_solution_score = float('inf')

        # Essayer 3 approches différentes
        for attempt in range(3):
            # Randomiser légèrement l'ordre pour explorer différentes solutions
            if attempt > 0:
                random.shuffle(prioritized)

            solution = self._greedy_selection(
                prioritized.copy(),
                target,
                min_foods,
                max_foods,
                is_last_meal,
                meal_type  # Ajouter le type de repas
            )

            # Évaluer la qualité de cette solution
            solution_score = self._evaluate_solution_quality(solution, target)

            if solution_score < best_solution_score:
                best_solution_score = solution_score
                best_solution = solution

        # Optimisation locale: essayer d'améliorer la solution
        if best_solution and len(best_solution) >= min_foods:
            optimized = self._local_optimization(
                best_solution,
                prioritized,
                target,
                max_foods
            )
            optimized_score = self._evaluate_solution_quality(optimized, target)

            if optimized_score < best_solution_score:
                best_solution = optimized

        # Marquer les aliments utilisés
        for food, _ in best_solution:
            self.used_foods.add(food.id)

        current_macros = self._calculate_solution_macros(best_solution)
        logger.info(
            f"Aliments sélectionnés: {len(best_solution)}, "
            f"Calories: {current_macros['calories']:.0f}/{target.calories:.0f}, "
            f"Score qualité: {best_solution_score:.2f}"
        )

        return best_solution

    def _greedy_selection(
        self,
        prioritized: List[Food],
        target: NutritionTarget,
        min_foods: int,
        max_foods: int,
        is_last_meal: bool,
        meal_type: str = ""
    ) -> List[Tuple[Food, float]]:
        """Sélection gloutonne standard."""
        selected = []
        current_macros = {"calories": 0.0, "proteins": 0.0, "carbs": 0.0, "fats": 0.0}

        for i in range(max_foods):
            if not prioritized:
                break

            best_food, best_quantity, best_score = self._find_best_food(
                prioritized,
                target,
                current_macros,
                len(selected),
                is_last_meal,
                selected,  # Passer les aliments déjà sélectionnés pour compatibilité
                meal_type  # Passer le type de repas pour cohérence
            )

            if best_food is None:
                break

            selected.append((best_food, best_quantity))

            food_macros = best_food.calculate_for_quantity(best_quantity)
            current_macros["calories"] += food_macros["calories"]
            current_macros["proteins"] += food_macros["proteins"]
            current_macros["carbs"] += food_macros["carbs"]
            current_macros["fats"] += food_macros["fats"]

            prioritized = [f for f in prioritized if f.id != best_food.id]

            # Vérifier si on peut s'arrêter (seulement après le minimum)
            if len(selected) >= min_foods:
                cal_ratio = current_macros["calories"] / target.calories if target.calories > 0 else 0

                # Conditions d'arrêt plus strictes pour éviter de toujours avoir le minimum
                # On s'arrête seulement si on est vraiment proche de la cible
                if is_last_meal:
                    # Dernier repas: être très précis (95-105%)
                    if 0.95 <= cal_ratio <= 1.05:
                        break
                else:
                    # Autres repas: être assez précis (92-103%)
                    # Mais continuer si on est en dessous ET qu'on n'a pas atteint max_foods
                    if 0.92 <= cal_ratio <= 1.03:
                        # Ajouter un facteur aléatoire pour la variabilité
                        # 60% de chance de s'arrêter, 40% de continuer pour plus de variété
                        if random.random() < 0.6 or len(selected) >= max_foods - 1:
                            break

        return selected

    def _evaluate_solution_quality(
        self,
        solution: List[Tuple[Food, float]],
        target: NutritionTarget
    ) -> float:
        """
        Évalue la qualité globale d'une solution.
        Plus le score est bas, meilleure est la solution.
        """
        if not solution:
            return float('inf')

        macros = self._calculate_solution_macros(solution)

        # Score nutritionnel (distance aux objectifs)
        nutrition_score = 0.0
        weights = {"calories": 2.0, "proteins": 2.5, "carbs": 1.0, "fats": 1.2}

        for macro in ["calories", "proteins", "carbs", "fats"]:
            target_val = getattr(target, macro)
            if target_val > 0:
                deviation = abs(macros[macro] - target_val) / target_val
                nutrition_score += deviation * weights[macro]

        # Score de palatabilité (compatibilité des aliments)
        palatability_score = 1.0
        if COMPATIBILITY_AVAILABLE and len(solution) > 1:
            foods = [f.name for f, _ in solution]
            categories = [f.category for f, _ in solution]
            palatability = calculate_meal_palatability(foods, categories)
            palatability_score = 1.0 - palatability  # Inverser (bas = bon)

        # Score composite
        total_score = nutrition_score + palatability_score * 0.3

        return total_score

    def _local_optimization(
        self,
        solution: List[Tuple[Food, float]],
        available: List[Food],
        target: NutritionTarget,
        max_foods: int
    ) -> List[Tuple[Food, float]]:
        """
        Optimisation locale: essayer de remplacer des aliments pour améliorer la solution.
        """
        best_solution = solution.copy()
        best_score = self._evaluate_solution_quality(best_solution, target)

        # Essayer de remplacer chaque aliment
        for i in range(len(solution)):
            food_to_replace, qty = solution[i]

            # Essayer des aliments alternatifs
            for alt_food in available[:10]:  # Limiter à 10 alternatives
                if alt_food.id == food_to_replace.id:
                    continue

                # Créer une solution alternative
                alt_solution = solution.copy()
                alt_solution[i] = (alt_food, qty)

                alt_score = self._evaluate_solution_quality(alt_solution, target)

                if alt_score < best_score:
                    best_score = alt_score
                    best_solution = alt_solution

        return best_solution

    def _find_best_food(
        self,
        available_foods: List[Food],
        target: NutritionTarget,
        current_macros: Dict[str, float],
        current_food_count: int,
        is_last_meal: bool = False,
        selected_foods: List[Tuple[Food, float]] = None,
        meal_type: str = ""
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
            # RÈGLE STRICTE PALATABILITÉ: Si un féculent est déjà sélectionné, interdire un autre féculent
            # CORRECTION: Toujours appliquer cette règle + détecter les variations du même féculent
            if selected_foods:
                try:
                    from meal_planner.data.meal_coherence_rules import is_starch_food, get_starch_base_name

                    # Vérifier si un féculent est déjà dans le repas
                    existing_starches = []
                    for sf, _ in selected_foods:
                        if is_starch_food(sf.category, sf.name):
                            # Stocker le nom de base pour détecter les variantes
                            existing_starches.append(get_starch_base_name(sf.name))

                    # Si food actuel est un féculent
                    if is_starch_food(food.category, food.name):
                        # Vérifier si c'est le même type de féculent (ou un autre)
                        current_base = get_starch_base_name(food.name)

                        # INTERDIRE si:
                        # 1. C'est un féculent différent (base différente)
                        # 2. OU c'est le même féculent mais déjà présent
                        if existing_starches and (
                            current_base in existing_starches or  # Même féculent
                            len(existing_starches) > 0  # Ou féculent différent
                        ):
                            continue  # SKIP cet aliment complètement
                except ImportError:
                    # Si module non disponible, continuer sans cette vérification
                    pass

            # Essayer différentes quantités ARRONDIES dès le départ
            quantities = self._get_reasonable_quantities(food, remaining["calories"])

            for quantity in quantities:
                # Forcer l'arrondi pour maximiser les portions pratiques
                quantity = self._round_to_practical_portion(quantity, food)

                # FILTRE CRITIQUE: Exclure les portions trop petites ou trop grandes
                # Portions minimales selon la catégorie FINE
                category_lower = food.category.lower()
                food_name_lower = food.name.lower()

                # Définir portion minimale acceptable par catégorie fine
                # Chercher dans catégorie ET nom pour plus de robustesse
                combined_text = (category_lower + " " + food_name_lower).lower()

                if any(cat in combined_text for cat in ["huile", "matiere", "matieres", "grasse", "grasses"]):
                    min_acceptable = 10  # Huiles: min 10g (1 cuillère à soupe)
                elif any(cat in combined_text for cat in ["epice", "épice", "condiment"]):
                    min_acceptable = 5  # Épices/condiments: min 5g
                elif any(cat in combined_text for cat in ["chocolat", "cacao"]):
                    min_acceptable = 20  # Chocolat: min 20g (2 carrés)
                elif any(word in combined_text for word in ["graine", "noix", "amande", "noisette", "cacahuete", "cacahuète", "sesame", "sésame", "chia", "lin", "tournesol", "pecan", "cajou"]):
                    min_acceptable = 20  # Noix/graines: min 20g (poignée minimale)
                elif any(cat in combined_text for cat in ["fromage", "beurre"]):
                    min_acceptable = 30  # Fromages: min 30g
                elif any(word in combined_text for word in ["lait", "yaourt", "skyr", "fromage blanc", "kefir", "kéfir", "cottage"]):
                    min_acceptable = 100  # Laitages liquides: min 100g/ml
                else:
                    min_acceptable = 30  # Minimum 30g pour tous les autres aliments

                # Exclure les portions trop petites
                if quantity < min_acceptable:
                    continue

                # Exclure les portions trop grandes (sauf légumes/salades)
                max_acceptable = 500 if any(cat in category_lower for cat in ["légumes", "salade"]) else 300
                if quantity > max_acceptable:
                    continue

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

                # Calculer le score de compatibilité avec les aliments déjà sélectionnés
                compatibility_score = self._calculate_compatibility_score(food, selected_foods)

                # NOUVEAU: Calculer le score de cohérence avec le type de repas
                coherence_score = 0.0
                if COHERENCE_RULES_AVAILABLE and meal_type:
                    # Score de cohérence de cet aliment pour ce type de repas
                    meal_coherence = get_meal_coherence_score(food.category, meal_type)

                    # Pénalités pour combinaisons incohérentes avec les aliments déjà dans le repas
                    combination_penalty = 0.0
                    if selected_foods:
                        for selected_food, _ in selected_foods:
                            # AMÉLIORATION: Passer aussi les noms pour détecter les féculents
                            penalty = get_combination_penalty(
                                food.category,
                                selected_food.category,
                                food.name,
                                selected_food.name
                            )
                            combination_penalty = max(combination_penalty, penalty)  # Prendre la pire pénalité

                    # Score final de cohérence (1 = parfait, 0 = incohérent)
                    # Plus le meal_coherence est haut, plus le score est bas (bon)
                    # Plus la pénalité est haute, plus le score est haut (mauvais)
                    coherence_score = (1.0 - meal_coherence) + combination_penalty
                else:
                    coherence_score = 0.5  # Neutre si pas de règles disponibles

                # Score composite pondéré - AMÉLIORATION PALATABILITÉ ET VARIÉTÉ
                # CORRECTION: Augmenter le poids de la variété pour réduire répétitivité
                score = (
                    macro_score * 0.26 +           # 26% priorité aux macros (réduit de 28%)
                    price_score * 0.06 +           # 6% priorité au prix (réduit de 7%)
                    health_score * 0.05 +          # 5% priorité à la santé (inchangé)
                    variety_score * 0.28 +         # 28% priorité à la variété (augmenté de 25% pour moins de répétition)
                    compatibility_score * 0.15 +   # 15% priorité à la compatibilité alimentaire (inchangé)
                    coherence_score * 0.20         # 20% pénalité de cohérence repas (inchangé)
                )

                # Pénaliser plus fortement si ça dépasse les objectifs
                new_calories = current_macros["calories"] + food_macros["calories"]
                new_proteins = current_macros["proteins"] + food_macros["proteins"]
                new_carbs = current_macros["carbs"] + food_macros["carbs"]
                new_fats = current_macros["fats"] + food_macros["fats"]

                # CORRECTION: Pénalité progressive pour dépassement calories
                # Problème identifié : dépassement systématique de +12-20%
                calories_overshoot = new_calories - target.calories
                if calories_overshoot > 0:
                    # Pénalité progressive selon l'importance du dépassement
                    if calories_overshoot > target.calories * 0.10:  # Dépassement >10%
                        score *= 8  # Pénalité très forte
                    elif calories_overshoot > target.calories * 0.05:  # Dépassement >5%
                        score *= 5   # Pénalité forte
                    elif calories_overshoot > target.calories * 0.02:  # Dépassement >2%
                        score *= 2   # Pénalité modérée

                # Pénalité si dépassement protéines (tolérance +10g)
                if new_proteins > target.proteins + 10:
                    score *= 3

                # CORRECTION CRITIQUE: Pénalité EXPONENTIELLE pour dépassement glucides
                # C'est le problème majeur identifié dans l'analyse
                carbs_overshoot = new_carbs - target.carbs
                if carbs_overshoot > 0:
                    # Pénalité progressive selon l'importance du dépassement
                    if carbs_overshoot > target.carbs * 0.15:  # Dépassement >15%
                        score *= 15  # Pénalité maximale (augmenté de 10)
                    elif carbs_overshoot > target.carbs * 0.08:  # Dépassement >8%
                        score *= 8   # Pénalité très forte (augmenté de 6)
                    elif carbs_overshoot > target.carbs * 0.03:  # Dépassement >3%
                        score *= 4   # Pénalité forte (augmenté de 3)
                    elif carbs_overshoot > 0:  # Tout dépassement
                        score *= 1.5  # Pénalité modérée

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
        # CORRECTION: Augmenter le poids des glucides pour meilleur contrôle
        weights = {
            "calories": 2.0,  # Forte priorité aux calories (augmenté de 1.8)
            "proteins": 2.5,  # Très forte priorité aux protéines (inchangé)
            "carbs": 1.8,     # Forte priorité aux glucides (augmenté de 1.0 à 1.8)
            "fats": 1.2       # Priorité modérée aux lipides (inchangé)
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

        # Bonus pour les aliments riches en protéines (ratio protéines/calories élevé)
        if food_macros["calories"] > 0:
            protein_ratio = food_macros["proteins"] / (food_macros["calories"] / 100)  # g protéines pour 100 kcal
            # Si l'aliment a un bon ratio protéines (>5g pour 100 kcal), réduire le score
            if protein_ratio > 5:
                total_distance *= 0.8  # Bonus 20%

        return total_distance

    def _get_reasonable_quantities(
        self,
        food: Food,
        remaining_calories: float
    ) -> List[float]:
        """
        Retourne des quantités raisonnables et PRATIQUES à tester pour un aliment.
        Génère directement des portions arrondies pour maximiser la praticité.

        Args:
            food: L'aliment
            remaining_calories: Calories restantes à atteindre

        Returns:
            Liste de quantités en grammes arrondies (portions pratiques)
        """
        # Quantité pour atteindre les calories restantes
        if food.calories > 0:
            optimal = (remaining_calories / food.calories) * 100

            # Définir min selon la catégorie FINE
            category_lower = food.category.lower()
            food_name_lower = food.name.lower()
            combined_text = (category_lower + " " + food_name_lower).lower()

            if any(cat in combined_text for cat in ["huile", "matiere", "matieres", "grasse", "grasses"]):
                min_qty = 10
            elif any(cat in combined_text for cat in ["epice", "épice", "condiment"]):
                min_qty = 5
            elif any(cat in combined_text for cat in ["chocolat", "cacao"]):
                min_qty = 20
            elif any(word in combined_text for word in ["graine", "noix", "amande", "noisette", "cacahuete", "cacahuète", "sesame", "sésame", "chia", "lin", "tournesol", "pecan", "cajou"]):
                min_qty = 20
            elif any(cat in combined_text for cat in ["fromage", "beurre"]):
                min_qty = 30
            elif any(word in combined_text for word in ["lait", "yaourt", "skyr", "fromage blanc", "kefir", "kéfir", "cottage"]):
                min_qty = 100
            else:
                min_qty = 30

            # Réduire la quantité max pour forcer la variété
            optimal = max(min_qty, min(optimal, 150))
        else:
            optimal = 80

        # Catégories avec portions typiques ARRONDIES et réalistes
        category_limits = {
            "huile": 15,  # Max 15g d'huile (1 cuillère à soupe)
            "matières grasses": 15,
            "noix": 30,  # Max 30g de noix (1 poignée)
            "fromage": 40,  # Max 40g de fromage
            "œufs": 100,  # Max 100g d'œufs (environ 2 œufs moyens)
            "viandes": 150,  # Max 150g de viande par repas
            "poissons": 150,  # Max 150g de poisson par repas
        }

        # Appliquer les limites par catégorie
        for cat_name, max_qty in category_limits.items():
            if cat_name.lower() in food.category.lower():
                optimal = min(optimal, max_qty)

        # Limites spécifiques pour certains aliments denses en calories
        if food.calories > 500:  # Aliments très caloriques (huiles, noix, etc.)
            optimal = min(optimal, 30)
        elif food.calories > 300:  # Aliments caloriques (fromages, viandes grasses)
            optimal = min(optimal, 100)

        # Générer des quantités PRATIQUES dès le départ
        # Au lieu de variations arbitraires, utiliser des multiples standards
        rounded_optimal = self._round_to_practical_portion(optimal, food)

        # Générer des variations PRATIQUES autour de l'optimal
        practical_variations = set()  # Set pour éviter les doublons

        # Ajouter la quantité optimale arrondie
        practical_variations.add(rounded_optimal)

        # Ajouter des variations plus petites et plus grandes en respectant les multiples
        increment = self._get_practical_increment(rounded_optimal)

        # Déterminer le minimum acceptable selon la catégorie FINE
        category_lower = food.category.lower()
        food_name_lower = food.name.lower()
        combined_text = (category_lower + " " + food_name_lower).lower()

        if any(cat in combined_text for cat in ["huile", "matiere", "matieres", "grasse", "grasses"]):
            min_acceptable = 10
        elif any(cat in combined_text for cat in ["epice", "épice", "condiment"]):
            min_acceptable = 5
        elif any(cat in combined_text for cat in ["chocolat", "cacao"]):
            min_acceptable = 20
        elif any(word in combined_text for word in ["graine", "noix", "amande", "noisette", "cacahuete", "cacahuète", "sesame", "sésame", "chia", "lin", "tournesol", "pecan", "cajou"]):
            min_acceptable = 20
        elif any(cat in combined_text for cat in ["fromage", "beurre"]):
            min_acceptable = 30
        elif any(word in combined_text for word in ["lait", "yaourt", "skyr", "fromage blanc", "kefir", "kéfir", "cottage"]):
            min_acceptable = 100
        else:
            min_acceptable = 30

        if rounded_optimal - increment >= min_acceptable:
            practical_variations.add(rounded_optimal - increment)
        if rounded_optimal - 2 * increment >= min_acceptable:
            practical_variations.add(rounded_optimal - 2 * increment)

        practical_variations.add(rounded_optimal + increment)
        practical_variations.add(rounded_optimal + 2 * increment)

        # Filtrer et trier avec le minimum acceptable
        return sorted([q for q in practical_variations if q >= min_acceptable and q <= 500])

    def _get_practical_increment(self, quantity: float) -> float:
        """
        Retourne l'incrément pratique selon la taille de la quantité.

        Args:
            quantity: Quantité de référence

        Returns:
            Incrément pratique (5, 10, 20, 25 ou 50g)
        """
        if quantity < 20:
            return 5
        elif quantity < 50:
            return 10
        elif quantity < 100:
            return 20
        elif quantity < 200:
            return 25
        else:
            return 50

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

        # AMÉLIORATION: Définir des catégories incompatibles par type de repas
        # pour éviter les combinaisons absurdes (ex: poisson au petit-déjeuner)
        incompatible_categories = {
            "breakfast": ["poissons", "viandes"],  # Sauf exceptions (saumon fumé géré par tags)
            "afternoon_snack": ["viandes", "poissons"],
            "morning_snack": ["viandes", "poissons"],
            "evening_snack": ["viandes", "poissons"]
        }

        # Exclure les aliments incompatibles par tags
        excluded_tags = incompatible_tags.get(meal_type, [])
        filtered = [
            f for f in foods
            if not any(f.has_tag(tag) for tag in excluded_tags)
        ]

        # NOUVEAU: Exclure aussi par catégories incompatibles
        excluded_categories = incompatible_categories.get(meal_type, [])
        if excluded_categories:
            # Exception: autoriser saumon fumé au petit-déjeuner même si c'est du poisson
            filtered = [
                f for f in filtered
                if not any(cat in f.category.lower() for cat in excluded_categories)
                or "fumé" in f.name.lower()  # Exception pour produits fumés
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
        RENFORCÉ pour une meilleure influence du variety_level.

        Args:
            food: L'aliment à évaluer

        Returns:
            Score de variété (0-1, plus bas = meilleur)
        """
        # Distance entre l'indice de variété de l'aliment et le niveau souhaité
        # AUGMENTÉ: Multiplier la distance par un facteur pour plus d'influence
        distance = abs(food.variety_index - self.variety_level)

        # NOUVELLE APPROCHE: Pénalité EXPONENTIELLE pour forcer le respect du variety_level
        # Plus la distance est grande, plus la pénalité augmente de manière disproportionnée
        # Cela garantit qu'un variety_level de 9 sélectionne vraiment des aliments exotiques

        # Calculer une pénalité exponentielle
        # distance=0 -> score=0.0 (parfait)
        # distance=1 -> score=0.1
        # distance=2 -> score=0.25
        # distance=3 -> score=0.5
        # distance=4 -> score=0.75
        # distance=5+ -> score=1.0 (très mauvais)

        if distance == 0:
            distance_score = 0.0  # Parfait match
        elif distance == 1:
            distance_score = 0.15  # Acceptable
        elif distance == 2:
            distance_score = 0.35  # Pénalité notable
        elif distance == 3:
            distance_score = 0.60  # Forte pénalité
        elif distance == 4:
            distance_score = 0.85  # Très forte pénalité
        else:  # distance >= 5
            distance_score = 1.0  # Presque éliminé

        # Pénalité de répétition (aliments déjà utilisés dans le plan)
        # OPTIMISATION: Augmenté de 0.5 à 0.8 pour éviter répétitions
        repetition_penalty = 0.0
        if food.id in self.used_foods:
            repetition_penalty = 0.8  # Pénalité très forte pour éviter répétitions

        # Intégrer les préférences utilisateur si disponibles
        user_preference_modifier = 0.0
        if self.feedback_system and food.id:
            pref_score = self.feedback_system.get_food_preference_score(food.id)
            # Convertir le score de préférence (-1 à +1) en modificateur (0 à 0.5)
            # Score négatif = augmenter le score de variété (moins bon)
            # Score positif = diminuer le score de variété (meilleur)
            user_preference_modifier = -pref_score * 0.25  # Inverser et pondérer

        # Bonus de saisonnalité si disponible
        seasonal_modifier = 0.0
        if SEASONAL_AVAILABLE:
            seasonal_bonus = get_seasonal_bonus(food.name)
            # Convertir le bonus (0.8-1.3) en modificateur (-0.15 à +0.15)
            # Bonus > 1.0 (de saison) = score plus bas (meilleur)
            # Bonus < 1.0 (hors saison) = score plus haut (moins bon)
            seasonal_modifier = -(seasonal_bonus - 1.0) * 0.5

        # Normaliser sur une échelle de 0 à 9 (différence max possible)
        base_score = distance_score + repetition_penalty
        final_score = base_score + user_preference_modifier + seasonal_modifier
        return max(0.0, min(1.0, final_score))

    def _calculate_compatibility_score(
        self,
        food: Food,
        selected_foods: List[Tuple[Food, float]] = None
    ) -> float:
        """
        Calcule le score de compatibilité d'un aliment avec les aliments déjà sélectionnés.
        Plus le score est bas, mieux c'est.

        Args:
            food: L'aliment à évaluer
            selected_foods: Liste des aliments déjà sélectionnés dans le repas

        Returns:
            Score de compatibilité (0-1, plus bas = meilleur)
        """
        if not COMPATIBILITY_AVAILABLE or not selected_foods or len(selected_foods) == 0:
            return 0.5  # Score neutre si pas de compatibilité disponible

        # Calculer la compatibilité moyenne avec tous les aliments sélectionnés
        compatibility_scores = []

        for selected_food, _ in selected_foods:
            score = get_compatibility_score(
                food.name,
                selected_food.name,
                food.category,
                selected_food.category
            )
            compatibility_scores.append(score)

        if not compatibility_scores:
            return 0.5

        # Moyenne des compatibilités
        avg_compatibility = sum(compatibility_scores) / len(compatibility_scores)

        # Inverser le score (on veut un score bas = bon)
        return 1.0 - avg_compatibility


class PresetMealGenerator(MealGeneratorBase):
    """
    Générateur de repas basé sur des repas prédéfinis en base de données.

    Ce générateur sélectionne des repas complets pré-configurés qui ont été
    validés pour leur équilibre nutritionnel et leur palatabilité.
    """

    def __init__(self, db_manager, **kwargs):
        """
        Initialise le générateur de repas prédéfinis.

        Args:
            db_manager: Gestionnaire de base de données pour accéder aux repas prédéfinis
            **kwargs: Paramètres de base (disponibles via MealGeneratorBase)
        """
        super().__init__(**kwargs)
        self.db_manager = db_manager

    def generate_meal(
        self,
        meal_type: str,
        day_number: int,
        target_percentage: float,
        is_last_meal_of_day: bool = False,
        min_foods: int = 5,
        max_foods: int = 9
    ) -> Meal:
        """
        Génère un repas en sélectionnant un repas prédéfini de la base de données.

        Args:
            meal_type: Type de repas (breakfast, lunch, dinner, snack)
            day_number: Numéro du jour
            target_percentage: Pourcentage des calories quotidiennes
            is_last_meal_of_day: Si c'est le dernier repas de la journée
            min_foods: Nombre minimum d'aliments dans le repas (ignoré pour preset)
            max_foods: Nombre maximum d'aliments dans le repas (ignoré pour preset)

        Returns:
            Repas généré
        """
        # Calculer l'objectif nutritionnel pour ce repas
        meal_target = self.nutrition_target.scale_for_meal(target_percentage)
        adjusted_target = self._adjust_meal_target(
            meal_target,
            target_percentage,
            is_last_meal_of_day
        )

        logger.info(
            f"Génération repas prédéfini {meal_type} jour {day_number}: "
            f"cible {adjusted_target.calories:.0f} kcal"
        )

        # 1. Récupérer les repas prédéfinis du bon type depuis la base
        preset_meals = self.db_manager.get_preset_meals_by_type(meal_type)

        if not preset_meals:
            logger.warning(
                f"Aucun repas prédéfini de type '{meal_type}' trouvé en base. "
                f"Créer un repas vide."
            )
            # Fallback: créer un repas vide
            meal = Meal(
                name=self._generate_meal_name(meal_type, day_number),
                meal_type=meal_type,
                target_calories=adjusted_target.calories,
                day_number=day_number
            )
            return meal

        # 2. Scorer chaque repas prédéfini selon sa proximité avec la cible
        best_preset = None
        best_score = float('inf')
        best_scale_factor = 1.0

        for preset in preset_meals:
            # Calculer les macros du preset
            preset_macros = preset.calculate_macros()

            # Calculer un facteur d'échelle pour approcher la cible calorique
            if preset_macros["calories"] > 0:
                scale_factor = adjusted_target.calories / preset_macros["calories"]
            else:
                scale_factor = 1.0

            # Limiter le facteur d'échelle pour éviter des portions absurdes
            scale_factor = max(0.5, min(2.0, scale_factor))

            # Calculer les macros après scaling
            scaled_macros = {k: v * scale_factor for k, v in preset_macros.items()}

            # Calculer le score de distance aux objectifs
            score = 0.0
            weights = {"calories": 2.0, "proteins": 2.5, "carbs": 1.0, "fats": 1.2}

            for macro in ["calories", "proteins", "carbs", "fats"]:
                target_val = getattr(adjusted_target, macro)
                if target_val > 0:
                    deviation = abs(scaled_macros[macro] - target_val) / target_val
                    score += deviation * weights[macro]

            # Pénalité si le preset a déjà été utilisé récemment
            if preset.id in self.used_foods:
                score *= 1.5

            if score < best_score:
                best_score = score
                best_preset = preset
                best_scale_factor = scale_factor

        if not best_preset:
            logger.warning(f"Impossible de trouver un repas prédéfini adapté pour {meal_type}")
            meal = Meal(
                name=self._generate_meal_name(meal_type, day_number),
                meal_type=meal_type,
                target_calories=adjusted_target.calories,
                day_number=day_number
            )
            return meal

        # 3. Créer le repas à partir du preset sélectionné
        meal = Meal(
            name=f"{best_preset.name} - Jour {day_number}",
            meal_type=meal_type,
            target_calories=adjusted_target.calories,
            day_number=day_number
        )

        # 4. Ajouter les aliments avec quantités ajustées
        for food, original_quantity in best_preset.foods:
            adjusted_quantity = original_quantity * best_scale_factor
            meal.add_food(food, adjusted_quantity)
            self.used_foods.add(food.id)

        # Mettre à jour l'accumulation journalière
        meal_macros = meal.calculate_macros()
        self.daily_accumulated_calories += meal_macros["calories"]

        logger.info(
            f"Repas prédéfini sélectionné: {best_preset.name}, "
            f"facteur échelle: {best_scale_factor:.2f}, "
            f"{meal_macros['calories']:.0f}/{adjusted_target.calories:.0f} kcal"
        )

        return meal


class ComponentBasedGenerator(MealGeneratorBase):
    """
    Générateur de repas basé sur la combinaison de composants (entrée/plat/dessert).

    Ce générateur construit des repas structurés en sélectionnant séparément
    une entrée, un plat principal et un dessert, puis en les combinant.
    """

    def __init__(self, db_manager, **kwargs):
        """
        Initialise le générateur par composants.

        Args:
            db_manager: Gestionnaire de base de données pour accéder aux composantes
            **kwargs: Paramètres de base (disponibles via MealGeneratorBase)
        """
        super().__init__(**kwargs)
        self.db_manager = db_manager
        # Fallback: utiliser FoodBasedGenerator pour les repas simples
        self.food_generator = FoodBasedGenerator(**kwargs)

    def generate_meal(
        self,
        meal_type: str,
        day_number: int,
        target_percentage: float,
        is_last_meal_of_day: bool = False,
        min_foods: int = 5,
        max_foods: int = 9
    ) -> Meal:
        """
        Génère un repas en combinant des composants (entrée/plat/dessert).

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
        # Calculer l'objectif nutritionnel
        meal_target = self.nutrition_target.scale_for_meal(target_percentage)
        adjusted_target = self._adjust_meal_target(
            meal_target,
            target_percentage,
            is_last_meal_of_day
        )

        # 1. Déterminer la structure selon le type de repas
        # Lunch et dinner utilisent entrée/plat/dessert
        # Breakfast et snacks utilisent le mode "par aliments"
        if meal_type not in ["lunch", "dinner"]:
            logger.info(f"{meal_type} utilise le mode 'par aliments' (pas de structure E/P/D)")
            return self.food_generator.generate_meal(
                meal_type, day_number, target_percentage,
                is_last_meal_of_day, min_foods, max_foods
            )

        logger.info(f"Génération par composants pour {meal_type} jour {day_number}")

        # 2. Définir la répartition calorique entre composants
        # Entrée: 20%, Plat: 60%, Dessert: 20% (optionnel)
        component_distribution = {
            "entrée": 0.20,
            "plat": 0.60,
            "dessert": 0.20
        }

        # 3. Récupérer les composantes disponibles en base
        available_entrees = self.db_manager.get_components_by_type("entrée")
        available_plats = self.db_manager.get_components_by_type("plat")
        available_desserts = self.db_manager.get_components_by_type("dessert")

        # Fallback si pas assez de composantes en base
        if len(available_entrees) == 0 or len(available_plats) == 0:
            logger.warning(
                f"Pas assez de composantes en base (entrées:{len(available_entrees)}, "
                f"plats:{len(available_plats)}). Fallback sur mode 'par aliments'"
            )
            return self.food_generator.generate_meal(
                meal_type, day_number, target_percentage,
                is_last_meal_of_day, min_foods, max_foods
            )

        # 4. Sélectionner la meilleure combinaison entrée + plat (+ dessert optionnel)
        meal = Meal(
            name=self._generate_meal_name(meal_type, day_number),
            meal_type=meal_type,
            target_calories=adjusted_target.calories,
            day_number=day_number
        )

        # Sélectionner entrée
        entree_target_cal = adjusted_target.calories * component_distribution["entrée"]
        best_entree = self._select_best_component(available_entrees, entree_target_cal)

        if best_entree:
            scale_factor = entree_target_cal / best_entree.calculate_macros()["calories"]
            scale_factor = max(0.5, min(2.0, scale_factor))
            for food, qty in best_entree.foods:
                meal.add_food(food, qty * scale_factor)
                self.used_foods.add(food.id)

        # Sélectionner plat principal
        plat_target_cal = adjusted_target.calories * component_distribution["plat"]
        best_plat = self._select_best_component(available_plats, plat_target_cal)

        if best_plat:
            scale_factor = plat_target_cal / best_plat.calculate_macros()["calories"]
            scale_factor = max(0.5, min(2.0, scale_factor))
            for food, qty in best_plat.foods:
                meal.add_food(food, qty * scale_factor)
                self.used_foods.add(food.id)

        # Dessert optionnel si disponible
        if len(available_desserts) > 0:
            dessert_target_cal = adjusted_target.calories * component_distribution["dessert"]
            best_dessert = self._select_best_component(available_desserts, dessert_target_cal)

            if best_dessert:
                scale_factor = dessert_target_cal / best_dessert.calculate_macros()["calories"]
                scale_factor = max(0.5, min(2.0, scale_factor))
                for food, qty in best_dessert.foods:
                    meal.add_food(food, qty * scale_factor)
                    self.used_foods.add(food.id)

        # Mettre à jour l'accumulation journalière
        meal_macros = meal.calculate_macros()
        self.daily_accumulated_calories += meal_macros["calories"]

        logger.info(
            f"Repas par composants généré: {len(meal.foods)} aliments, "
            f"{meal_macros['calories']:.0f}/{adjusted_target.calories:.0f} kcal"
        )

        return meal

    def _select_best_component(self, components, target_calories):
        """
        Sélectionne la meilleure composante selon la cible calorique.

        Args:
            components: Liste de MealComponent disponibles
            target_calories: Calories cibles pour cette composante

        Returns:
            MealComponent sélectionné ou None
        """
        if not components:
            return None

        best_component = None
        best_score = float('inf')

        for comp in components:
            comp_macros = comp.calculate_macros()

            # Score basé sur la distance calorique
            if comp_macros["calories"] > 0:
                score = abs(comp_macros["calories"] - target_calories) / target_calories
            else:
                score = float('inf')

            # Pénalité si déjà utilisé récemment
            if comp.id and comp.id in self.used_foods:
                score *= 1.5

            if score < best_score:
                best_score = score
                best_component = comp

        return best_component


class CategoryBasedGenerator(MealGeneratorBase):
    """
    Générateur de repas basé sur des règles de catégories alimentaires.

    Ce générateur utilise des règles diététiques pour construire des repas
    équilibrés en sélectionnant un aliment de chaque catégorie nécessaire.
    """

    def __init__(self, rules_file=None, **kwargs):
        """
        Initialise le générateur par catégories.

        Args:
            rules_file: Chemin vers le fichier JSON des règles (optionnel)
            **kwargs: Paramètres de base (disponibles via MealGeneratorBase)
        """
        super().__init__(**kwargs)
        self.rules_file = rules_file
        self.rules = self._load_rules()

    def _load_rules(self):
        """Charge les règles de catégories depuis le fichier JSON."""
        import json
        from meal_planner.config import CATEGORY_RULES_PATH

        rules_path = self.rules_file or CATEGORY_RULES_PATH

        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            logger.info(f"Règles de catégories chargées depuis {rules_path}")
            return rules
        except FileNotFoundError:
            logger.warning(f"Fichier de règles introuvable: {rules_path}, utilisation de règles par défaut")
            # Règles par défaut
            return {
                "breakfast": {"required": ["céréales", "produits laitiers"], "optional": ["fruits"]},
                "lunch": {"required": ["protéines", "féculents", "légumes"], "optional": []},
                "dinner": {"required": ["protéines", "légumes"], "optional": ["féculents"]},
                "snack": {"required": ["fruits"], "optional": ["produits laitiers"]},
            }
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            return {}

    def generate_meal(
        self,
        meal_type: str,
        day_number: int,
        target_percentage: float,
        is_last_meal_of_day: bool = False,
        min_foods: int = 5,
        max_foods: int = 9
    ) -> Meal:
        """
        Génère un repas selon des règles de catégories alimentaires.

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
        # Calculer l'objectif nutritionnel
        meal_target = self.nutrition_target.scale_for_meal(target_percentage)
        adjusted_target = self._adjust_meal_target(
            meal_target,
            target_percentage,
            is_last_meal_of_day
        )

        logger.info(f"Génération par catégories pour {meal_type} jour {day_number}")

        # 1. Récupérer les règles pour ce type de repas
        meal_rules = self.rules.get(meal_type, {})
        required_categories = meal_rules.get("required", [])
        optional_categories = meal_rules.get("optional", [])

        if not required_categories:
            logger.warning(f"Aucune règle définie pour {meal_type}")
            required_categories = ["protéines", "légumes"]  # Fallback

        logger.info(
            f"Règles {meal_type}: requis={required_categories}, optionnel={optional_categories}"
        )

        # 2. Créer le repas
        meal = Meal(
            name=self._generate_meal_name(meal_type, day_number),
            meal_type=meal_type,
            target_calories=adjusted_target.calories,
            day_number=day_number
        )

        # 3. Mapper les catégories simples aux catégories de la base
        from meal_planner.config import CATEGORY_MAPPING

        # 4. Sélectionner un aliment pour chaque catégorie requise
        selected_foods_per_category = []
        categories_to_use = required_categories.copy()

        # Ajouter certaines catégories optionnelles si espace disponible
        if len(categories_to_use) < max_foods and optional_categories:
            categories_to_use.extend(optional_categories[:max_foods - len(categories_to_use)])

        for category in categories_to_use:
            # Mapper la catégorie simple vers les catégories DB
            db_categories = CATEGORY_MAPPING.get(category, [category])

            # Chercher des aliments dans cette catégorie
            category_foods = [
                f for f in self.available_foods
                if any(db_cat.lower() in f.category.lower() for db_cat in db_categories)
                and f.id not in self.used_foods
            ]

            if not category_foods:
                logger.warning(f"Aucun aliment disponible pour la catégorie '{category}'")
                continue

            # Sélectionner le meilleur aliment de cette catégorie
            best_food = self._select_best_food_from_category(category_foods)
            if best_food:
                selected_foods_per_category.append((best_food, category))

        if not selected_foods_per_category:
            logger.warning(f"Impossible de trouver des aliments pour les catégories requises")
            return meal

        # 5. Calculer les quantités pour atteindre la cible calorique
        # Répartir équitablement les calories entre les aliments sélectionnés
        target_cal_per_food = adjusted_target.calories / len(selected_foods_per_category)

        for food, category in selected_foods_per_category:
            # Calculer la quantité pour atteindre la cible par aliment
            if food.calories > 0:
                quantity = (target_cal_per_food / food.calories) * 100
            else:
                quantity = 100

            # Limiter les quantités extrêmes
            quantity = max(10, min(300, quantity))

            meal.add_food(food, quantity)
            self.used_foods.add(food.id)

        # Mettre à jour l'accumulation journalière
        meal_macros = meal.calculate_macros()
        self.daily_accumulated_calories += meal_macros["calories"]

        logger.info(
            f"Repas par catégories généré: {len(meal.foods)} aliments, "
            f"{meal_macros['calories']:.0f}/{adjusted_target.calories:.0f} kcal"
        )

        return meal

    def _select_best_food_from_category(self, category_foods):
        """
        Sélectionne le meilleur aliment d'une catégorie.

        Args:
            category_foods: Liste d'aliments de la catégorie

        Returns:
            Food sélectionné
        """
        if not category_foods:
            return None

        # Sélectionner selon le variety_level et health_index
        best_food = None
        best_score = float('inf')

        for food in category_foods:
            # Score basé sur la distance au variety_level souhaité
            variety_distance = abs(food.variety_index - self.variety_level)
            health_distance = abs(food.health_index - self.health_index)

            score = variety_distance + health_distance

            # Bonus pour les aliments de saison si disponible
            if SEASONAL_AVAILABLE:
                seasonal_bonus = get_seasonal_bonus(food.name)
                score *= seasonal_bonus  # Réduit le score si de saison

            if score < best_score:
                best_score = score
                best_food = food

        return best_food
