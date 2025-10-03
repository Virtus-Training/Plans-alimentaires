"""
Configuration et constantes de l'application Meal Planner Pro
"""

import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "meal_planner" / "data"
PRESETS_DIR = DATA_DIR / "presets"
ICONS_DIR = DATA_DIR / "icons"
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
    "lactose_free": "Sans lactose",
    "keto": "Keto (cétogène)",
    "paleo": "Paléo",
    "mediterranean": "Méditerranéen"
}

# Définition des régimes spécifiques avec leurs règles
DIET_RULES = {
    "keto": {
        "description": "Régime cétogène - très faible en glucides, riche en lipides",
        "carbs_max_percent": 0.10,  # Max 10% des calories en glucides
        "fats_min_percent": 0.70,   # Min 70% des calories en lipides
        "proteins_percent": 0.20,    # ~20% des calories en protéines
        "excluded_categories": [
            "céréales", "féculents", "fruits", "légumineuses"
        ],
        "allowed_low_carb_foods": [
            # Légumes faibles en glucides autorisés
            "épinards", "chou kale", "laitue", "concombre", "courgette",
            "brocoli", "chou-fleur", "asperges", "champignons", "tomates"
        ],
        "prioritized_foods": [
            # Aliments prioritaires en keto
            "huile", "beurre", "fromage", "viandes", "poissons", "œufs",
            "avocat", "noix", "graines"
        ]
    },
    "paleo": {
        "description": "Régime paléo - aliments non transformés, comme au paléolithique",
        "excluded_categories": [
            "céréales", "produits laitiers", "légumineuses"
        ],
        "excluded_keywords": [
            "pain", "pâtes", "riz", "blé", "lait", "yaourt", "fromage",
            "lentilles", "haricots", "pois", "soja"
        ],
        "prioritized_foods": [
            "viandes", "poissons", "œufs", "légumes", "fruits",
            "noix", "graines", "huile d'olive", "huile de coco"
        ],
        "allowed_exceptions": [
            # Quelques exceptions couramment acceptées
            "patate douce", "courge", "huile d'olive"
        ]
    },
    "mediterranean": {
        "description": "Régime méditerranéen - riche en fruits, légumes, poissons, huile d'olive",
        "prioritized_categories": [
            "légumes", "fruits", "poissons", "légumineuses", "noix et graines"
        ],
        "prioritized_foods": [
            "huile d'olive", "tomates", "olives", "poissons gras",
            "légumes verts", "légumineuses", "noix", "fruits frais"
        ],
        "limited_foods": [
            # Aliments à limiter (pas exclus mais moins prioritaires)
            "viande rouge", "beurre", "crème"
        ],
        "carbs_range": (0.40, 0.50),   # 40-50% glucides
        "fats_range": (0.30, 0.40),    # 30-40% lipides (surtout insaturés)
        "proteins_range": (0.15, 0.20)  # 15-20% protéines
    }
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
MACRO_TOLERANCE = 0.10  # ±10% (tolérance réaliste pour un plan alimentaire précis)

# Contraintes de quantités pour l'optimisation (en grammes)
MIN_FOOD_QUANTITY = 10  # Réduit pour permettre de petites quantités (huile, épices, etc.)
MAX_FOOD_QUANTITY = 500

# Nombre d'aliments par repas (augmenté pour plus de diversité)
MIN_FOODS_PER_MEAL = 5
MAX_FOODS_PER_MEAL = 9

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

# Valeurs caloriques des macronutriments (kcal/g)
MACRO_CALORIES = {
    "proteins": 4,
    "carbs": 4,
    "fats": 9
}

# ========== Modes de Génération ==========

# Modes de génération disponibles
GENERATION_MODES = {
    "food": "🍎 Par Aliments",
    "preset": "🍽️ Repas Complets",
    "components": "🥗 Entrée/Plat/Dessert",
    "categories": "📋 Par Catégories"
}

# Chemin vers le fichier de règles de catégories
CATEGORY_RULES_PATH = BASE_DIR / "meal_planner" / "config" / "category_rules.json"

# Catégories d'aliments détaillées pour le mode "Par Catégories"
FOOD_CATEGORIES_DETAILED = {
    "protéines": ["viandes", "poissons", "œufs", "tofu", "seitan"],
    "féculents": ["céréales", "pain", "pâtes", "riz", "pommes de terre"],
    "légumes": ["légumes verts", "légumes racines", "légumes-feuilles", "crucifères"],
    "fruits": ["fruits frais", "fruits secs", "baies"],
    "produits laitiers": ["lait", "yaourt", "fromage", "fromage blanc"],
    "noix": ["amandes", "noix", "noisettes", "pistaches", "graines"],
    "légumineuses": ["lentilles", "haricots", "pois chiches", "fèves"],
    "matières grasses": ["huile", "beurre", "margarine", "avocat"]
}

# Mapping catégories simples -> catégories détaillées dans la base
# Pour mapper les catégories configurables aux vraies catégories de la DB
CATEGORY_MAPPING = {
    "protéines": ["viandes", "poissons", "œufs", "légumineuses", "tofu"],
    "féculents": ["céréales", "féculents"],
    "légumes": ["légumes"],
    "fruits": ["fruits"],
    "produits laitiers": ["produits laitiers"],
    "noix": ["noix et graines"],
    "céréales": ["céréales", "féculents"],
    "légumineuses": ["légumineuses"]
}
