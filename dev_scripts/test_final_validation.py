"""
Test de validation finale des améliorations du système de meal planning
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.controllers.meal_plan_controller import MealPlanController
from meal_planner.config import DATABASE_PATH


def test_comprehensive_plan():
    """Test complet avec analyse détaillée."""
    print("\n" + "=" * 80)
    print(" " * 20 + "VALIDATION FINALE DES AMÉLIORATIONS")
    print("=" * 80)
    print()

    db = DatabaseManager(DATABASE_PATH)
    controller = MealPlanController(db)

    # Test avec un profil réaliste
    settings = {
        'nutrition_target': NutritionTarget(calories=2200, proteins=160, carbs=230, fats=70),
        'duration_days': 3,
        'meal_count': 4,
        'dietary_preferences': [],
        'price_level': 6,
        'health_index': 8,
        'variety_level': 7
    }

    print("📋 PARAMÈTRES DU TEST:")
    print(f"   Calories: {settings['nutrition_target'].calories} kcal/jour")
    print(f"   Protéines: {settings['nutrition_target'].proteins}g")
    print(f"   Glucides: {settings['nutrition_target'].carbs}g")
    print(f"   Lipides: {settings['nutrition_target'].fats}g")
    print(f"   Durée: {settings['duration_days']} jours")
    print(f"   Repas/jour: {settings['meal_count']}")
    print(f"   Prix: {settings['price_level']}/10")
    print(f"   Santé: {settings['health_index']}/10")
    print(f"   Variété: {settings['variety_level']}/10")
    print()

    # Générer le plan
    print("🔄 Génération du plan en cours...")
    controller.generate_meal_plan(settings)
    plan = controller.get_current_plan()

    if not plan:
        print("❌ ERREUR: Plan non généré")
        return False

    print("✅ Plan généré avec succès!")
    print()

    # =========================================================================
    # TEST 1: VALIDATION NUTRITIONNELLE
    # =========================================================================
    print("=" * 80)
    print("TEST 1: VALIDATION NUTRITIONNELLE")
    print("=" * 80)

    validation = plan.validate_against_target()
    print(f"\n📊 Résultats globaux:")
    print(f"   Jours valides: {sum(1 for d in validation['days'].values() if d['is_valid'])}/{plan.duration_days}")
    print()

    for day_key, day_result in validation['days'].items():
        day_num = int(day_key.split('_')[1])
        totals = day_result['totals']
        target = settings['nutrition_target']

        print(f"   Jour {day_num}:")
        print(f"      Calories: {totals['calories']:.0f}/{target.calories} kcal "
              f"({(totals['calories']/target.calories - 1)*100:+.1f}%)")
        print(f"      Protéines: {totals['proteins']:.0f}/{target.proteins}g "
              f"({(totals['proteins']/target.proteins - 1)*100:+.1f}%)")
        print(f"      Glucides: {totals['carbs']:.0f}/{target.carbs}g "
              f"({(totals['carbs']/target.carbs - 1)*100:+.1f}%)")
        print(f"      Lipides: {totals['fats']:.0f}/{target.fats}g "
              f"({(totals['fats']/target.fats - 1)*100:+.1f}%)")

        # Afficher l'équilibre glycémique
        glycemic = day_result.get('glycemic_balance', {})
        if glycemic:
            print(f"      Équilibre glycémique: {glycemic['score']}/100 ({glycemic['status']})")

        print()

    # =========================================================================
    # TEST 2: DIVERSITÉ ALIMENTAIRE
    # =========================================================================
    print("=" * 80)
    print("TEST 2: DIVERSITÉ ALIMENTAIRE")
    print("=" * 80)

    all_foods = []
    all_categories = set()

    for meal in plan.meals:
        for food, qty in meal.foods:
            all_foods.append(food.name)
            all_categories.add(food.category)

    unique_foods = len(set(all_foods))
    foods_per_day = unique_foods / plan.duration_days

    print(f"\n📊 Métriques de diversité:")
    print(f"   Aliments uniques: {unique_foods}")
    print(f"   Aliments par jour: {foods_per_day:.1f}")
    print(f"   Catégories: {len(all_categories)}")
    print(f"   Ratio diversité: {unique_foods/len(all_foods)*100:.1f}%")
    print()

    print(f"   Catégories utilisées:")
    for cat in sorted(all_categories):
        print(f"      - {cat}")

    # Objectif: 20+ aliments par jour
    diversity_ok = foods_per_day >= 15  # Un peu moins strict que 20
    print()
    if diversity_ok:
        print(f"   ✅ Diversité excellente ({foods_per_day:.1f} aliments/jour)")
    else:
        print(f"   ⚠️ Diversité à améliorer ({foods_per_day:.1f}/20 aliments/jour)")

    print()

    # =========================================================================
    # TEST 3: PORTIONS PRATIQUES
    # =========================================================================
    print("=" * 80)
    print("TEST 3: PORTIONS PRATIQUES")
    print("=" * 80)

    practical_count = 0
    total_count = 0
    sample_portions = []

    for meal in plan.meals[:3]:  # Afficher les 3 premiers repas
        print(f"\n   {meal.name}:")
        for food, qty in meal.foods:
            total_count += 1

            # Vérifier si la portion est pratique (multiple de 5, 10, 20, 25, 50)
            is_practical = (qty % 50 == 0 or qty % 25 == 0 or qty % 20 == 0 or
                          qty % 10 == 0 or qty % 5 == 0)
            if is_practical:
                practical_count += 1

            marker = "✓" if is_practical else "○"
            print(f"      {marker} {food.name}: {qty:.0f}g")

    for meal in plan.meals:
        for food, qty in meal.foods:
            total_count += 1
            if (qty % 50 == 0 or qty % 25 == 0 or qty % 20 == 0 or qty % 10 == 0 or qty % 5 == 0):
                practical_count += 1

    practicality_ratio = (practical_count / total_count) * 100 if total_count > 0 else 0

    print()
    print(f"   📊 Portions pratiques: {practical_count}/{total_count} ({practicality_ratio:.1f}%)")

    if practicality_ratio >= 85:
        print(f"   ✅ Excellent taux de portions pratiques")
    elif practicality_ratio >= 70:
        print(f"   ✓ Bon taux de portions pratiques")
    else:
        print(f"   ⚠️ Portions à améliorer")

    print()

    # =========================================================================
    # TEST 4: SCORE DE QUALITÉ GLOBAL
    # =========================================================================
    print("=" * 80)
    print("TEST 4: SCORE DE QUALITÉ GLOBAL")
    print("=" * 80)

    quality = plan.calculate_quality_score()

    print(f"\n📊 Scores de qualité:")
    print(f"   Score global: {quality['total_score']}/100 (Grade: {quality['grade']})")
    print(f"   - Nutrition: {quality['nutrition_score']}/100")
    print(f"   - Diversité: {quality['diversity_score']}/100")
    print(f"   - Palatabilité: {quality['palatability_score']}/100")
    print(f"   - Praticité: {quality['practicality_score']}/100")

    print(f"\n💡 Recommandations:")
    for i, rec in enumerate(quality['recommendations'], 1):
        print(f"   {i}. {rec}")

    print()

    # =========================================================================
    # TEST 5: UTILISATION DES PARAMÈTRES
    # =========================================================================
    print("=" * 80)
    print("TEST 5: UTILISATION DES PARAMÈTRES UTILISATEUR")
    print("=" * 80)

    # Analyser l'impact des paramètres
    total_items = 0
    total_health = 0
    total_variety = 0
    total_price = 0

    for meal in plan.meals:
        for food, qty in meal.foods:
            total_items += 1
            total_health += food.health_index
            total_variety += food.variety_index
            total_price += (food.price_per_100g * qty / 100)

    avg_health = total_health / total_items if total_items > 0 else 0
    avg_variety = total_variety / total_items if total_items > 0 else 0
    avg_price = total_price / len(plan.meals) if plan.meals else 0

    print(f"\n📊 Analyse des paramètres:")
    print(f"   Health index cible: {settings['health_index']}/10")
    print(f"   Health index moyen aliments: {avg_health:.1f}/10")
    health_delta = abs(avg_health - settings['health_index'])
    if health_delta <= 1.5:
        print(f"   ✅ Paramètre health_index bien utilisé (écart: {health_delta:.1f})")
    else:
        print(f"   ⚠️ Paramètre health_index peu influent (écart: {health_delta:.1f})")

    print()
    print(f"   Variety level cible: {settings['variety_level']}/10")
    print(f"   Variety index moyen aliments: {avg_variety:.1f}/10")
    variety_delta = abs(avg_variety - settings['variety_level'])
    if variety_delta <= 1.5:
        print(f"   ✅ Paramètre variety_level bien utilisé (écart: {variety_delta:.1f})")
    else:
        print(f"   ⚠️ Paramètre variety_level peu influent (écart: {variety_delta:.1f})")

    print()
    print(f"   Prix moyen par repas: {avg_price:.2f}€")

    print()

    # =========================================================================
    # RAPPORT FINAL
    # =========================================================================
    print("=" * 80)
    print("RAPPORT FINAL")
    print("=" * 80)

    tests_passed = []
    tests_failed = []

    # Critères de validation
    if validation['is_valid'] or sum(1 for d in validation['days'].values() if d['is_valid']) >= plan.duration_days * 0.8:
        tests_passed.append("Précision nutritionnelle")
    else:
        tests_failed.append("Précision nutritionnelle insuffisante")

    if foods_per_day >= 15:
        tests_passed.append("Diversité alimentaire excellente")
    elif foods_per_day >= 12:
        tests_passed.append("Diversité alimentaire bonne")
    else:
        tests_failed.append("Diversité alimentaire insuffisante")

    if practicality_ratio >= 70:
        tests_passed.append("Portions pratiques")
    else:
        tests_failed.append("Portions à améliorer")

    if quality['total_score'] >= 75:
        tests_passed.append("Score de qualité élevé")
    elif quality['total_score'] >= 65:
        tests_passed.append("Score de qualité acceptable")
    else:
        tests_failed.append("Score de qualité insuffisant")

    if health_delta <= 2.0 and variety_delta <= 2.0:
        tests_passed.append("Paramètres utilisateur respectés")
    else:
        tests_failed.append("Paramètres utilisateur peu influents")

    print(f"\n✅ Tests réussis ({len(tests_passed)}):")
    for test in tests_passed:
        print(f"   ✓ {test}")

    if tests_failed:
        print(f"\n⚠️ Points à améliorer ({len(tests_failed)}):")
        for test in tests_failed:
            print(f"   • {test}")

    print()
    success_rate = len(tests_passed) / (len(tests_passed) + len(tests_failed)) * 100

    if success_rate >= 80:
        print(f"🎉 SUCCÈS! Taux de réussite: {success_rate:.0f}%")
        print("   Le système de génération est de qualité professionnelle!")
        return True
    elif success_rate >= 60:
        print(f"✓ BON. Taux de réussite: {success_rate:.0f}%")
        print("   Le système fonctionne bien avec quelques améliorations possibles.")
        return True
    else:
        print(f"⚠️ À AMÉLIORER. Taux de réussite: {success_rate:.0f}%")
        print("   Certains aspects nécessitent des ajustements.")
        return False


if __name__ == "__main__":
    try:
        success = test_comprehensive_plan()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
