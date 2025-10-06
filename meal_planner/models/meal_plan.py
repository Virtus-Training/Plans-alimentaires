"""
Modèle MealPlan - Représente un plan alimentaire complet
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from collections import defaultdict

from meal_planner.models.meal import Meal
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.config import MACRO_TOLERANCE


@dataclass
class MealPlan:
    """
    Représente un plan alimentaire complet sur plusieurs jours.

    Attributes:
        duration_days: Nombre de jours du plan
        nutrition_target: Objectif nutritionnel quotidien
        meals: Liste des repas du plan
        notes: Notes ou commentaires sur le plan
        id: Identifiant unique en base de données
    """

    duration_days: int
    nutrition_target: NutritionTarget
    meals: List[Meal] = field(default_factory=list)
    notes: str = ""
    id: Optional[int] = None

    def validate(self) -> Dict:
        """
        Valide le plan alimentaire complet.

        Returns:
            Dict contenant les résultats de validation pour chaque jour
        """
        results = {}

        for day in range(1, self.duration_days + 1):
            day_result = self.validate_day(day)
            results[f"day_{day}"] = day_result

        return results

    def validate_day(self, day: int) -> Dict:
        """
        Valide un jour spécifique du plan, incluant l'équilibre glycémique.

        Args:
            day: Numéro du jour à valider

        Returns:
            Dict contenant les résultats de validation
        """
        daily_totals = self.calculate_daily_totals(day)
        target = self.nutrition_target

        result = {
            "is_valid": True,
            "totals": daily_totals,
            "target": target.to_dict(),
            "deviations": {},
            "messages": [],
            "glycemic_balance": self._calculate_glycemic_balance(day)
        }

        # Calculer les écarts
        macros = ["calories", "proteins", "carbs", "fats"]
        for macro in macros:
            actual = daily_totals.get(macro, 0)
            expected = getattr(target, macro)

            if expected > 0:
                deviation = abs(actual - expected) / expected
                result["deviations"][macro] = deviation

                if deviation > MACRO_TOLERANCE:
                    result["is_valid"] = False
                    result["messages"].append(
                        f"{macro.capitalize()}: {actual:.1f} (cible: {expected:.1f}, "
                        f"écart: {deviation * 100:.1f}%)"
                    )

        # Ajouter un avertissement si l'équilibre glycémique est mauvais
        if result["glycemic_balance"]["score"] < 60:
            result["messages"].append(
                f"⚠️ Équilibre glycémique insuffisant ({result['glycemic_balance']['score']}/100)"
            )

        return result

    def _calculate_glycemic_balance(self, day: int) -> Dict:
        """
        Évalue l'équilibre glycémique d'une journée.
        Un bon équilibre signifie une distribution appropriée des glucides sur la journée.

        Args:
            day: Numéro du jour

        Returns:
            Dict avec le score d'équilibre et des détails
        """
        day_meals = self.get_meals_for_day(day)

        if not day_meals:
            return {"score": 0, "status": "Aucun repas", "details": {}}

        # Calculer la distribution des glucides par repas
        total_carbs = 0
        meal_carbs = []

        for meal in day_meals:
            macros = meal.calculate_macros()
            carbs = macros.get("carbs", 0)
            total_carbs += carbs
            meal_carbs.append({
                "meal": meal.name,
                "carbs": carbs,
                "meal_type": meal.meal_type
            })

        if total_carbs == 0:
            return {"score": 0, "status": "Pas de glucides", "details": {}}

        # Vérifier la distribution (éviter les pics glycémiques)
        # Un bon plan distribue les glucides régulièrement
        carb_percentages = [m["carbs"] / total_carbs for m in meal_carbs]

        # Calculer l'écart-type de la distribution
        import statistics
        if len(carb_percentages) > 1:
            std_dev = statistics.stdev(carb_percentages)
            # Un écart-type faible = bonne distribution
            # Écart-type > 0.2 = mauvaise distribution
            if std_dev < 0.15:
                distribution_score = 100
            elif std_dev < 0.25:
                distribution_score = 80
            elif std_dev < 0.35:
                distribution_score = 60
            else:
                distribution_score = 40
        else:
            distribution_score = 50  # Score neutre si un seul repas

        # Vérifier qu'il y a des fibres (ralentissent l'absorption)
        daily_totals = self.calculate_daily_totals(day)
        fiber_ratio = daily_totals.get("fibers", 0) / total_carbs if total_carbs > 0 else 0

        # Objectif: au moins 0.10 (10g de fibres pour 100g de glucides)
        if fiber_ratio >= 0.12:
            fiber_score = 100
        elif fiber_ratio >= 0.08:
            fiber_score = 80
        elif fiber_ratio >= 0.05:
            fiber_score = 60
        else:
            fiber_score = 40

        # Score global (70% distribution, 30% fibres)
        total_score = distribution_score * 0.70 + fiber_score * 0.30

        # Statut
        if total_score >= 80:
            status = "Excellent"
        elif total_score >= 70:
            status = "Bon"
        elif total_score >= 60:
            status = "Acceptable"
        else:
            status = "À améliorer"

        return {
            "score": round(total_score, 1),
            "status": status,
            "details": {
                "total_carbs": round(total_carbs, 1),
                "total_fibers": round(daily_totals.get("fibers", 0), 1),
                "fiber_ratio": round(fiber_ratio, 2),
                "distribution_score": round(distribution_score, 1),
                "fiber_score": round(fiber_score, 1),
                "meal_distribution": [
                    {
                        "meal": m["meal"],
                        "carbs": round(m["carbs"], 1),
                        "percentage": round((m["carbs"] / total_carbs) * 100, 1)
                    }
                    for m in meal_carbs
                ]
            }
        }

    def validate_against_target(self, tolerance: float = MACRO_TOLERANCE) -> Dict:
        """
        Valide l'ensemble du plan par rapport aux objectifs.

        Args:
            tolerance: Tolérance acceptable (par défaut: MACRO_TOLERANCE)

        Returns:
            Dict contenant les résultats de validation globaux
        """
        all_valid = True
        days_results = {}

        for day in range(1, self.duration_days + 1):
            day_result = self.validate_day(day)
            days_results[f"day_{day}"] = day_result

            if not day_result["is_valid"]:
                all_valid = False

        return {
            "is_valid": all_valid,
            "days": days_results,
            "total_meals": len(self.meals),
            "duration_days": self.duration_days
        }

    def calculate_daily_totals(self, day: int) -> Dict[str, float]:
        """
        Calcule les totaux nutritionnels pour un jour donné.

        Args:
            day: Numéro du jour

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

        day_meals = self.get_meals_for_day(day)

        for meal in day_meals:
            meal_macros = meal.calculate_macros()
            for key in totals.keys():
                totals[key] += meal_macros.get(key, 0.0)

        return totals

    def get_meals_for_day(self, day: int) -> List[Meal]:
        """
        Retourne tous les repas pour un jour donné.

        Args:
            day: Numéro du jour

        Returns:
            Liste des repas du jour
        """
        return [meal for meal in self.meals if meal.day_number == day]

    def add_meal(self, meal: Meal) -> None:
        """
        Ajoute un repas au plan.

        Args:
            meal: Le repas à ajouter
        """
        if meal.day_number > self.duration_days:
            raise ValueError(
                f"Le jour du repas ({meal.day_number}) dépasse la durée du plan ({self.duration_days})"
            )

        self.meals.append(meal)

    def remove_meal(self, meal: Meal) -> bool:
        """
        Retire un repas du plan.

        Args:
            meal: Le repas à retirer

        Returns:
            True si le repas a été retiré, False sinon
        """
        original_length = len(self.meals)
        self.meals = [m for m in self.meals if m.id != meal.id]
        return len(self.meals) < original_length

    def get_meals_by_type(self) -> Dict[str, List[Meal]]:
        """
        Regroupe les repas par type.

        Returns:
            Dict avec les types de repas comme clés et listes de repas comme valeurs
        """
        meals_by_type = defaultdict(list)

        for meal in self.meals:
            meals_by_type[meal.meal_type].append(meal)

        return dict(meals_by_type)

    def get_summary(self) -> str:
        """
        Retourne un résumé textuel du plan.

        Returns:
            Chaîne décrivant le plan
        """
        summary_lines = [
            f"Plan alimentaire - {self.duration_days} jour(s)",
            f"Objectif: {self.nutrition_target}",
            f"Nombre de repas: {len(self.meals)}",
            ""
        ]

        for day in range(1, self.duration_days + 1):
            day_meals = self.get_meals_for_day(day)
            day_totals = self.calculate_daily_totals(day)

            summary_lines.append(f"Jour {day}:")
            summary_lines.append(f"  {len(day_meals)} repas")
            summary_lines.append(
                f"  Total: {day_totals['calories']:.0f} kcal - "
                f"P: {day_totals['proteins']:.1f}g, "
                f"C: {day_totals['carbs']:.1f}g, "
                f"F: {day_totals['fats']:.1f}g"
            )

            for meal in day_meals:
                summary_lines.append(f"    - {meal}")

            summary_lines.append("")

        return "\n".join(summary_lines)

    def calculate_quality_score(self) -> Dict:
        """
        Calcule un score de qualité global du plan alimentaire.
        Basé sur les meilleures pratiques de l'industrie (MyFitnessPal, Yazio).

        Returns:
            Dict contenant les scores et métriques de qualité
        """
        # Score nutritionnel (40% du score total)
        nutrition_score = self._calculate_nutrition_score()

        # Score de diversité (30% du score total)
        diversity_score = self._calculate_diversity_score()

        # Score de palatabilité (20% du score total)
        palatability_score = self._calculate_palatability_score()

        # Score de praticité (10% du score total)
        practicality_score = self._calculate_practicality_score()

        # Score global pondéré
        total_score = (
            nutrition_score * 0.40 +
            diversity_score * 0.30 +
            palatability_score * 0.20 +
            practicality_score * 0.10
        )

        return {
            "total_score": round(total_score, 2),
            "nutrition_score": round(nutrition_score, 2),
            "diversity_score": round(diversity_score, 2),
            "palatability_score": round(palatability_score, 2),
            "practicality_score": round(practicality_score, 2),
            "grade": self._get_grade(total_score),
            "recommendations": self._generate_recommendations(
                nutrition_score, diversity_score, palatability_score, practicality_score
            )
        }

    def _calculate_nutrition_score(self) -> float:
        """Score basé sur la précision nutritionnelle (0-100)"""
        total_deviation = 0.0
        day_count = 0

        for day in range(1, self.duration_days + 1):
            day_result = self.validate_day(day)
            # Moyenne des déviations pour ce jour
            if day_result["deviations"]:
                avg_deviation = sum(day_result["deviations"].values()) / len(day_result["deviations"])
                total_deviation += avg_deviation
                day_count += 1

        if day_count == 0:
            return 100.0

        avg_total_deviation = total_deviation / day_count

        # Convertir la déviation en score (moins de déviation = meilleur score)
        # Tolérance de 10% = score parfait
        if avg_total_deviation <= 0.10:
            return 100.0
        elif avg_total_deviation <= 0.15:
            return 90.0
        elif avg_total_deviation <= 0.20:
            return 75.0
        else:
            return max(0, 50 - (avg_total_deviation - 0.20) * 100)

    def _calculate_diversity_score(self) -> float:
        """Score basé sur la diversité alimentaire (0-100)"""
        all_foods = []
        all_categories = []

        for meal in self.meals:
            for food, qty in meal.foods:
                all_foods.append(food.name)
                all_categories.append(food.category)

        unique_foods = len(set(all_foods))
        unique_categories = len(set(all_categories))
        total_foods = len(all_foods)

        # Ratio de diversité
        diversity_ratio = unique_foods / total_foods if total_foods > 0 else 0

        # Objectifs: 20+ aliments uniques/jour, 8+ catégories
        foods_per_day = unique_foods / self.duration_days if self.duration_days > 0 else 0

        # Score basé sur la diversité
        food_score = min(100, (foods_per_day / 20) * 100)
        category_score = min(100, (unique_categories / 8) * 100)
        ratio_score = diversity_ratio * 100

        return (food_score * 0.5 + category_score * 0.3 + ratio_score * 0.2)

    def _calculate_palatability_score(self) -> float:
        """Score basé sur la compatibilité et palatabilité des repas (0-100)"""
        try:
            from meal_planner.data.food_compatibility import calculate_meal_palatability

            total_palatability = 0.0
            meal_count = 0

            for meal in self.meals:
                if len(meal.foods) > 1:
                    foods = [food.name for food, qty in meal.foods]
                    categories = [food.category for food, qty in meal.foods]
                    palatability = calculate_meal_palatability(foods, categories)
                    total_palatability += palatability
                    meal_count += 1

            if meal_count == 0:
                return 75.0  # Score neutre si pas de données

            avg_palatability = total_palatability / meal_count
            return avg_palatability * 100

        except ImportError:
            return 75.0  # Score neutre si module non disponible

    def _calculate_practicality_score(self) -> float:
        """Score basé sur la praticité du plan (portions, quantités) (0-100)"""
        practical_portions = 0
        total_portions = 0

        for meal in self.meals:
            for food, quantity in meal.foods:
                total_portions += 1

                # Vérifier si la quantité est "pratique" (multiple de 5, 10, 20, 25, 50)
                if (quantity % 50 == 0 or quantity % 25 == 0 or quantity % 20 == 0 or
                    quantity % 10 == 0 or quantity % 5 == 0):
                    practical_portions += 1

        if total_portions == 0:
            return 100.0

        practicality_ratio = practical_portions / total_portions
        return practicality_ratio * 100

    def _get_grade(self, score: float) -> str:
        """Convertit un score en note alphabétique"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        else:
            return "D"

    def _generate_recommendations(
        self,
        nutrition_score: float,
        diversity_score: float,
        palatability_score: float,
        practicality_score: float
    ) -> List[str]:
        """Génère des recommandations pour améliorer le plan"""
        recommendations = []

        if nutrition_score < 80:
            recommendations.append(
                "Ajuster les portions pour mieux respecter les objectifs nutritionnels"
            )

        if diversity_score < 70:
            recommendations.append(
                "Augmenter la variété d'aliments et de catégories alimentaires"
            )

        if palatability_score < 70:
            recommendations.append(
                "Améliorer les combinaisons d'aliments pour une meilleure compatibilité gustative"
            )

        if practicality_score < 75:
            recommendations.append(
                "Arrondir les quantités pour faciliter la préparation"
            )

        if not recommendations:
            recommendations.append("Excellent plan alimentaire, aucune amélioration majeure nécessaire!")

        return recommendations

    def to_dict(self) -> Dict:
        """
        Convertit le plan en dictionnaire.

        Returns:
            Dict représentant le plan
        """
        return {
            "id": self.id,
            "duration_days": self.duration_days,
            "nutrition_target": self.nutrition_target.to_dict(),
            "meals": [meal.to_dict() for meal in self.meals],
            "notes": self.notes,
            "validation": self.validate_against_target(),
            "quality_score": self.calculate_quality_score()
        }

    def save_to_json(self, filepath: str) -> bool:
        """
        Sauvegarde le plan alimentaire au format JSON.

        Args:
            filepath: Chemin du fichier de sauvegarde

        Returns:
            True si sauvegarde réussie, False sinon
        """
        import json
        from datetime import datetime

        try:
            data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "plan": self.to_dict()
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False

    def __str__(self) -> str:
        """Représentation textuelle du plan."""
        return (
            f"Plan alimentaire {self.duration_days} jour(s) - "
            f"{len(self.meals)} repas - "
            f"Objectif: {self.nutrition_target.calories:.0f} kcal/jour"
        )

    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (
            f"MealPlan(id={self.id}, duration={self.duration_days}, "
            f"meals_count={len(self.meals)})"
        )
