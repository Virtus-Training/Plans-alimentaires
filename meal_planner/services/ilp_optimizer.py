"""
Optimiseur ILP (Integer Linear Programming) pour la sélection optimale d'aliments.
Utilise PuLP pour résoudre le problème d'optimisation multi-contraintes.
"""

from typing import List, Dict, Tuple, Optional
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, PULP_CBC_CMD

from meal_planner.models.food import Food
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


class ILPMealOptimizer:
    """
    Optimiseur basé sur la programmation linéaire entière (ILP).

    Résout le problème d'optimisation:
    - Minimiser l'écart aux objectifs nutritionnels
    - Sous contraintes: calories, protéines, glucides, lipides
    - Variables: quantités d'aliments (continues entre min et max)
    """

    def __init__(
        self,
        min_quantity: float = 10.0,
        max_quantity: float = 500.0,
        tolerance: float = 0.10,
        force_practical_portions: bool = True
    ):
        """
        Initialise l'optimiseur.

        Args:
            min_quantity: Quantité minimale d'un aliment (grammes)
            max_quantity: Quantité maximale d'un aliment (grammes)
            tolerance: Tolérance acceptable pour les contraintes
            force_practical_portions: Si True, arrondit les quantités aux portions pratiques
        """
        self.min_quantity = min_quantity
        self.max_quantity = max_quantity
        self.tolerance = tolerance
        self.force_practical_portions = force_practical_portions

    def optimize_meal(
        self,
        available_foods: List[Food],
        target: NutritionTarget,
        min_foods: int = 3,
        max_foods: int = 7,
        compatibility_scores: Optional[Dict[int, float]] = None
    ) -> List[Tuple[Food, float]]:
        """
        Optimise la sélection d'aliments pour un repas en utilisant ILP.

        Args:
            available_foods: Liste des aliments disponibles
            target: Objectif nutritionnel à atteindre
            min_foods: Nombre minimum d'aliments dans le repas
            max_foods: Nombre maximum d'aliments dans le repas
            compatibility_scores: Scores de compatibilité par food_id (optionnel)

        Returns:
            Liste de tuples (Food, quantité_en_grammes)
        """
        if len(available_foods) < min_foods:
            logger.warning(
                f"Pas assez d'aliments disponibles ({len(available_foods)} < {min_foods})"
            )
            return []

        # Créer le problème d'optimisation
        prob = LpProblem("MealOptimization", LpMinimize)

        # Variables de décision
        food_vars = {}  # Quantité de chaque aliment
        food_binary = {}  # 1 si l'aliment est utilisé, 0 sinon

        for i, food in enumerate(available_foods):
            food_vars[i] = LpVariable(
                f"qty_{i}",
                lowBound=0,
                upBound=self.max_quantity,
                cat='Continuous'
            )
            food_binary[i] = LpVariable(f"used_{i}", cat='Binary')

        # Variables d'écart (pour la fonction objectif)
        cal_dev_plus = LpVariable("cal_dev_plus", lowBound=0)
        cal_dev_minus = LpVariable("cal_dev_minus", lowBound=0)
        prot_dev_plus = LpVariable("prot_dev_plus", lowBound=0)
        prot_dev_minus = LpVariable("prot_dev_minus", lowBound=0)
        carbs_dev_plus = LpVariable("carbs_dev_plus", lowBound=0)
        carbs_dev_minus = LpVariable("carbs_dev_minus", lowBound=0)
        fats_dev_plus = LpVariable("fats_dev_plus", lowBound=0)
        fats_dev_minus = LpVariable("fats_dev_minus", lowBound=0)

        # Fonction objectif: minimiser les écarts pondérés
        weights = {
            'calories': 2.0,
            'proteins': 2.5,
            'carbs': 1.0,
            'fats': 1.2
        }

        objective = (
            weights['calories'] * (cal_dev_plus + cal_dev_minus) +
            weights['proteins'] * (prot_dev_plus + prot_dev_minus) +
            weights['carbs'] * (carbs_dev_plus + carbs_dev_minus) +
            weights['fats'] * (fats_dev_plus + fats_dev_minus)
        )

        # Bonus pour la compatibilité si disponible
        if compatibility_scores:
            compatibility_bonus = lpSum([
                -compatibility_scores.get(food.id, 0.5) * food_vars[i] * 0.01
                for i, food in enumerate(available_foods)
            ])
            objective += compatibility_bonus

        prob += objective

        # Contraintes nutritionnelles avec variables d'écart
        total_cal = lpSum([
            food_vars[i] * available_foods[i].calories / 100
            for i in range(len(available_foods))
        ])
        prob += total_cal - cal_dev_plus + cal_dev_minus == target.calories

        total_prot = lpSum([
            food_vars[i] * available_foods[i].proteins / 100
            for i in range(len(available_foods))
        ])
        prob += total_prot - prot_dev_plus + prot_dev_minus == target.proteins

        total_carbs = lpSum([
            food_vars[i] * available_foods[i].carbs / 100
            for i in range(len(available_foods))
        ])
        prob += total_carbs - carbs_dev_plus + carbs_dev_minus == target.carbs

        total_fats = lpSum([
            food_vars[i] * available_foods[i].fats / 100
            for i in range(len(available_foods))
        ])
        prob += total_fats - fats_dev_plus + fats_dev_minus == target.fats

        # Contraintes sur le nombre d'aliments
        prob += lpSum([food_binary[i] for i in range(len(available_foods))]) >= min_foods
        prob += lpSum([food_binary[i] for i in range(len(available_foods))]) <= max_foods

        # Lien entre quantité et utilisation
        for i in range(len(available_foods)):
            # Si utilisé (binary=1), quantité >= min_quantity
            prob += food_vars[i] >= self.min_quantity * food_binary[i]
            # Si utilisé, quantité <= max_quantity
            prob += food_vars[i] <= self.max_quantity * food_binary[i]

        # Contraintes sur les déviations (tolérance)
        prob += cal_dev_plus <= target.calories * self.tolerance
        prob += cal_dev_minus <= target.calories * self.tolerance
        prob += prot_dev_plus <= target.proteins * self.tolerance
        prob += prot_dev_minus <= target.proteins * self.tolerance

        # Résoudre le problème (en mode silencieux)
        prob.solve(PULP_CBC_CMD(msg=0))

        # Vérifier si une solution a été trouvée
        status = LpStatus[prob.status]
        if status != 'Optimal':
            logger.warning(f"ILP n'a pas trouvé de solution optimale: {status}")
            return []

        # Extraire la solution
        result = []
        total_macros = {'calories': 0, 'proteins': 0, 'carbs': 0, 'fats': 0}

        for i, food in enumerate(available_foods):
            qty = food_vars[i].varValue
            if qty and qty >= self.min_quantity:
                # NOUVEAU: Arrondir aux portions pratiques si activé
                if self.force_practical_portions:
                    qty = self._round_to_practical_portion(qty, food)

                result.append((food, qty))

                # Calculer les macros pour logging
                food_macros = food.calculate_for_quantity(qty)
                for key in total_macros:
                    total_macros[key] += food_macros[key]

        logger.info(
            f"ILP Solution optimale trouvée: {len(result)} aliments, "
            f"Calories: {total_macros['calories']:.0f}/{target.calories:.0f}, "
            f"Protéines: {total_macros['proteins']:.1f}/{target.proteins:.1f}g"
            + (", Portions pratiques: ON" if self.force_practical_portions else "")
        )

        return result

    def _round_to_practical_portion(self, quantity: float, food: Food) -> float:
        """
        Arrondit une quantité à une portion pratique et réaliste.
        Identique à la fonction dans meal_generator.py pour cohérence.

        Args:
            quantity: Quantité brute en grammes
            food: L'aliment concerné

        Returns:
            Quantité arrondie en grammes
        """
        # Arrondir toujours au minimum à 10g
        if quantity < 10:
            return 10

        # Portions très petites (huiles, épices, etc.) : arrondir à 5g
        if quantity < 20:
            return round(quantity / 5) * 5

        # Portions petites (beurre, fromage) : arrondir à 10g
        elif quantity < 50:
            return round(quantity / 10) * 10

        # Portions moyennes : arrondir à 20g pour plus de praticité
        elif quantity < 100:
            return round(quantity / 20) * 20

        # Portions grandes : arrondir à 25g
        elif quantity < 200:
            return round(quantity / 25) * 25

        # Très grandes portions : arrondir à 50g
        else:
            return round(quantity / 50) * 50

    def optimize_with_fallback(
        self,
        available_foods: List[Food],
        target: NutritionTarget,
        min_foods: int = 3,
        max_foods: int = 7,
        compatibility_scores: Optional[Dict[int, float]] = None
    ) -> Tuple[List[Tuple[Food, float]], bool]:
        """
        Optimise avec fallback sur une solution moins contrainte si échec.

        Args:
            available_foods: Liste des aliments disponibles
            target: Objectif nutritionnel
            min_foods: Nombre minimum d'aliments
            max_foods: Nombre maximum d'aliments
            compatibility_scores: Scores de compatibilité (optionnel)

        Returns:
            Tuple (solution, is_optimal) où is_optimal indique si c'est la solution ILP
        """
        # Essayer l'optimisation ILP complète
        result = self.optimize_meal(
            available_foods,
            target,
            min_foods,
            max_foods,
            compatibility_scores
        )

        if result:
            return result, True

        # Fallback: essayer avec tolérance plus large
        logger.info("ILP strict échoué, essai avec tolérance large...")
        old_tolerance = self.tolerance
        self.tolerance = 0.20  # Tolérance plus large

        result = self.optimize_meal(
            available_foods,
            target,
            min_foods,
            max_foods,
            compatibility_scores
        )

        self.tolerance = old_tolerance

        if result:
            logger.info("Solution trouvée avec tolérance large")
            return result, False

        # Fallback final: réduire le nombre d'aliments requis
        logger.warning("ILP échoué même avec tolérance large, réduction min_foods")
        result = self.optimize_meal(
            available_foods,
            target,
            max(2, min_foods - 1),
            max_foods,
            compatibility_scores
        )

        return result if result else [], False


def create_ilp_optimizer(
    min_quantity: float = 10.0,
    max_quantity: float = 500.0,
    tolerance: float = 0.10
) -> ILPMealOptimizer:
    """
    Factory function pour créer un optimiseur ILP.

    Args:
        min_quantity: Quantité minimale d'un aliment (grammes)
        max_quantity: Quantité maximale d'un aliment (grammes)
        tolerance: Tolérance acceptable pour les contraintes

    Returns:
        Instance de ILPMealOptimizer
    """
    return ILPMealOptimizer(min_quantity, max_quantity, tolerance)
