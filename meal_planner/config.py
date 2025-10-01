"""
Configuration et constantes de l'application Meal Planner Pro
"""

import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "meal_planner" / "data"
PRESETS_DIR = DATA_DIR / "presets"
DATABASE_PATH = DATA_DIR / "foods.db"

# Configuration des macros (min, max, step)
CALORIES_CONFIG = {
    "min": 1200,
    "max": 4000,
    "step": 50,
    "default": 2000
}

PROTEINS_CONFIG = {
    "min": 50,
    "max": 300,
    "step": 5,
    "default": 150
}

CARBS_CONFIG = {
    "min": 50,
    "max": 500,
    "step": 10,
    "default": 200
}

FATS_CONFIG = {
    "min": 30,
    "max": 150,
    "step": 5,
    "default": 70
}

# Options de repas
MEAL_COUNT_OPTIONS = [3, 4, 5, 6]
DEFAULT_MEAL_COUNT = 3

# Types de repas
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]

# Préférences diététiques (tags)
DIETARY_PREFERENCES = {
    "vegetarian": "Végétarien",
    "vegan": "Végan",
    "gluten_free": "Sans gluten",
    "lactose_free": "Sans lactose"
}

# Durée du plan
PLAN_DURATION_CONFIG = {
    "min": 1,
    "max": 14,
    "default": 7
}

# Catégories d'aliments
FOOD_CATEGORIES = [
    "Viandes et poissons",
    "Produits laitiers",
    "Céréales et féculents",
    "Légumes",
    "Fruits",
    "Légumineuses",
    "Noix et graines",
    "Huiles et matières grasses",
    "Autres"
]

# Tolérance pour la validation des macros (en pourcentage)
MACRO_TOLERANCE = 0.05  # ±5%

# Contraintes de quantités pour l'optimisation (en grammes)
MIN_FOOD_QUANTITY = 30
MAX_FOOD_QUANTITY = 500

# Nombre d'aliments par repas
MIN_FOODS_PER_MEAL = 3
MAX_FOODS_PER_MEAL = 8

# Configuration de l'interface
WINDOW_CONFIG = {
    "title": "Meal Planner Pro",
    "width": 1200,
    "height": 800,
    "min_width": 1000,
    "min_height": 600
}

# Configuration du logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": BASE_DIR / "meal_planner.log"
}

# Répartition des macros par repas (pourcentages par défaut)
DEFAULT_MEAL_DISTRIBUTION = {
    3: {  # 3 repas
        "breakfast": 0.30,
        "lunch": 0.40,
        "dinner": 0.30
    },
    4: {  # 4 repas
        "breakfast": 0.25,
        "lunch": 0.35,
        "snack": 0.10,
        "dinner": 0.30
    },
    5: {  # 5 repas
        "breakfast": 0.25,
        "snack1": 0.10,
        "lunch": 0.30,
        "snack2": 0.10,
        "dinner": 0.25
    },
    6: {  # 6 repas
        "breakfast": 0.20,
        "snack1": 0.10,
        "lunch": 0.25,
        "snack2": 0.10,
        "dinner": 0.25,
        "snack3": 0.10
    }
}

# Valeurs caloriques des macronutriments (kcal/g)
MACRO_CALORIES = {
    "proteins": 4,
    "carbs": 4,
    "fats": 9
}
