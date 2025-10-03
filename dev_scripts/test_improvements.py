"""
Script de test des améliorations du système de génération de plans alimentaires
"""

from pathlib import Path
from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.controllers.meal_plan_controller import MealPlanController
from meal_planner.models.feedback import UserFeedbackSystem
from meal_planner.config import DATABASE_PATH
from meal_planner.data.food_compatibility import calculate_meal_palatability


def test_basic_generation():
    """Test la génération basique."""
    print("="*80)
    print(" "*20 + "TEST 1: GÉNÉRATION BASIQUE")
    print("="*80)
    print()

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    settings = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=150, carbs=200, fats=65),
        'duration_days': 3,
        'meal_count': 3,
        'dietary_preferences': [],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 6
    }

    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    if plan:
        target = settings['nutrition_target']
        valid_count = 0

        for day in range(1, plan.duration_days + 1):
            val = plan.validate_day(day)
            if val['is_valid']:
                valid_count += 1

        print(f"[OK] Plan genere: {len(plan.meals)} repas sur {plan.duration_days} jours")
        print(f"[OK] Jours valides: {valid_count}/{plan.duration_days}")
        print(f"[OK] Ecart calorique moyen: {sum(abs(plan.validate_day(d)['totals']['calories'] - target.calories) for d in range(1, 4)) / 3:.0f} kcal")
        print()
        return True

    return False


def test_food_compatibility():
    """Test la compatibilité alimentaire."""
    print("="*80)
    print(" "*20 + "TEST 2: COMPATIBILITÉ ALIMENTAIRE")
    print("="*80)
    print()

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

    if plan:
        # Analyser la compatibilité de chaque repas
        total_pal_score = 0
        meal_count = 0

        for meal in plan.meals:
            if len(meal.foods) > 1:
                foods = [f.name for f, _ in meal.foods]
                categories = [f.category for f, _ in meal.foods]
                pal_score = calculate_meal_palatability(foods, categories)
                total_pal_score += pal_score
                meal_count += 1

                quality = "Excellent" if pal_score > 0.8 else "Bon" if pal_score > 0.6 else "Acceptable"
                print(f"  {meal.name}: {pal_score:.2f} ({quality})")
                print(f"    -> {', '.join(foods[:3])}")

        avg_score = total_pal_score / meal_count if meal_count > 0 else 0
        print()
        print(f"[OK] Score moyen de palatabilité: {avg_score:.2f}")
        print(f"[OK] Qualité: {'Excellent' if avg_score > 0.75 else 'Bon' if avg_score > 0.65 else 'À améliorer'}")
        print()
        return True

    return False


def test_feedback_system():
    """Test le système de feedback."""
    print("="*80)
    print(" "*20 + "TEST 3: SYSTÈME DE FEEDBACK")
    print("="*80)
    print()

    # Créer un système de feedback de test
    feedback = UserFeedbackSystem(user_id="test_user")
    feedback.clear_all_data()  # Nettoyer les données précédentes

    # Générer un plan
    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    settings = {
        'nutrition_target': NutritionTarget(calories=2000, proteins=150, carbs=200, fats=65),
        'duration_days': 1,
        'meal_count': 3,
        'dietary_preferences': [],
        'price_level': 5,
        'health_index': 7,
        'variety_level': 6
    }

    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    if plan:
        # Simuler des feedbacks
        meals = plan.meals

        # Noter le premier repas positivement
        feedback.record_meal_feedback(meals[0], rating=5.0, followed=True, comments="Excellent!")
        print(f"[OK] Feedback positif enregistré: {meals[0].name} (5/5)")

        # Noter le deuxième repas négativement
        feedback.record_meal_feedback(meals[1], rating=2.0, followed=False, comments="Pas apprécié")
        print(f"[OK] Feedback négatif enregistré: {meals[1].name} (2/5)")

        # Vérifier les préférences apprises
        stats = feedback.get_statistics()
        print()
        print(f"[OK] Statistiques du feedback:")
        print(f"  - Total feedbacks: {stats['total_feedbacks']}")
        print(f"  - Note moyenne: {stats['average_rating']:.1f}/5")
        print(f"  - Préférences enregistrées: {stats['total_food_preferences']}")

        # Afficher les aliments aimés
        liked = feedback.get_top_liked_foods(limit=3)
        if liked:
            print()
            print(f"[OK] Top 3 aliments appréciés:")
            for pref in liked:
                print(f"  - {pref.food_name}: score {pref.preference_score:.2f}")

        print()
        return True

    return False


def test_multi_objective_optimization():
    """Test l'optimisation multi-objectifs (plusieurs tentatives)."""
    print("="*80)
    print(" "*20 + "TEST 4: OPTIMISATION MULTI-OBJECTIFS")
    print("="*80)
    print()

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    # Tester avec différents objectifs
    scenarios = [
        ("Prise de masse", NutritionTarget(calories=3000, proteins=200, carbs=350, fats=80)),
        ("Sèche", NutritionTarget(calories=1500, proteins=130, carbs=120, fats=50)),
        ("Entretien", NutritionTarget(calories=2000, proteins=150, carbs=200, fats=65)),
    ]

    results = []

    for name, target in scenarios:
        settings = {
            'nutrition_target': target,
            'duration_days': 1,
            'meal_count': 3,
            'dietary_preferences': [],
            'price_level': 5,
            'health_index': 7,
            'variety_level': 6
        }

        controller.generate_meal_plan(settings)
        plan = controller.get_current_plan()

        if plan:
            val = plan.validate_day(1)
            tot = val['totals']

            cal_ecart = abs(tot['calories'] - target.calories) / target.calories * 100
            prot_ecart = abs(tot['proteins'] - target.proteins) / target.proteins * 100

            results.append({
                'scenario': name,
                'cal_ecart': cal_ecart,
                'prot_ecart': prot_ecart,
                'valid': val['is_valid']
            })

            status = "[OK]" if val['is_valid'] else "[o]"
            print(f"{status} {name:15s}: {tot['calories']:.0f}/{target.calories} kcal "
                  f"({cal_ecart:.1f}%), P: {tot['proteins']:.0f}g ({prot_ecart:.1f}%)")

    print()
    avg_cal_ecart = sum(r['cal_ecart'] for r in results) / len(results)
    avg_prot_ecart = sum(r['prot_ecart'] for r in results) / len(results)
    valid_count = sum(1 for r in results if r['valid'])

    print(f"[OK] Résultats globaux:")
    print(f"  - Scénarios valides: {valid_count}/{len(results)}")
    print(f"  - Écart calorique moyen: {avg_cal_ecart:.1f}%")
    print(f"  - Écart protéines moyen: {avg_prot_ecart:.1f}%")
    print()

    return avg_cal_ecart < 3.0 and avg_prot_ecart < 10.0


def main():
    """Lance tous les tests."""
    print("\n")
    print("=" * 80)
    print(" " * 10 + "TESTS DES AMELIORATIONS DU SYSTEME DE MEAL PLANNING")
    print("=" * 80)
    print()

    tests = [
        ("Génération basique", test_basic_generation),
        ("Compatibilité alimentaire", test_food_compatibility),
        ("Système de feedback", test_feedback_system),
        ("Optimisation multi-objectifs", test_multi_objective_optimization),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"[X] ERREUR dans {test_name}: {e}")
            results.append((test_name, False))

    # Rapport final
    print()
    print("="*80)
    print(" "*25 + "RAPPORT FINAL")
    print("="*80)
    print()

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "[OK] PASS" if success else "[X] FAIL"
        print(f"{status:8s} - {test_name}")

    print()
    print(f"Résultat: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print()

    if passed == total:
        print("[SUCCESS] TOUTES LES AMÉLIORATIONS FONCTIONNENT PARFAITEMENT!")
    elif passed >= total * 0.75:
        print("[OK] Améliorations fonctionnelles avec quelques ajustements nécessaires")
    else:
        print("[!] Certaines améliorations nécessitent des corrections")

    print()
    print("="*80)
    print()


if __name__ == "__main__":
    main()
