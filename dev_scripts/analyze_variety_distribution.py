"""
Analyse la distribution actuelle des variety_index et propose des améliorations.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from meal_planner.models.database import DatabaseManager
from meal_planner.config import DATABASE_PATH

def analyze_distribution():
    """Analyse la distribution des variety_index."""
    db = DatabaseManager(DATABASE_PATH)

    print("="*80)
    print(" "*20 + "ANALYSE DE LA DISTRIBUTION DES VARIETY_INDEX")
    print("="*80)
    print()

    all_foods = db.get_all_foods()
    print(f"Total aliments: {len(all_foods)}")
    print()

    # Grouper par variety_index
    by_index = {}
    for food in all_foods:
        idx = food.variety_index
        if idx not in by_index:
            by_index[idx] = []
        by_index[idx].append(food)

    print("Distribution détaillée:")
    print()

    for idx in sorted(by_index.keys()):
        foods = by_index[idx]
        print(f"Variety Index {idx}: {len(foods)} aliments")
        print(f"  Exemples: {', '.join([f.name for f in foods[:5]])}")
        print()

    print("="*80)
    print()

    # Analyser l'impact sur la génération
    print("IMPACT SUR LA GÉNÉRATION:")
    print()

    # Variety level 3
    foods_near_3 = []
    for food in all_foods:
        distance = abs(food.variety_index - 3)
        if distance <= 2:  # Distance acceptable
            foods_near_3.append(food)

    print(f"Variety level 3 -> {len(foods_near_3)} aliments dans la zone (index 1-5)")
    avg_index_3 = sum(f.variety_index for f in foods_near_3) / len(foods_near_3) if foods_near_3 else 0
    print(f"  Index moyen: {avg_index_3:.1f}")
    print()

    # Variety level 9
    foods_near_9 = []
    for food in all_foods:
        distance = abs(food.variety_index - 9)
        if distance <= 2:  # Distance acceptable
            foods_near_9.append(food)

    print(f"Variety level 9 -> {len(foods_near_9)} aliments dans la zone (index 7-10)")
    avg_index_9 = sum(f.variety_index for f in foods_near_9) / len(foods_near_9) if foods_near_9 else 0
    print(f"  Index moyen: {avg_index_9:.1f}")
    print()

    # Diagnostic
    print("="*80)
    print("DIAGNOSTIC:")
    print()

    if len(foods_near_9) < 20:
        print(f"⚠️ PROBLÈME: Seulement {len(foods_near_9)} aliments avec variety_index >= 7")
        print("   -> Impossible d'avoir une vraie différence entre variety_level 3 et 9")
        print("   -> Solution: Reclassifier plus d'aliments vers index 7-9")
    else:
        print(f"✅ OK: {len(foods_near_9)} aliments avec variety_index >= 7")

    print()

    if avg_index_3 > 4:
        print(f"⚠️ PROBLÈME: Index moyen pour variety_level 3 est {avg_index_3:.1f} (trop haut)")
        print("   -> Solution: Reclassifier plus d'aliments basiques vers index 2-3")
    else:
        print(f"✅ OK: Index moyen pour variety_level 3 est {avg_index_3:.1f}")

    print()
    print("="*80)


if __name__ == "__main__":
    analyze_distribution()
