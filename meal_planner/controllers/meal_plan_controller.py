"""
MealPlanController - Contrôleur pour la gestion des plans alimentaires
"""

from typing import Optional, Dict
from PyQt6.QtCore import QObject, pyqtSignal

from meal_planner.models.meal_plan import MealPlan
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.models.database import DatabaseManager
from meal_planner.utils.logger import get_logger

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

    def generate_meal_plan(self, settings: Dict) -> None:
        """
        Génère un plan alimentaire basé sur les paramètres.

        Pour la Phase 1, cette méthode crée un plan vide pour démonstration.
        L'algorithme de génération sera implémenté en Phase 2.

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

            # Pour la Phase 1: créer un plan vide pour démonstration
            # Phase 2: Implémenter l'algorithme de génération réel
            meal_plan = MealPlan(
                duration_days=duration_days,
                nutrition_target=nutrition_target,
                meals=[],  # Phase 2: Générer les repas
                notes=f"Plan généré avec {meal_count} repas/jour. "
                      f"Préférences: {', '.join(dietary_preferences) if dietary_preferences else 'Aucune'}"
            )

            self.current_plan = meal_plan

            logger.info(f"Plan généré: {meal_plan}")
            self.status_updated.emit(
                f"Plan généré: {duration_days} jour(s), "
                f"{meal_count} repas/jour"
            )

            # Note pour Phase 1: Le plan est vide, l'algorithme sera en Phase 2
            self.status_updated.emit(
                "NOTE: Génération de repas à implémenter (Phase 2)"
            )

            self.plan_generated.emit(meal_plan)

        except Exception as e:
            error_msg = f"Erreur lors de la génération du plan: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
            self.status_updated.emit("Erreur lors de la génération")

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
            if duration_days < 1 or duration_days > 14:
                return False, "La durée doit être entre 1 et 14 jours"

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
