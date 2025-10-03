"""
Script intelligent pour enrichir les variety_index basé sur les catégories.
Utilise une approche plus large pour mieux distribuer les variety_index.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from meal_planner.models.database import DatabaseManager
from meal_planner.config import DATABASE_PATH

# Règles basées sur les catégories
CATEGORY_VARIETY_MAPPING = {
    # Index 2 - Aliments très communs
    2: {
        "categories": ["pain", "pâtes", "riz", "pommes de terre"],
        "common_words": ["blanc", "nature", "simple"]
    },

    # Index 3-4 - Aliments communs
    3: {
        "categories": ["lait", "yaourt", "œufs", "poulet", "bœuf"],
        "common_words": []
    },

    # Index 5-6 - Aliments courants (défaut)
    5: {
        "categories": ["fromage", "poisson", "légumes", "fruits"],
        "common_words": ["ordinaire", "standard"]
    },

    # Index 7-8 - Aliments variés
    7: {
        "categories": ["fruits de mer", "poissons gras", "légumes verts", "céréales complètes"],
        "common_words": ["bio", "complet", "entier", "gras"]
    },

    # Index 9-10 - Aliments rares/exotiques
    9: {
        "categories": ["super-aliments", "exotique", "rare"],
        "common_words": ["exotique", "rare", "spécial", "importé"]
    }
}


def auto_enrich_by_category():
    """Enrichit automatiquement basé sur les catégories existantes."""
    db = DatabaseManager(DATABASE_PATH)

    print("="*80)
    print(" "*20 + "ENRICHISSEMENT AUTOMATIQUE PAR CATÉGORIE")
    print("="*80)
    print()

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

    # Stratégie: répartir les aliments variety_index=5 vers d'autres catégories
    updated_count = 0

    for food in all_foods:
        # Ne modifier que si l'index actuel est 5 (par défaut)
        if food.variety_index != 5:
            continue

        category_lower = food.category.lower() if food.category else ""
        name_lower = food.name.lower()

        new_index = None

        # Protéines animales basiques -> 3
        if any(word in category_lower for word in ["viande", "volaille"]):
            if any(word in name_lower for word in ["poulet", "bœuf", "porc", "veau"]):
                new_index = 3

        # Poissons gras ou fruits de mer -> 7
        elif any(word in category_lower for word in ["poisson", "fruits de mer"]):
            if any(word in name_lower for word in ["saumon", "maquereau", "sardine", "hareng", "truite"]):
                new_index = 7
            elif any(word in category_lower for word in ["fruits de mer"]):
                new_index = 8

        # Légumes verts et colorés -> 7
        elif "légume" in category_lower:
            if any(word in name_lower for word in ["brocoli", "épinard", "kale", "chou", "asperge"]):
                new_index = 7
            elif any(word in name_lower for word in ["carotte", "tomate", "laitue", "concombre"]):
                new_index = 4

        # Fruits exotiques -> 8-9
        elif "fruit" in category_lower:
            if any(word in name_lower for word in ["mangue", "papaye", "ananas", "kiwi", "litchi", "passion"]):
                new_index = 8
            elif any(word in name_lower for word in ["pomme", "poire", "banane", "orange"]):
                new_index = 3

        # Céréales complètes -> 7
        elif any(word in category_lower for word in ["céréale", "féculent"]):
            if any(word in name_lower for word in ["complet", "quinoa", "sarrasin", "épeautre"]):
                new_index = 7
            elif any(word in name_lower for word in ["blanc", "riz blanc", "pâtes blanches"]):
                new_index = 2

        # Produits laitiers spéciaux -> 7
        elif any(word in category_lower for word in ["fromage", "lait", "yaourt"]):
            if any(word in name_lower for word in ["chèvre", "brebis", "roquefort", "comté"]):
                new_index = 7
            elif any(word in name_lower for word in ["lait", "yaourt nature"]):
                new_index = 3

        # Huiles et graisses spéciales -> 8
        elif "huile" in category_lower or "graisse" in category_lower:
            if any(word in name_lower for word in ["olive", "coco", "avocat", "lin"]):
                new_index = 8
            elif "tournesol" in name_lower or "colza" in name_lower:
                new_index = 4

        # Appliquer le changement si trouvé
        if new_index and new_index != food.variety_index:
            food.variety_index = new_index
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
        count = auto_enrich_by_category()
        print(f"✅ Enrichissement automatique terminé: {count} aliments modifiés")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
