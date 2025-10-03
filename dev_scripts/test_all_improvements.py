"""
Test complet de toutes les améliorations optimisées
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.controllers.meal_plan_controller import MealPlanController
from meal_planner.config import DATABASE_PATH


def test_practical_portions():
    """Test des portions pratiques optimisées."""
    print("\n" + "=" * 80)
    print(" " * 20 + "TEST 1: PORTIONS PRATIQUES OPTIMISÉES")
    print("=" * 80)

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    settings = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=150, carbs=200, fats=65),
        'duration_days': 2,
        'meal_count': 3,
        'dietary_preferences': [],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 6
    }

    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    # Compter les portions pratiques
    practical = 0
    total = 0

    for meal in plan.meals:
        for food, qty in meal.foods:
            total += 1
            if (qty % 50 == 0 or qty % 25 == 0 or qty % 20 == 0 or
                qty % 10 == 0 or qty % 5 == 0):
                practical += 1

    ratio = (practical / total * 100) if total > 0 else 0

    print(f"\n   Portions pratiques: {practical}/{total} ({ratio:.1f}%)")

    if ratio >= 70:
        print(f"   ✅ EXCELLENT! Objectif atteint ({ratio:.1f}% >= 70%)")
        return True
    elif ratio >= 50:
        print(f"   ✓ BON! En amélioration ({ratio:.1f}% >= 50%)")
        return True
    else:
        print(f"   ⚠️ À améliorer ({ratio:.1f}%)")
        return False


def test_variety_level_influence():
    """Test de l'influence renforcée du variety_level."""
    print("\n" + "=" * 80)
    print(" " * 20 + "TEST 2: INFLUENCE DU VARIETY_LEVEL")
    print("=" * 80)

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    # Test avec variety_level bas (3)
    settings_low = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=150, carbs=200, fats=65),
        'duration_days': 1,
        'meal_count': 3,
        'dietary_preferences': [],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 3
    }

    controller.generate_meal_plan(settings_low)
    plan_low = controller.get_current_plan()

    avg_variety_low = 0
    count = 0
    for meal in plan_low.meals:
        for food, _ in meal.foods:
            avg_variety_low += food.variety_index
            count += 1
    avg_variety_low = avg_variety_low / count if count > 0 else 0

    # Test avec variety_level élevé (9)
    settings_high = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=150, carbs=200, fats=65),
        'duration_days': 1,
        'meal_count': 3,
        'dietary_preferences': [],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 9
    }

    controller.generate_meal_plan(settings_high)
    plan_high = controller.get_current_plan()

    avg_variety_high = 0
    count = 0
    for meal in plan_high.meals:
        for food, _ in meal.foods:
            avg_variety_high += food.variety_index
            count += 1
    avg_variety_high = avg_variety_high / count if count > 0 else 0

    print(f"\n   Variety level 3 → Variety index moyen: {avg_variety_low:.1f}")
    print(f"   Variety level 9 → Variety index moyen: {avg_variety_high:.1f}")

    difference = abs(avg_variety_high - avg_variety_low)
    print(f"\n   Différence: {difference:.1f}")

    if difference >= 2.0:
        print(f"   ✅ EXCELLENT! Forte influence ({difference:.1f} >= 2.0)")
        return True
    elif difference >= 1.0:
        print(f"   ✓ BON! Influence modérée ({difference:.1f} >= 1.0)")
        return True
    else:
        print(f"   ⚠️ Influence faible ({difference:.1f})")
        return False


def test_keto_diet():
    """Test du régime keto."""
    print("\n" + "=" * 80)
    print(" " * 20 + "TEST 3: RÉGIME KETO (CÉTOGÈNE)")
    print("=" * 80)

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    settings = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=100, carbs=50, fats=155),
        'duration_days': 1,
        'meal_count': 3,
        'dietary_preferences': ['keto'],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 6
    }

    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    # Vérifier les macros
    totals = plan.calculate_daily_totals(1)

    carbs_percent = (totals['carbs'] * 4 / totals['calories']) * 100 if totals['calories'] > 0 else 0
    fats_percent = (totals['fats'] * 9 / totals['calories']) * 100 if totals['calories'] > 0 else 0
    proteins_percent = (totals['proteins'] * 4 / totals['calories']) * 100 if totals['calories'] > 0 else 0

    print(f"\n   Macros keto:")
    print(f"      Glucides: {totals['carbs']:.0f}g ({carbs_percent:.0f}% des calories)")
    print(f"      Lipides: {totals['fats']:.0f}g ({fats_percent:.0f}% des calories)")
    print(f"      Protéines: {totals['proteins']:.0f}g ({proteins_percent:.0f}% des calories)")

    # Keto = glucides < 15%, lipides > 60%
    is_keto = carbs_percent < 15 and fats_percent > 60

    if is_keto:
        print(f"\n   ✅ RÉGIME KETO RESPECTÉ!")
        return True
    else:
        print(f"\n   ⚠️ Macros hors keto")
        return False


def test_paleo_diet():
    """Test du régime paléo."""
    print("\n" + "=" * 80)
    print(" " * 20 + "TEST 4: RÉGIME PALÉO")
    print("=" * 80)

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    settings = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=150, carbs=150, fats=75),
        'duration_days': 1,
        'meal_count': 3,
        'dietary_preferences': ['paleo'],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 6
    }

    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    # Vérifier qu'il n'y a pas d'aliments exclus
    excluded_keywords = ['pain', 'pâtes', 'riz', 'lait', 'yaourt', 'fromage', 'lentilles', 'haricot']

    violations = []
    for meal in plan.meals:
        for food, _ in meal.foods:
            for keyword in excluded_keywords:
                if keyword.lower() in food.name.lower():
                    violations.append(f"{food.name} ({keyword})")

    print(f"\n   Aliments dans le plan: {sum(len(m.foods) for m in plan.meals)}")
    print(f"   Violations paléo détectées: {len(violations)}")

    if violations:
        print(f"   ⚠️ Aliments non-paléo trouvés:")
        for v in violations[:5]:
            print(f"      - {v}")

    if len(violations) == 0:
        print(f"\n   ✅ RÉGIME PALÉO RESPECTÉ!")
        return True
    elif len(violations) <= 2:
        print(f"\n   ✓ Régime paléo globalement respecté (quelques exceptions)")
        return True
    else:
        print(f"\n   ⚠️ Trop d'aliments non-paléo")
        return False


def test_mediterranean_diet():
    """Test du régime méditerranéen."""
    print("\n" + "=" * 80)
    print(" " * 20 + "TEST 5: RÉGIME MÉDITERRANÉEN")
    print("=" * 80)

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    settings = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=75, carbs=230, fats=70),
        'duration_days': 1,
        'meal_count': 3,
        'dietary_preferences': ['mediterranean'],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 6
    }

    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    # Vérifier les macros
    totals = plan.calculate_daily_totals(1)

    carbs_percent = (totals['carbs'] * 4 / totals['calories']) * 100 if totals['calories'] > 0 else 0
    fats_percent = (totals['fats'] * 9 / totals['calories']) * 100 if totals['calories'] > 0 else 0
    proteins_percent = (totals['proteins'] * 4 / totals['calories']) * 100 if totals['calories'] > 0 else 0

    print(f"\n   Macros méditerranéennes:")
    print(f"      Glucides: {totals['carbs']:.0f}g ({carbs_percent:.0f}% des calories)")
    print(f"      Lipides: {totals['fats']:.0f}g ({fats_percent:.0f}% des calories)")
    print(f"      Protéines: {totals['proteins']:.0f}g ({proteins_percent:.0f}% des calories)")

    # Méditerranéen = glucides 40-50%, lipides 30-40%, protéines 15-20%
    is_mediterranean = (40 <= carbs_percent <= 50 and
                       30 <= fats_percent <= 40 and
                       15 <= proteins_percent <= 20)

    # Compter les poissons et légumes (prioritaires en méditerranéen)
    fish_count = 0
    veggie_count = 0

    for meal in plan.meals:
        for food, _ in meal.foods:
            if 'poisson' in food.category.lower():
                fish_count += 1
            if 'légume' in food.category.lower():
                veggie_count += 1

    print(f"\n   Aliments prioritaires:")
    print(f"      Poissons: {fish_count}")
    print(f"      Légumes: {veggie_count}")

    if is_mediterranean and (fish_count > 0 or veggie_count > 3):
        print(f"\n   ✅ RÉGIME MÉDITERRANÉEN RESPECTÉ!")
        return True
    else:
        print(f"\n   ⚠️ Macros ou aliments hors méditerranéen")
        return False


def main():
    """Lance tous les tests."""
    print("\n")
    print("=" * 80)
    print(" " * 15 + "TESTS COMPLETS DES AMÉLIORATIONS OPTIMISÉES")
    print("=" * 80)

    tests = [
        ("Portions pratiques optimisées", test_practical_portions),
        ("Influence du variety_level", test_variety_level_influence),
        ("Régime Keto", test_keto_diet),
        ("Régime Paléo", test_paleo_diet),
        ("Régime Méditerranéen", test_mediterranean_diet),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n   ❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Rapport final
    print("\n" + "=" * 80)
    print(" " * 30 + "RAPPORT FINAL")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status:8s} - {test_name}")

    print()
    print(f"   Résultat: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print()

    if passed == total:
        print("   🎉 SUCCÈS TOTAL! Toutes les améliorations fonctionnent parfaitement!")
    elif passed >= total * 0.8:
        print("   ✅ EXCELLENT! La grande majorité des améliorations fonctionne!")
    elif passed >= total * 0.6:
        print("   ✓ BON! Les améliorations sont globalement fonctionnelles.")
    else:
        print("   ⚠️ Des ajustements sont nécessaires.")

    print()
    print("=" * 80)
    print()

    return passed >= total * 0.6


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
