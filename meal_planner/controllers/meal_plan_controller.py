"""
MealPlanController - Contrôleur pour la gestion des plans alimentaires
"""

from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal

from meal_planner.models.meal_plan import MealPlan
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.models.database import DatabaseManager
from meal_planner.services.meal_generators import (
    MealDistribution,
    FoodBasedGenerator, PresetMealGenerator,
    ComponentBasedGenerator, CategoryBasedGenerator
)
from meal_planner.utils.logger import get_logger
from meal_planner.utils.diet_filters import apply_diet_filter

logger = get_logger(__name__)


class MealPlanController(QObject):
    """
    Contrôleur pour la coordination entre la vue et les modèles.

    Signals:
        plan_generated: Émis quand un plan est généré
        error_occurred: Émis en cas d'erreur
        status_updated: Émis pour mettre à jour le statut
    """

    plan_generated = pyqtSignal(MealPlan)
    error_occurred = pyqtSignal(str)
    status_updated = pyqtSignal(str)

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialise le contrôleur.

        Args:
            db_manager: Gestionnaire de base de données
        """
        super().__init__()
        self.db_manager = db_manager
        self.current_plan: Optional[MealPlan] = None

    def _create_generator(
        self,
        mode: str,
        available_foods,
        nutrition_target,
        distribution,
        price_level,
        health_index,
        variety_level,
        feedback_system
    ):
        """
        Factory method pour créer le générateur approprié selon le mode.

        Args:
            mode: Mode de génération ("food", "preset", "components", "categories")
            available_foods: Liste des aliments disponibles
            nutrition_target: Objectif nutritionnel
            distribution: Répartition calorique
            price_level: Niveau de prix
            health_index: Indice de santé
            variety_level: Niveau de variété
            feedback_system: Système de feedback utilisateur

        Returns:
            Instance du générateur approprié
        """
        common_params = {
            "available_foods": available_foods,
            "nutrition_target": nutrition_target,
            "distribution": distribution,
            "price_level": price_level,
            "health_index": health_index,
            "variety_level": variety_level,
            "feedback_system": feedback_system
        }

        if mode == "food":
            logger.info("Utilisation du mode 'Par Aliments' (FoodBasedGenerator)")
            return FoodBasedGenerator(**common_params)

        elif mode == "preset":
            logger.info("Utilisation du mode 'Repas Complets' (PresetMealGenerator)")
            # Passer aussi le db_manager pour accéder aux repas prédéfinis
            return PresetMealGenerator(**common_params, db_manager=self.db_manager)

        elif mode == "components":
            logger.info("Utilisation du mode 'Entrée/Plat/Dessert' (ComponentBasedGenerator)")
            return ComponentBasedGenerator(**common_params, db_manager=self.db_manager)

        elif mode == "categories":
            logger.info("Utilisation du mode 'Par Catégories' (CategoryBasedGenerator)")
            return CategoryBasedGenerator(**common_params)

        else:
            logger.warning(f"Mode inconnu '{mode}', fallback sur 'Par Aliments'")
            return FoodBasedGenerator(**common_params)

    def generate_meal_plan(self, settings: Dict) -> None:
        """
        Génère un plan alimentaire basé sur les paramètres.

        Args:
            settings: Paramètres du plan (nutrition_target, meal_count, etc.)
        """
        try:
            self.status_updated.emit("Génération du plan alimentaire...")
            logger.info(f"Génération d'un plan avec les paramètres: {settings}")

            # Extraire les paramètres
            nutrition_target = settings.get("nutrition_target")
            duration_days = settings.get("duration_days", 1)
            meal_count = settings.get("meal_count", 3)
            dietary_preferences = settings.get("dietary_preferences", [])

            # Valider les paramètres
            if not isinstance(nutrition_target, NutritionTarget):
                raise ValueError("Objectif nutritionnel invalide")

            is_valid, msg = nutrition_target.validate()
            if not is_valid:
                raise ValueError(f"Objectif nutritionnel invalide: {msg}")

            # Récupérer les aliments disponibles selon les préférences
            self.status_updated.emit("Chargement des aliments...")

            # Séparer les régimes spécifiques des autres préférences
            special_diets = ['keto', 'paleo', 'mediterranean']
            diet_type = None
            other_preferences = []

            for pref in dietary_preferences:
                if pref in special_diets:
                    diet_type = pref
                else:
                    other_preferences.append(pref)

            # Charger les aliments avec les préférences non-régimes (vegetarian, vegan, etc.)
            if other_preferences:
                available_foods = self.db_manager.get_foods_with_tags(other_preferences)
                logger.info(f"{len(available_foods)} aliments trouvés avec les préférences: {other_preferences}")
            else:
                available_foods = self.db_manager.get_all_foods()
                logger.info(f"{len(available_foods)} aliments disponibles au total")

            # Appliquer les filtres de régimes spécifiques (Keto, Paléo, Méditerranéen)
            if diet_type:
                self.status_updated.emit(f"Application du régime {diet_type}...")
                available_foods, nutrition_target = apply_diet_filter(
                    available_foods,
                    diet_type,
                    nutrition_target
                )
                logger.info(
                    f"Régime {diet_type} appliqué: {len(available_foods)} aliments compatibles"
                )

            if len(available_foods) < 5:
                raise ValueError(
                    f"Pas assez d'aliments disponibles ({len(available_foods)}). "
                    "Minimum requis: 5 aliments."
                )

            # Créer le plan
            meal_plan = MealPlan(
                duration_days=duration_days,
                nutrition_target=nutrition_target,
                meals=[],
                notes=f"Plan généré avec {meal_count} repas/jour. "
                      f"Préférences: {', '.join(dietary_preferences) if dietary_preferences else 'Aucune'}"
            )

            # Définir la répartition calorique selon le nombre de repas
            distribution = self._create_meal_distribution(meal_count)

            # Extraire les critères de sélection
            price_level = settings.get("price_level", 5)
            health_index = settings.get("health_index", 5)
            variety_level = settings.get("variety_level", 5)
            feedback_system = settings.get("feedback_system", None)
            generation_mode = settings.get("generation_mode", "food")

            # Factory Pattern: Créer le générateur approprié selon le mode
            generator = self._create_generator(
                mode=generation_mode,
                available_foods=available_foods,
                nutrition_target=nutrition_target,
                distribution=distribution,
                price_level=price_level,
                health_index=health_index,
                variety_level=variety_level,
                feedback_system=feedback_system
            )

            # Générer les repas pour chaque jour
            meal_types = self._get_meal_types(meal_count)

            for day in range(1, duration_days + 1):
                self.status_updated.emit(f"Génération jour {day}/{duration_days}...")

                # Réinitialiser l'accumulation journalière au début de chaque jour
                generator.daily_accumulated_calories = 0.0

                # Réinitialiser l'historique des aliments tous les 2 jours pour la variété
                if day > 1 and day % 2 == 1:
                    generator.reset_used_foods()

                for i, (meal_type, percentage) in enumerate(meal_types):
                    # Déterminer si c'est le dernier repas de la journée
                    is_last_meal = (i == len(meal_types) - 1)

                    # Définir le nombre d'aliments selon le type de repas pour la variabilité
                    import random
                    if meal_type in ["breakfast", "snack", "afternoon_snack", "morning_snack", "evening_snack"]:
                        # Repas légers: 3-6 aliments
                        min_foods = random.randint(3, 4)
                        max_foods = random.randint(5, 6)
                    else:  # lunch, dinner
                        # Repas principaux: 4-8 aliments
                        min_foods = random.randint(4, 5)
                        max_foods = random.randint(6, 8)

                    meal = generator.generate_meal(
                        meal_type=meal_type,
                        day_number=day,
                        target_percentage=percentage,
                        is_last_meal_of_day=is_last_meal,
                        min_foods=min_foods,
                        max_foods=max_foods
                    )
                    meal_plan.add_meal(meal)

                    logger.info(
                        f"Repas ajouté: {meal.name} - "
                        f"{meal.calculate_macros()['calories']:.0f} kcal"
                    )

            self.current_plan = meal_plan

            # Validation du plan
            validation = meal_plan.validate_against_target()

            logger.info(f"Plan généré: {meal_plan}")
            logger.info(f"Validation: {validation['is_valid']}")

            success_msg = (
                f"Plan généré avec succès: {duration_days} jour(s), "
                f"{len(meal_plan.meals)} repas total"
            )

            if not validation['is_valid']:
                success_msg += " (quelques écarts avec les objectifs)"

            self.status_updated.emit(success_msg)
            self.plan_generated.emit(meal_plan)

        except Exception as e:
            error_msg = f"Erreur lors de la génération du plan: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            self.status_updated.emit("Erreur lors de la génération")

    def _create_meal_distribution(self, meal_count: int) -> MealDistribution:
        """
        Crée une répartition calorique selon le nombre de repas.

        Args:
            meal_count: Nombre de repas par jour

        Returns:
            Répartition calorique
        """
        if meal_count == 3:
            # 3 repas: petit-déj, déjeuner, dîner
            return MealDistribution(
                breakfast=0.30,
                lunch=0.40,
                dinner=0.30,
                snack=0.0
            )
        elif meal_count == 4:
            # 4 repas: petit-déj, déjeuner, dîner, collation
            return MealDistribution(
                breakfast=0.25,
                lunch=0.35,
                dinner=0.30,
                snack=0.10
            )
        elif meal_count == 5:
            # 5 repas: petit-déj, collation, déjeuner, collation, dîner
            return MealDistribution(
                breakfast=0.25,
                lunch=0.35,
                dinner=0.25,
                snack=0.15  # Réparti entre 2 collations
            )
        else:  # 6 repas
            return MealDistribution(
                breakfast=0.20,
                lunch=0.30,
                dinner=0.25,
                snack=0.25  # Réparti entre 3 collations
            )

    def _get_meal_types(self, meal_count: int) -> list[tuple[str, float]]:
        """
        Retourne les types de repas et leur pourcentage calorique.

        Args:
            meal_count: Nombre de repas par jour

        Returns:
            Liste de tuples (type_repas, pourcentage)
        """
        distribution = self._create_meal_distribution(meal_count)

        if meal_count == 3:
            return [
                ("breakfast", distribution.breakfast),
                ("lunch", distribution.lunch),
                ("dinner", distribution.dinner)
            ]
        elif meal_count == 4:
            # 4 repas: petit-déj, déjeuner, dîner, collation
            return [
                ("breakfast", distribution.breakfast),
                ("lunch", distribution.lunch),
                ("dinner", distribution.dinner),
                ("snack", distribution.snack)
            ]
        elif meal_count == 5:
            # 5 repas: petit-déj, déjeuner, goûter (après-midi), dîner, collation soirée
            return [
                ("breakfast", distribution.breakfast),
                ("lunch", distribution.lunch),
                ("afternoon_snack", distribution.snack / 2),
                ("dinner", distribution.dinner),
                ("evening_snack", distribution.snack / 2)
            ]
        else:  # 6 repas
            # 6 repas: petit-déj, collation matinale, déjeuner, goûter, dîner, collation soirée
            return [
                ("breakfast", distribution.breakfast),
                ("morning_snack", distribution.snack / 3),
                ("lunch", distribution.lunch),
                ("afternoon_snack", distribution.snack / 3),
                ("dinner", distribution.dinner),
                ("evening_snack", distribution.snack / 3)
            ]

    def get_current_plan(self) -> Optional[MealPlan]:
        """
        Retourne le plan actuel.

        Returns:
            Le plan actuel ou None
        """
        return self.current_plan

    def validate_settings(self, settings: Dict) -> tuple[bool, str]:
        """
        Valide les paramètres avant génération.

        Args:
            settings: Paramètres à valider

        Returns:
            Tuple (est_valide, message_erreur)
        """
        try:
            # Vérifier l'objectif nutritionnel
            nutrition_target = settings.get("nutrition_target")
            if not nutrition_target:
                return False, "Objectif nutritionnel manquant"

            is_valid, msg = nutrition_target.validate()
            if not is_valid:
                return False, msg

            # Vérifier la durée
            duration_days = settings.get("duration_days", 0)
            if duration_days < 1 or duration_days > 84:
                return False, "La durée doit être entre 1 et 84 jours (12 semaines)"

            # Vérifier le nombre de repas
            meal_count = settings.get("meal_count", 0)
            if meal_count < 3 or meal_count > 6:
                return False, "Le nombre de repas doit être entre 3 et 6"

            return True, ""

        except Exception as e:
            return False, f"Erreur de validation: {str(e)}"

    def load_foods_count(self) -> int:
        """
        Retourne le nombre d'aliments en base.

        Returns:
            Nombre d'aliments
        """
        try:
            stats = self.db_manager.get_statistics()
            return stats.get("total_foods", 0)
        except Exception as e:
            logger.error(f"Erreur lors du comptage des aliments: {e}")
            return 0

    def get_available_foods_with_preferences(self, preferences: list) -> int:
        """
        Retourne le nombre d'aliments correspondant aux préférences.

        Args:
            preferences: Liste des tags requis

        Returns:
            Nombre d'aliments correspondants
        """
        try:
            if not preferences:
                return self.load_foods_count()

            foods = self.db_manager.get_foods_with_tags(preferences)
            return len(foods)

        except Exception as e:
            logger.error(f"Erreur lors du filtrage des aliments: {e}")
            return 0
