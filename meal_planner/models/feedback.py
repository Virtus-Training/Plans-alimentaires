"""
Système de feedback et d'apprentissage des préférences utilisateur
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import json
from pathlib import Path

from meal_planner.models.meal import Meal
from meal_planner.models.meal_plan import MealPlan
from meal_planner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MealFeedback:
    """Feedback sur un repas spécifique."""
    meal_id: Optional[int]
    meal_name: str
    rating: float  # 1-5
    followed: bool  # Si l'utilisateur a suivi le plan
    timestamp: datetime = field(default_factory=datetime.now)
    comments: str = ""


@dataclass
class FoodPreference:
    """Préférence apprise pour un aliment."""
    food_id: int
    food_name: str
    preference_score: float = 0.0  # -1 (n'aime pas) à +1 (aime beaucoup)
    times_used: int = 0
    times_liked: int = 0
    times_disliked: int = 0
    last_used: Optional[datetime] = None


class UserFeedbackSystem:
    """
    Système de gestion du feedback utilisateur et d'apprentissage des préférences.

    Permet de:
    - Enregistrer les retours sur les plans alimentaires
    - Apprendre les préférences alimentaires
    - Ajuster les recommandations futures
    """

    def __init__(self, user_id: str = "default", storage_path: Optional[Path] = None):
        """
        Initialise le système de feedback.

        Args:
            user_id: Identifiant de l'utilisateur
            storage_path: Chemin de stockage des données (optionnel)
        """
        self.user_id = user_id
        self.storage_path = storage_path or Path("meal_planner/data/user_feedback")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Données en mémoire
        self.meal_feedbacks: List[MealFeedback] = []
        self.food_preferences: Dict[int, FoodPreference] = {}
        self.plan_ratings: Dict[int, float] = {}

        # Charger les données existantes
        self.load_from_disk()

    def record_meal_feedback(
        self,
        meal: Meal,
        rating: float,
        followed: bool = True,
        comments: str = ""
    ) -> None:
        """
        Enregistre le feedback sur un repas.

        Args:
            meal: Le repas évalué
            rating: Note de 1 à 5
            followed: Si l'utilisateur a suivi le plan
            comments: Commentaires optionnels
        """
        if not 1 <= rating <= 5:
            raise ValueError("La note doit être entre 1 et 5")

        # Créer le feedback
        feedback = MealFeedback(
            meal_id=meal.id,
            meal_name=meal.name,
            rating=rating,
            followed=followed,
            comments=comments
        )

        self.meal_feedbacks.append(feedback)

        # Mettre à jour les préférences pour chaque aliment du repas
        for food, qty in meal.foods:
            self._update_food_preference(food.id, food.name, rating, followed)

        logger.info(
            f"Feedback enregistré: {meal.name} - Note: {rating}/5, "
            f"Suivi: {'Oui' if followed else 'Non'}"
        )

        # Sauvegarder
        self.save_to_disk()

    def record_plan_feedback(self, plan: MealPlan, overall_rating: float) -> None:
        """
        Enregistre le feedback global sur un plan.

        Args:
            plan: Le plan alimentaire
            overall_rating: Note globale de 1 à 5
        """
        if not 1 <= overall_rating <= 5:
            raise ValueError("La note doit être entre 1 et 5")

        if plan.id:
            self.plan_ratings[plan.id] = overall_rating

        logger.info(f"Feedback plan enregistré: {plan} - Note: {overall_rating}/5")
        self.save_to_disk()

    def _update_food_preference(
        self,
        food_id: int,
        food_name: str,
        rating: float,
        followed: bool
    ) -> None:
        """
        Met à jour la préférence pour un aliment.

        Args:
            food_id: ID de l'aliment
            food_name: Nom de l'aliment
            rating: Note du repas (1-5)
            followed: Si le plan a été suivi
        """
        if food_id not in self.food_preferences:
            self.food_preferences[food_id] = FoodPreference(
                food_id=food_id,
                food_name=food_name
            )

        pref = self.food_preferences[food_id]
        pref.times_used += 1
        pref.last_used = datetime.now()

        # Si le repas a été suivi et bien noté, c'est positif
        if followed and rating >= 4:
            pref.times_liked += 1
            pref.preference_score += 0.1
        elif followed and rating <= 2:
            pref.times_disliked += 1
            pref.preference_score -= 0.1
        elif not followed:
            # Si non suivi, c'est négatif
            pref.times_disliked += 1
            pref.preference_score -= 0.15

        # Normaliser entre -1 et +1
        pref.preference_score = max(-1.0, min(1.0, pref.preference_score))

    def get_food_preference_score(self, food_id: int) -> float:
        """
        Retourne le score de préférence pour un aliment.

        Args:
            food_id: ID de l'aliment

        Returns:
            Score entre -1 (n'aime pas) et +1 (aime beaucoup), 0 = neutre
        """
        if food_id in self.food_preferences:
            return self.food_preferences[food_id].preference_score
        return 0.0

    def get_top_liked_foods(self, limit: int = 10) -> List[FoodPreference]:
        """
        Retourne les aliments les plus appréciés.

        Args:
            limit: Nombre maximum d'aliments à retourner

        Returns:
            Liste des préférences alimentaires, triées par score décroissant
        """
        sorted_prefs = sorted(
            self.food_preferences.values(),
            key=lambda p: p.preference_score,
            reverse=True
        )
        return sorted_prefs[:limit]

    def get_disliked_foods(self, threshold: float = -0.3) -> List[FoodPreference]:
        """
        Retourne les aliments peu appréciés.

        Args:
            threshold: Seuil en-dessous duquel un aliment est considéré non apprécié

        Returns:
            Liste des aliments peu appréciés
        """
        return [
            pref for pref in self.food_preferences.values()
            if pref.preference_score <= threshold
        ]

    def get_statistics(self) -> Dict:
        """
        Retourne des statistiques sur les feedbacks.

        Returns:
            Dictionnaire avec les statistiques
        """
        total_feedbacks = len(self.meal_feedbacks)
        followed_count = sum(1 for f in self.meal_feedbacks if f.followed)
        avg_rating = (
            sum(f.rating for f in self.meal_feedbacks) / total_feedbacks
            if total_feedbacks > 0 else 0
        )

        return {
            "total_feedbacks": total_feedbacks,
            "plans_followed_pct": (followed_count / total_feedbacks * 100) if total_feedbacks > 0 else 0,
            "average_rating": avg_rating,
            "total_food_preferences": len(self.food_preferences),
            "liked_foods_count": len([p for p in self.food_preferences.values() if p.preference_score > 0.3]),
            "disliked_foods_count": len([p for p in self.food_preferences.values() if p.preference_score < -0.3])
        }

    def save_to_disk(self) -> None:
        """Sauvegarde les données sur le disque."""
        try:
            # Sauvegarder les feedbacks
            feedbacks_file = self.storage_path / f"{self.user_id}_feedbacks.json"
            feedbacks_data = [
                {
                    "meal_id": f.meal_id,
                    "meal_name": f.meal_name,
                    "rating": f.rating,
                    "followed": f.followed,
                    "timestamp": f.timestamp.isoformat(),
                    "comments": f.comments
                }
                for f in self.meal_feedbacks
            ]

            with open(feedbacks_file, 'w', encoding='utf-8') as f:
                json.dump(feedbacks_data, f, indent=2, ensure_ascii=False)

            # Sauvegarder les préférences
            prefs_file = self.storage_path / f"{self.user_id}_preferences.json"
            prefs_data = {
                str(food_id): {
                    "food_id": pref.food_id,
                    "food_name": pref.food_name,
                    "preference_score": pref.preference_score,
                    "times_used": pref.times_used,
                    "times_liked": pref.times_liked,
                    "times_disliked": pref.times_disliked,
                    "last_used": pref.last_used.isoformat() if pref.last_used else None
                }
                for food_id, pref in self.food_preferences.items()
            }

            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Feedback sauvegardé pour l'utilisateur {self.user_id}")

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du feedback: {e}")

    def load_from_disk(self) -> None:
        """Charge les données depuis le disque."""
        try:
            # Charger les feedbacks
            feedbacks_file = self.storage_path / f"{self.user_id}_feedbacks.json"
            if feedbacks_file.exists():
                with open(feedbacks_file, 'r', encoding='utf-8') as f:
                    feedbacks_data = json.load(f)

                self.meal_feedbacks = [
                    MealFeedback(
                        meal_id=f["meal_id"],
                        meal_name=f["meal_name"],
                        rating=f["rating"],
                        followed=f["followed"],
                        timestamp=datetime.fromisoformat(f["timestamp"]),
                        comments=f.get("comments", "")
                    )
                    for f in feedbacks_data
                ]

            # Charger les préférences
            prefs_file = self.storage_path / f"{self.user_id}_preferences.json"
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs_data = json.load(f)

                self.food_preferences = {
                    int(food_id): FoodPreference(
                        food_id=pref["food_id"],
                        food_name=pref["food_name"],
                        preference_score=pref["preference_score"],
                        times_used=pref["times_used"],
                        times_liked=pref["times_liked"],
                        times_disliked=pref["times_disliked"],
                        last_used=datetime.fromisoformat(pref["last_used"]) if pref["last_used"] else None
                    )
                    for food_id, pref in prefs_data.items()
                }

                logger.info(
                    f"Feedback chargé pour {self.user_id}: "
                    f"{len(self.meal_feedbacks)} feedbacks, "
                    f"{len(self.food_preferences)} préférences"
                )

        except Exception as e:
            logger.error(f"Erreur lors du chargement du feedback: {e}")

    def clear_all_data(self) -> None:
        """Efface toutes les données de feedback (à utiliser avec précaution)."""
        self.meal_feedbacks.clear()
        self.food_preferences.clear()
        self.plan_ratings.clear()
        self.save_to_disk()
        logger.warning(f"Toutes les données de feedback effacées pour {self.user_id}")
