"""
DatabaseManager - Gestion de la base de données SQLite avec SQLAlchemy
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from meal_planner.models.food import Food
from meal_planner.config import DATABASE_PATH, PRESETS_DIR
from meal_planner.utils.logger import get_logger

# Import des modèles PresetMeal et MealComponent (import tardif pour éviter circular import)
# Ces imports seront faits dans les méthodes qui en ont besoin

logger = get_logger(__name__)

Base = declarative_base()


class FoodDB(Base):
    """Table SQLAlchemy pour les aliments."""
    __tablename__ = 'foods'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    calories = Column(Float, nullable=False)
    proteins = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    fibers = Column(Float, default=0.0)
    tags = Column(Text, default='[]')  # JSON array as string
    price_per_100g = Column(Float, default=0.0)
    health_index = Column(Integer, default=5)
    variety_index = Column(Integer, default=5)
    unit_weight = Column(Float, nullable=True)  # Poids unitaire en grammes


class PresetMealDB(Base):
    """Table SQLAlchemy pour les repas prédéfinis."""
    __tablename__ = 'preset_meals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    meal_type = Column(String(50), nullable=False)
    foods_json = Column(Text, nullable=False)  # JSON: [{"food_id": int, "quantity": float}, ...]
    description = Column(Text, default='')


class MealComponentDB(Base):
    """Table SQLAlchemy pour les composantes de repas (entrée/plat/dessert)."""
    __tablename__ = 'meal_components'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    component_type = Column(String(50), nullable=False)  # entrée, plat, dessert, accompagnement
    foods_json = Column(Text, nullable=False)  # JSON: [{"food_id": int, "quantity": float}, ...]
    description = Column(Text, default='')


class DatabaseManager:
    """
    Gestionnaire de la base de données SQLite.

    Fournit les opérations CRUD pour les aliments et la gestion de la base.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialise le gestionnaire de base de données.

        Args:
            db_path: Chemin vers la base de données (utilise DATABASE_PATH par défaut)
        """
        self.db_path = db_path or DATABASE_PATH
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialise la connexion et crée les tables si nécessaire."""
        try:
            # Créer le répertoire parent si nécessaire
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Créer l'engine SQLAlchemy
            self.engine = create_engine(
                f'sqlite:///{self.db_path}',
                echo=False,
                connect_args={'check_same_thread': False}
            )

            # Créer la session factory
            self.SessionLocal = sessionmaker(bind=self.engine)

            # Créer les tables
            Base.metadata.create_all(self.engine)

            logger.info(f"Base de données initialisée: {self.db_path}")

        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager pour obtenir une session de base de données.

        Yields:
            Session SQLAlchemy
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur de session: {e}")
            raise
        finally:
            session.close()

    def _food_to_db(self, food: Food) -> FoodDB:
        """Convertit un objet Food en objet FoodDB."""
        return FoodDB(
            id=food.id,
            name=food.name,
            category=food.category,
            calories=food.calories,
            proteins=food.proteins,
            carbs=food.carbs,
            fats=food.fats,
            fibers=food.fibers,
            tags=json.dumps(food.tags),
            price_per_100g=food.price_per_100g,
            health_index=food.health_index,
            variety_index=food.variety_index,
            unit_weight=food.unit_weight
        )

    def _db_to_food(self, food_db: FoodDB) -> Food:
        """Convertit un objet FoodDB en objet Food."""
        tags = json.loads(food_db.tags) if food_db.tags else []

        return Food(
            id=food_db.id,
            name=food_db.name,
            category=food_db.category,
            calories=food_db.calories,
            proteins=food_db.proteins,
            carbs=food_db.carbs,
            fats=food_db.fats,
            fibers=food_db.fibers,
            tags=tags,
            price_per_100g=getattr(food_db, 'price_per_100g', 0.0),
            health_index=getattr(food_db, 'health_index', 5),
            variety_index=getattr(food_db, 'variety_index', 5),
            unit_weight=getattr(food_db, 'unit_weight', None)
        )

    def add_food(self, food: Food) -> Food:
        """
        Ajoute un aliment à la base de données.

        Args:
            food: L'aliment à ajouter

        Returns:
            L'aliment avec son ID assigné

        Raises:
            ValueError: Si la validation échoue ou si l'aliment existe déjà
        """
        # Valider l'aliment
        is_valid, msg = food.validate()
        if not is_valid:
            raise ValueError(f"Aliment invalide: {msg}")

        with self.get_session() as session:
            # Vérifier si l'aliment existe déjà
            existing = session.query(FoodDB).filter_by(name=food.name).first()
            if existing:
                raise ValueError(f"Un aliment nommé '{food.name}' existe déjà")

            food_db = self._food_to_db(food)
            session.add(food_db)
            session.flush()

            food.id = food_db.id
            logger.info(f"Aliment ajouté: {food.name} (ID: {food.id})")

            return food

    def get_food_by_id(self, food_id: int) -> Optional[Food]:
        """
        Récupère un aliment par son ID.

        Args:
            food_id: L'ID de l'aliment

        Returns:
            L'aliment ou None s'il n'existe pas
        """
        with self.get_session() as session:
            food_db = session.query(FoodDB).filter_by(id=food_id).first()
            return self._db_to_food(food_db) if food_db else None

    def get_food_by_name(self, name: str) -> Optional[Food]:
        """
        Récupère un aliment par son nom.

        Args:
            name: Le nom de l'aliment

        Returns:
            L'aliment ou None s'il n'existe pas
        """
        with self.get_session() as session:
            food_db = session.query(FoodDB).filter_by(name=name).first()
            return self._db_to_food(food_db) if food_db else None

    def get_all_foods(self) -> List[Food]:
        """
        Récupère tous les aliments de la base de données.

        Returns:
            Liste de tous les aliments
        """
        with self.get_session() as session:
            foods_db = session.query(FoodDB).all()
            return [self._db_to_food(food_db) for food_db in foods_db]

    def get_foods_by_category(self, category: str) -> List[Food]:
        """
        Récupère tous les aliments d'une catégorie.

        Args:
            category: La catégorie recherchée

        Returns:
            Liste des aliments de la catégorie
        """
        with self.get_session() as session:
            foods_db = session.query(FoodDB).filter_by(category=category).all()
            return [self._db_to_food(food_db) for food_db in foods_db]

    def get_foods_with_tags(self, required_tags: List[str]) -> List[Food]:
        """
        Récupère les aliments possédant tous les tags requis.

        Args:
            required_tags: Liste des tags requis

        Returns:
            Liste des aliments correspondants
        """
        all_foods = self.get_all_foods()
        return [food for food in all_foods if food.matches_preferences(required_tags)]

    def update_food(self, food: Food) -> Food:
        """
        Met à jour un aliment existant.

        Args:
            food: L'aliment à mettre à jour (doit avoir un ID)

        Returns:
            L'aliment mis à jour

        Raises:
            ValueError: Si l'aliment n'a pas d'ID ou n'existe pas
        """
        if food.id is None:
            raise ValueError("L'aliment doit avoir un ID pour être mis à jour")

        # Valider l'aliment
        is_valid, msg = food.validate()
        if not is_valid:
            raise ValueError(f"Aliment invalide: {msg}")

        with self.get_session() as session:
            food_db = session.query(FoodDB).filter_by(id=food.id).first()

            if not food_db:
                raise ValueError(f"Aliment avec ID {food.id} introuvable")

            # Mettre à jour les champs
            food_db.name = food.name
            food_db.category = food.category
            food_db.calories = food.calories
            food_db.proteins = food.proteins
            food_db.carbs = food.carbs
            food_db.fats = food.fats
            food_db.fibers = food.fibers
            food_db.tags = json.dumps(food.tags)
            food_db.price_per_100g = food.price_per_100g
            food_db.health_index = food.health_index
            food_db.variety_index = food.variety_index

            logger.info(f"Aliment mis à jour: {food.name} (ID: {food.id})")

            return food

    def delete_food(self, food_id: int) -> bool:
        """
        Supprime un aliment de la base de données.

        Args:
            food_id: L'ID de l'aliment à supprimer

        Returns:
            True si l'aliment a été supprimé, False sinon
        """
        with self.get_session() as session:
            food_db = session.query(FoodDB).filter_by(id=food_id).first()

            if food_db:
                session.delete(food_db)
                logger.info(f"Aliment supprimé: ID {food_id}")
                return True

            return False

    def search_foods(self, query: str) -> List[Food]:
        """
        Recherche des aliments par nom (recherche partielle).

        Args:
            query: Chaîne de recherche

        Returns:
            Liste des aliments correspondants
        """
        with self.get_session() as session:
            foods_db = session.query(FoodDB).filter(
                FoodDB.name.like(f'%{query}%')
            ).all()
            return [self._db_to_food(food_db) for food_db in foods_db]

    def load_foods_from_json(self, json_path: Path) -> int:
        """
        Charge des aliments depuis un fichier JSON.

        Args:
            json_path: Chemin vers le fichier JSON

        Returns:
            Nombre d'aliments ajoutés

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le JSON est invalide
        """
        if not json_path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Le JSON doit contenir une liste d'aliments")

            added_count = 0
            for food_data in data:
                try:
                    food = Food.from_dict(food_data)
                    self.add_food(food)
                    added_count += 1
                except Exception as e:
                    logger.warning(f"Impossible d'ajouter {food_data.get('name', 'inconnu')}: {e}")

            logger.info(f"{added_count} aliments chargés depuis {json_path}")
            return added_count

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide: {e}")

    def get_statistics(self) -> Dict:
        """
        Retourne des statistiques sur la base de données.

        Returns:
            Dict contenant les statistiques
        """
        with self.get_session() as session:
            total = session.query(FoodDB).count()

            categories = {}
            for food_db in session.query(FoodDB).all():
                cat = food_db.category
                categories[cat] = categories.get(cat, 0) + 1

            preset_meals_count = session.query(PresetMealDB).count()
            components_count = session.query(MealComponentDB).count()

            return {
                "total_foods": total,
                "categories": categories,
                "preset_meals": preset_meals_count,
                "meal_components": components_count,
                "database_path": str(self.db_path)
            }

    # ========== Méthodes CRUD pour PresetMeal ==========

    def add_preset_meal(self, preset_meal) -> 'PresetMeal':
        """
        Ajoute un repas prédéfini à la base de données.

        Args:
            preset_meal: Le repas prédéfini (PresetMeal)

        Returns:
            Le repas avec son ID assigné
        """
        from meal_planner.models.preset_meal import PresetMeal

        # Valider le repas
        is_valid, msg = preset_meal.validate()
        if not is_valid:
            raise ValueError(f"Repas prédéfini invalide: {msg}")

        with self.get_session() as session:
            preset_db = PresetMealDB(
                name=preset_meal.name,
                meal_type=preset_meal.meal_type,
                foods_json=preset_meal.to_json_string(),
                description=preset_meal.description
            )
            session.add(preset_db)
            session.flush()

            preset_meal.id = preset_db.id
            logger.info(f"Repas prédéfini ajouté: {preset_meal.name} (ID: {preset_meal.id})")

            return preset_meal

    def get_preset_meal_by_id(self, meal_id: int) -> Optional['PresetMeal']:
        """
        Récupère un repas prédéfini par son ID.

        Args:
            meal_id: L'ID du repas

        Returns:
            Le repas prédéfini ou None
        """
        from meal_planner.models.preset_meal import PresetMeal

        with self.get_session() as session:
            preset_db = session.query(PresetMealDB).filter_by(id=meal_id).first()
            if not preset_db:
                return None

            # Récupérer tous les aliments nécessaires
            foods_by_id = {food.id: food for food in self.get_all_foods()}

            return PresetMeal.from_db_row({
                "id": preset_db.id,
                "name": preset_db.name,
                "meal_type": preset_db.meal_type,
                "foods_json": preset_db.foods_json,
                "description": preset_db.description
            }, foods_by_id)

    def get_all_preset_meals(self) -> List['PresetMeal']:
        """
        Récupère tous les repas prédéfinis.

        Returns:
            Liste de PresetMeal
        """
        from meal_planner.models.preset_meal import PresetMeal

        with self.get_session() as session:
            presets_db = session.query(PresetMealDB).all()
            foods_by_id = {food.id: food for food in self.get_all_foods()}

            return [
                PresetMeal.from_db_row({
                    "id": p.id,
                    "name": p.name,
                    "meal_type": p.meal_type,
                    "foods_json": p.foods_json,
                    "description": p.description
                }, foods_by_id)
                for p in presets_db
            ]

    def get_preset_meals_by_type(self, meal_type: str) -> List['PresetMeal']:
        """
        Récupère les repas prédéfinis d'un type donné.

        Args:
            meal_type: Type de repas

        Returns:
            Liste de PresetMeal
        """
        from meal_planner.models.preset_meal import PresetMeal

        with self.get_session() as session:
            presets_db = session.query(PresetMealDB).filter_by(meal_type=meal_type).all()
            foods_by_id = {food.id: food for food in self.get_all_foods()}

            return [
                PresetMeal.from_db_row({
                    "id": p.id,
                    "name": p.name,
                    "meal_type": p.meal_type,
                    "foods_json": p.foods_json,
                    "description": p.description
                }, foods_by_id)
                for p in presets_db
            ]

    def update_preset_meal(self, preset_meal) -> 'PresetMeal':
        """
        Met à jour un repas prédéfini.

        Args:
            preset_meal: Le repas à mettre à jour (doit avoir un ID)

        Returns:
            Le repas mis à jour
        """
        if preset_meal.id is None:
            raise ValueError("Le repas doit avoir un ID pour être mis à jour")

        is_valid, msg = preset_meal.validate()
        if not is_valid:
            raise ValueError(f"Repas prédéfini invalide: {msg}")

        with self.get_session() as session:
            preset_db = session.query(PresetMealDB).filter_by(id=preset_meal.id).first()

            if not preset_db:
                raise ValueError(f"Repas avec ID {preset_meal.id} introuvable")

            preset_db.name = preset_meal.name
            preset_db.meal_type = preset_meal.meal_type
            preset_db.foods_json = preset_meal.to_json_string()
            preset_db.description = preset_meal.description

            logger.info(f"Repas prédéfini mis à jour: {preset_meal.name} (ID: {preset_meal.id})")

            return preset_meal

    def delete_preset_meal(self, meal_id: int) -> bool:
        """
        Supprime un repas prédéfini.

        Args:
            meal_id: L'ID du repas à supprimer

        Returns:
            True si supprimé, False sinon
        """
        with self.get_session() as session:
            preset_db = session.query(PresetMealDB).filter_by(id=meal_id).first()

            if preset_db:
                session.delete(preset_db)
                logger.info(f"Repas prédéfini supprimé: ID {meal_id}")
                return True

            return False

    # ========== Méthodes CRUD pour MealComponent ==========

    def add_meal_component(self, component) -> 'MealComponent':
        """
        Ajoute une composante de repas à la base de données.

        Args:
            component: La composante (MealComponent)

        Returns:
            La composante avec son ID assigné
        """
        from meal_planner.models.meal_component import MealComponent

        is_valid, msg = component.validate()
        if not is_valid:
            raise ValueError(f"Composante invalide: {msg}")

        with self.get_session() as session:
            component_db = MealComponentDB(
                name=component.name,
                component_type=component.component_type,
                foods_json=component.to_json_string(),
                description=component.description
            )
            session.add(component_db)
            session.flush()

            component.id = component_db.id
            logger.info(f"Composante ajoutée: {component.name} (ID: {component.id})")

            return component

    def get_meal_component_by_id(self, component_id: int) -> Optional['MealComponent']:
        """
        Récupère une composante par son ID.

        Args:
            component_id: L'ID de la composante

        Returns:
            La composante ou None
        """
        from meal_planner.models.meal_component import MealComponent

        with self.get_session() as session:
            component_db = session.query(MealComponentDB).filter_by(id=component_id).first()
            if not component_db:
                return None

            foods_by_id = {food.id: food for food in self.get_all_foods()}

            return MealComponent.from_db_row({
                "id": component_db.id,
                "name": component_db.name,
                "component_type": component_db.component_type,
                "foods_json": component_db.foods_json,
                "description": component_db.description
            }, foods_by_id)

    def get_all_meal_components(self) -> List['MealComponent']:
        """
        Récupère toutes les composantes de repas.

        Returns:
            Liste de MealComponent
        """
        from meal_planner.models.meal_component import MealComponent

        with self.get_session() as session:
            components_db = session.query(MealComponentDB).all()
            foods_by_id = {food.id: food for food in self.get_all_foods()}

            return [
                MealComponent.from_db_row({
                    "id": c.id,
                    "name": c.name,
                    "component_type": c.component_type,
                    "foods_json": c.foods_json,
                    "description": c.description
                }, foods_by_id)
                for c in components_db
            ]

    def get_components_by_type(self, component_type: str) -> List['MealComponent']:
        """
        Récupère les composantes d'un type donné.

        Args:
            component_type: Type de composante (entrée, plat, dessert, accompagnement)

        Returns:
            Liste de MealComponent
        """
        from meal_planner.models.meal_component import MealComponent

        with self.get_session() as session:
            components_db = session.query(MealComponentDB).filter_by(
                component_type=component_type
            ).all()
            foods_by_id = {food.id: food for food in self.get_all_foods()}

            return [
                MealComponent.from_db_row({
                    "id": c.id,
                    "name": c.name,
                    "component_type": c.component_type,
                    "foods_json": c.foods_json,
                    "description": c.description
                }, foods_by_id)
                for c in components_db
            ]

    def update_meal_component(self, component) -> 'MealComponent':
        """
        Met à jour une composante de repas.

        Args:
            component: La composante à mettre à jour (doit avoir un ID)

        Returns:
            La composante mise à jour
        """
        if component.id is None:
            raise ValueError("La composante doit avoir un ID pour être mise à jour")

        is_valid, msg = component.validate()
        if not is_valid:
            raise ValueError(f"Composante invalide: {msg}")

        with self.get_session() as session:
            component_db = session.query(MealComponentDB).filter_by(id=component.id).first()

            if not component_db:
                raise ValueError(f"Composante avec ID {component.id} introuvable")

            component_db.name = component.name
            component_db.component_type = component.component_type
            component_db.foods_json = component.to_json_string()
            component_db.description = component.description

            logger.info(f"Composante mise à jour: {component.name} (ID: {component.id})")

            return component

    def delete_meal_component(self, component_id: int) -> bool:
        """
        Supprime une composante de repas.

        Args:
            component_id: L'ID de la composante à supprimer

        Returns:
            True si supprimé, False sinon
        """
        with self.get_session() as session:
            component_db = session.query(MealComponentDB).filter_by(id=component_id).first()

            if component_db:
                session.delete(component_db)
                logger.info(f"Composante supprimée: ID {component_id}")
                return True

            return False
