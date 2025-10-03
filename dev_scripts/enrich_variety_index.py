"""
Script pour enrichir les variety_index des aliments dans la base de données.
Attribue des indices de variété basés sur la rareté et l'exotisme des aliments.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from meal_planner.models.database import DatabaseManager
from meal_planner.config import DATABASE_PATH

# Catégories de rareté/variété
VARIETY_RULES = {
    # Aliments très communs (variety_index 1-3)
    "communs": {
        "variety_index": 2,
        "keywords": [
            "pain", "pâtes", "riz", "pomme de terre", "lait", "yaourt",
            "œuf", "poulet", "bœuf", "porc", "carotte", "tomate",
            "banane", "pomme", "orange", "laitue", "eau"
        ]
    },

    # Aliments courants (variety_index 4-5)
    "courants": {
        "variety_index": 5,
        "keywords": [
            "fromage", "thon", "saumon", "jambon", "dinde",
            "brocoli", "chou-fleur", "épinard", "concombre", "poivron",
            "raisin", "poire", "fraise", "kiwi", "mangue",
            "quinoa", "avoine", "sarrasin"
        ]
    },

    # Aliments variés (variety_index 6-7)
    "varies": {
        "variety_index": 7,
        "keywords": [
            "maquereau", "sardine", "hareng", "truite",
            "kale", "bok choy", "roquette", "endive",
            "papaye", "goyave", "fruit de la passion", "litchi",
            "millet", "amaranthe", "épeautre",
            "edamame", "tempeh", "seitan",
            "noix de cajou", "pistache", "noisette"
        ]
    },

    # Aliments exotiques/rares (variety_index 8-10)
    "exotiques": {
        "variety_index": 9,
        "keywords": [
            "quinoa rouge", "quinoa noir", "fonio", "teff",
            "spiruline", "chlorella", "moringa",
            "goji", "açaí", "camu camu", "baie de sureau",
            "yuzu", "kumquat", "ramboutan", "durian",
            "dragon fruit", "carambole",
            "chou romanesco", "chou-rave", "panais",
            "topinambour", "rutabaga",
            "viande de bison", "viande d'autruche", "viande de kangourou"
        ]
    }
}


def enrich_variety_indexes():
    """Enrichit les variety_index de tous les aliments."""
    db = DatabaseManager(DATABASE_PATH)

    print("="*80)
    print(" "*20 + "ENRICHISSEMENT DES VARIETY_INDEX")
    print("="*80)
    print()

    # Récupérer tous les aliments
    all_foods = db.get_all_foods()
    print(f"Total aliments: {len(all_foods)}")
    print()

    # Statistiques avant
    variety_counts_before = {}
    for food in all_foods:
        idx = food.variety_index
        variety_counts_before[idx] = variety_counts_before.get(idx, 0) + 1

    print("Distribution AVANT:")
    for idx in sorted(variety_counts_before.keys()):
        print(f"  Variety index {idx}: {variety_counts_before[idx]} aliments")
    print()

    # Appliquer les règles
    updated_count = 0

    for food in all_foods:
        new_variety_index = 5  # Par défaut: moyen

        food_name_lower = food.name.lower()

        # Vérifier les catégories (de la plus spécifique à la plus générale)
        for category_name in ["exotiques", "varies", "courants", "communs"]:
            rules = VARIETY_RULES[category_name]
            keywords = rules["keywords"]

            for keyword in keywords:
                if keyword in food_name_lower:
                    new_variety_index = rules["variety_index"]
                    break

            if new_variety_index != 5:
                break

        # Mettre à jour si changé
        if food.variety_index != new_variety_index:
            food.variety_index = new_variety_index
            # Mettre à jour dans la base
            db.update_food(food)
            updated_count += 1

    print(f"✅ {updated_count} aliments mis à jour")
    print()

    # Statistiques après
    all_foods = db.get_all_foods()  # Recharger
    variety_counts_after = {}
    for food in all_foods:
        idx = food.variety_index
        variety_counts_after[idx] = variety_counts_after.get(idx, 0) + 1

    print("Distribution APRÈS:")
    for idx in sorted(variety_counts_after.keys()):
        print(f"  Variety index {idx}: {variety_counts_after[idx]} aliments")
    print()

    print("="*80)
    print()

    return updated_count


if __name__ == "__main__":
    try:
        count = enrich_variety_indexes()
        print(f"✅ Enrichissement terminé: {count} aliments modifiés")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
