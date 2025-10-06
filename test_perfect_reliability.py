"""
Test de fiabilité parfaite - 100 repas
Objectif: 0 violation sur tous les critères
"""

from pathlib import Path
from collections import defaultdict
from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.services.meal_generators import FoodBasedGenerator
from meal_planner.config import DATABASE_PATH
from meal_planner.data.meal_coherence_rules import is_starch_food


def test_perfect_reliability(num_meals=100):
    """Test de fiabilité sur un grand nombre de repas"""

    print("="*70)
    print("TEST DE FIABILITE PARFAITE - 100 REPAS")
    print("="*70)

    db_manager = DatabaseManager(DATABASE_PATH)
    foods = db_manager.get_all_foods()

    # Profils à tester
    profiles = [
        ("Standard", NutritionTarget(2000, 150, 200, 67)),
        ("Haute proteine", NutritionTarget(2000, 180, 150, 70)),
        ("Faible glucides", NutritionTarget(2000, 150, 100, 100)),
        ("Vegetarien", NutritionTarget(1800, 120, 220, 60)),
        ("Gain musculaire", NutritionTarget(2500, 200, 250, 80)),
    ]

    results = {
        'total_meals': 0,
        'starch_violations': 0,
        'carb_violations': 0,
        'calorie_violations': 0,
        'protein_violations': 0,
        'snack_violations': 0,
        'details': defaultdict(list)
    }

    meals_per_profile = num_meals // len(profiles)

    for profile_name, target in profiles:
        print(f"\nTest profil: {profile_name}")
        print(f"  Cible: {target.calories} kcal, P:{target.proteins}g, C:{target.carbs}g, L:{target.fats}g")

        generator = FoodBasedGenerator(
            available_foods=foods,
            nutrition_target=target,
            tolerance=0.10,
            use_ilp=False
        )

        profile_violations = {
            'starch': 0,
            'carbs': 0,
            'calories': 0,
            'proteins': 0,
            'snacks': 0
        }

        for i in range(meals_per_profile):
            results['total_meals'] += 1
            generator.reset_used_foods()
            generator.daily_accumulated_calories = 0.0

            # Alterner entre différents types de repas
            meal_types = [
                ("breakfast", 0.25),
                ("lunch", 0.40),
                ("dinner", 0.35),
                ("snack", 0.05)
            ]
            meal_type, target_pct = meal_types[i % 4]

            meal = generator.generate_meal(meal_type, i // 4 + 1, target_pct)
            macros = meal.calculate_macros()

            # Vérification 1: Féculents (CRITIQUE)
            starches = [f for f, _ in meal.foods if is_starch_food(f.category, f.name)]
            if len(starches) > 1:
                results['starch_violations'] += 1
                profile_violations['starch'] += 1
                results['details']['starch'].append({
                    'profile': profile_name,
                    'meal_type': meal_type,
                    'starches': [f.name for f in starches]
                })

            # Vérification 2: Glucides
            target_carbs = target.carbs * target_pct
            carb_deviation = abs(macros['carbs'] - target_carbs) / target_carbs
            if carb_deviation > 0.30:  # Tolérance 30%
                results['carb_violations'] += 1
                profile_violations['carbs'] += 1

            # Vérification 3: Calories
            target_cals = target.calories * target_pct
            cal_deviation = abs(macros['calories'] - target_cals) / target_cals
            if cal_deviation > 0.15:  # Tolérance 15%
                results['calorie_violations'] += 1
                profile_violations['calories'] += 1

            # Vérification 4: Protéines
            target_prots = target.proteins * target_pct
            prot_deviation = abs(macros['proteins'] - target_prots) / target_prots
            if prot_deviation > 0.20:  # Tolérance 20%
                results['protein_violations'] += 1
                profile_violations['proteins'] += 1

            # Vérification 5: Collations (plus strict)
            if "snack" in meal_type.lower():
                snack_deviation = abs(macros['calories'] - target_cals) / target_cals
                if snack_deviation > 0.60:  # Tolérance 60% pour snacks
                    results['snack_violations'] += 1
                    profile_violations['snacks'] += 1

        # Afficher résultats du profil
        total_profile_violations = sum(profile_violations.values())
        conformity = (meals_per_profile - total_profile_violations) / meals_per_profile * 100

        print(f"  Repas testes: {meals_per_profile}")
        print(f"  Conformite: {conformity:.1f}%")
        if total_profile_violations > 0:
            print(f"  Violations:")
            for vtype, count in profile_violations.items():
                if count > 0:
                    print(f"    - {vtype}: {count}")

    # Résultats globaux
    print("\n" + "="*70)
    print("RESULTATS GLOBAUX")
    print("="*70)
    print(f"\nTotal repas testes: {results['total_meals']}")

    total_violations = (
        results['starch_violations'] +
        results['carb_violations'] +
        results['calorie_violations'] +
        results['protein_violations'] +
        results['snack_violations']
    )

    global_conformity = (results['total_meals'] - total_violations) / results['total_meals'] * 100

    print(f"\nTaux de conformite global: {global_conformity:.1f}%")
    print(f"\nViolations par critere:")
    print(f"  Feculents (>1 par repas): {results['starch_violations']}/{results['total_meals']} ({results['starch_violations']/results['total_meals']*100:.1f}%)")
    print(f"  Glucides (>30% ecart): {results['carb_violations']}/{results['total_meals']} ({results['carb_violations']/results['total_meals']*100:.1f}%)")
    print(f"  Calories (>15% ecart): {results['calorie_violations']}/{results['total_meals']} ({results['calorie_violations']/results['total_meals']*100:.1f}%)")
    print(f"  Proteines (>20% ecart): {results['protein_violations']}/{results['total_meals']} ({results['protein_violations']/results['total_meals']*100:.1f}%)")
    print(f"  Collations (>60% ecart): {results['snack_violations']}/{results['total_meals']//4} ({results['snack_violations']/(results['total_meals']//4)*100:.1f}%)")

    # Détails des violations féculents
    if results['details']['starch']:
        print(f"\nDetails violations feculents ({len(results['details']['starch'])} cas):")
        for v in results['details']['starch'][:5]:  # Afficher 5 premiers
            print(f"  - {v['profile']} / {v['meal_type']}: {', '.join(v['starches'])}")

    # Score final
    print("\n" + "="*70)
    if global_conformity >= 99.0:
        print("RESULTAT: FIABILITE PARFAITE [OK] (>99%)")
        score = 10.0
    elif global_conformity >= 95.0:
        print("RESULTAT: EXCELLENT [OK] (95-99%)")
        score = 9.0
    elif global_conformity >= 90.0:
        print("RESULTAT: TRES BON [OK] (90-95%)")
        score = 8.0
    else:
        print("RESULTAT: AMELIORATION NECESSAIRE (<90%)")
        score = 7.0

    print(f"Score final: {score}/10")
    print("="*70)

    return results, global_conformity


if __name__ == "__main__":
    results, conformity = test_perfect_reliability(100)
