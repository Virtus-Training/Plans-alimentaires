"""
Analyse détaillée des cas d'échec pour atteindre 100% de fiabilité
"""

from pathlib import Path
from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.services.meal_generators import FoodBasedGenerator
from meal_planner.config import DATABASE_PATH
from meal_planner.data.meal_coherence_rules import is_starch_food


def analyze_carb_failures():
    """Analyse pourquoi les glucides dépassent encore"""
    print("\n" + "="*70)
    print("ANALYSE DES ÉCHECS GLUCIDES")
    print("="*70)

    db_manager = DatabaseManager(DATABASE_PATH)
    foods = db_manager.get_all_foods()

    # Profil faible glucides (le plus problématique)
    target = NutritionTarget(calories=2000, proteins=150, carbs=100, fats=100)

    generator = FoodBasedGenerator(
        available_foods=foods,
        nutrition_target=target,
        tolerance=0.10,
        use_ilp=False
    )

    print(f"\nProfil: Faible glucides (cible: 100g glucides)")
    print(f"Aliments disponibles: {len(foods)}")

    # Analyser les aliments par ratio glucides/calories
    high_carb_foods = []
    for food in foods:
        if food.calories > 0:
            carb_ratio = (food.carbs * 4) / food.calories  # % calories from carbs
            if carb_ratio > 0.5:  # Plus de 50% des calories viennent des glucides
                high_carb_foods.append((food.name, food.category, food.carbs, carb_ratio))

    high_carb_foods.sort(key=lambda x: x[3], reverse=True)

    print(f"\n[!] Aliments a >50% de glucides: {len(high_carb_foods)}/{len(foods)}")
    print(f"\nTop 10 aliments les plus riches en glucides (% calories):")
    for name, cat, carbs, ratio in high_carb_foods[:10]:
        print(f"  - {name} ({cat}): {carbs:.1f}g/100g ({ratio*100:.0f}% calories)")

    # Générer quelques repas et voir lesquels posent problème
    print(f"\n\nTest génération de 10 repas:")
    total_carbs_violations = 0

    for i in range(10):
        generator.reset_used_foods()
        generator.daily_accumulated_calories = 0.0

        # Générer un déjeuner (40% des calories)
        meal = generator.generate_meal("lunch", i+1, 0.40)
        macros = meal.calculate_macros()

        meal_target_carbs = 100 * 0.40  # 40g
        actual_carbs = macros['carbs']
        deviation = (actual_carbs - meal_target_carbs) / meal_target_carbs * 100

        if deviation > 20:
            total_carbs_violations += 1
            print(f"\n  [X] Repas {i+1}: {actual_carbs:.1f}g glucides (cible: {meal_target_carbs:.1f}g, ecart: +{deviation:.0f}%)")
            print(f"     Composition:")
            for food, qty in meal.foods:
                food_carbs = food.calculate_for_quantity(qty)['carbs']
                print(f"       - {food.name}: {qty:.0f}g -> {food_carbs:.1f}g glucides")
        else:
            print(f"  [OK] Repas {i+1}: {actual_carbs:.1f}g glucides (cible: {meal_target_carbs:.1f}g, ecart: {deviation:+.0f}%)")

    print(f"\n\n[STATS] Taux de violation: {total_carbs_violations}/10 ({total_carbs_violations*10}%)")


def analyze_starch_failures():
    """Analyse pourquoi certains repas ont encore 2 féculents"""
    print("\n" + "="*70)
    print("ANALYSE DES VIOLATIONS FÉCULENTS")
    print("="*70)

    db_manager = DatabaseManager(DATABASE_PATH)
    foods = db_manager.get_all_foods()

    # Profil végétarien (le plus problématique)
    target = NutritionTarget(calories=1800, proteins=120, carbs=220, fats=60)

    generator = FoodBasedGenerator(
        available_foods=foods,
        nutrition_target=target,
        tolerance=0.10,
        use_ilp=False
    )

    print(f"\nProfil: Végétarien (le plus problématique)")

    # Identifier tous les féculents disponibles
    starches = []
    for food in foods:
        if is_starch_food(food.category, food.name):
            starches.append((food.name, food.category))

    print(f"\nFéculents disponibles: {len(starches)}")
    print("Liste:")
    for name, cat in sorted(starches):
        print(f"  - {name} ({cat})")

    # Générer 30 repas et analyser les violations
    print(f"\n\nTest génération de 30 repas:")
    violations = []

    for i in range(30):
        generator.reset_used_foods()
        generator.daily_accumulated_calories = 0.0

        # Alterner entre lunch et dinner
        meal_type = "lunch" if i % 2 == 0 else "dinner"
        meal = generator.generate_meal(meal_type, i//2 + 1, 0.40)

        # Compter les féculents
        meal_starches = []
        for food, qty in meal.foods:
            if is_starch_food(food.category, food.name):
                meal_starches.append((food.name, qty))

        if len(meal_starches) > 1:
            violations.append({
                'meal_num': i+1,
                'meal_type': meal_type,
                'starches': meal_starches,
                'all_foods': [(f.name, q) for f, q in meal.foods]
            })
            print(f"\n  [X] Repas {i+1} ({meal_type}): {len(meal_starches)} féculents")
            for name, qty in meal_starches:
                print(f"       - {name}: {qty:.0f}g")
        else:
            status = "[OK]" if len(meal_starches) == 1 else "[i]"
            print(f"  {status} Repas {i+1} ({meal_type}): {len(meal_starches)} féculent(s)")

    print(f"\n\n[STATS] Violations: {len(violations)}/30 ({len(violations)/30*100:.1f}%)")

    if violations:
        print(f"\n\nAnalyse des violations:")
        for v in violations:
            print(f"\n  Repas {v['meal_num']} - {v['meal_type']}:")
            print(f"    Féculents: {', '.join([f'{n} ({q:.0f}g)' for n, q in v['starches']])}")


def analyze_snack_failures():
    """Analyse pourquoi les collations dépassent encore"""
    print("\n" + "="*70)
    print("ANALYSE DES DÉPASSEMENTS COLLATIONS")
    print("="*70)

    db_manager = DatabaseManager(DATABASE_PATH)
    foods = db_manager.get_all_foods()

    target = NutritionTarget(calories=2000, proteins=150, carbs=200, fats=67)

    generator = FoodBasedGenerator(
        available_foods=foods,
        nutrition_target=target,
        tolerance=0.10,
        use_ilp=False
    )

    print(f"\nTest génération de 20 collations:")
    print(f"Cible: 5% des 2000 kcal = 100 kcal")

    violations = []

    for i in range(20):
        generator.reset_used_foods()
        generator.daily_accumulated_calories = 0.0

        # Générer une collation
        snack = generator.generate_meal("snack", i+1, 0.05)
        macros = snack.calculate_macros()

        target_cal = 100
        actual_cal = macros['calories']
        deviation = (actual_cal - target_cal) / target_cal * 100

        if deviation > 50:  # Plus de 50% d'écart
            violations.append({
                'num': i+1,
                'calories': actual_cal,
                'target': target_cal,
                'deviation': deviation,
                'num_foods': len(snack.foods),
                'foods': [(f.name, q, f.calculate_for_quantity(q)['calories']) for f, q in snack.foods]
            })
            print(f"\n  [X] Collation {i+1}: {actual_cal:.0f} kcal (cible: {target_cal:.0f}, écart: +{deviation:.0f}%)")
            print(f"     {len(snack.foods)} aliments:")
            for name, qty, cal in violations[-1]['foods']:
                print(f"       - {name}: {qty:.0f}g ({cal:.0f} kcal)")
        else:
            print(f"  [OK] Collation {i+1}: {actual_cal:.0f} kcal (écart: {deviation:+.0f}%)")

    print(f"\n\n[STATS] Violations (>50% écart): {len(violations)}/20 ({len(violations)/20*100:.0f}%)")

    if violations:
        avg_foods = sum(v['num_foods'] for v in violations) / len(violations)
        print(f"\nMoyenne d'aliments dans violations: {avg_foods:.1f}")


def main():
    """Point d'entrée"""
    print("="*70)
    print("ANALYSE DÉTAILLÉE DES CAS D'ÉCHEC")
    print("Objectif: Atteindre 100% de fiabilité")
    print("="*70)

    analyze_carb_failures()
    analyze_starch_failures()
    analyze_snack_failures()

    print("\n" + "="*70)
    print("FIN DE L'ANALYSE")
    print("="*70)


if __name__ == "__main__":
    main()
