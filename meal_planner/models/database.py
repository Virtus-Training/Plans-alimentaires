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
            variety_index=food.variety_index
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
            variety_index=getattr(food_db, 'variety_index', 5)
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

            return {
                "total_foods": total,
                "categories": categories,
                "database_path": str(self.db_path)
            }
