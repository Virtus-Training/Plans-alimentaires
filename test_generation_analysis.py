"""
Script de test pour générer et analyser plusieurs plans alimentaires
Comparaison avec des standards professionnels
"""

import json
from pathlib import Path
from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.services.meal_generators import FoodBasedGenerator, MealDistribution
from meal_planner.models.meal_plan import MealPlan
from collections import defaultdict


def analyze_meal_composition(meal):
    """Analyse la composition d'un repas."""
    categories = defaultdict(float)
    total_weight = 0

    for food, qty in meal.foods:
        categories[food.category] += qty
        total_weight += qty

    macros = meal.calculate_macros()

    return {
        "name": meal.name,
        "num_foods": len(meal.foods),
        "total_weight": total_weight,
        "categories": dict(categories),
        "macros": macros,
        "foods_detail": [(food.name, qty, food.unit_weight) for food, qty in meal.foods]
    }


def analyze_meal_plan(meal_plan):
    """Analyse complète d'un plan alimentaire."""
    print(f"\n{'='*80}")
    print(f"ANALYSE DU PLAN: {meal_plan.nutrition_target.calories:.0f} kcal/jour")
    print(f"{'='*80}")

    daily_analyses = {}

    for day in range(1, meal_plan.duration_days + 1):
        print(f"\n--- JOUR {day} ---")
        day_meals = meal_plan.get_meals_for_day(day)
        day_totals = meal_plan.calculate_daily_totals(day)

        print(f"\nTotal jour: {day_totals['calories']:.0f} kcal | "
              f"P: {day_totals['proteins']:.1f}g | "
              f"C: {day_totals['carbs']:.1f}g | "
              f"F: {day_totals['fats']:.1f}g | "
              f"Fibres: {day_totals['fibers']:.1f}g")

        meal_analyses = []
        for meal in day_meals:
            analysis = analyze_meal_composition(meal)
            meal_analyses.append(analysis)

            print(f"\n  {analysis['name']}:")
            print(f"    Aliments ({analysis['num_foods']}): ", end="")
            for food_name, qty, unit_weight in analysis['foods_detail']:
                unit_info = f" ({unit_weight}g/unité)" if unit_weight else ""
                print(f"\n      - {food_name}: {qty:.0f}g{unit_info}", end="")

            print(f"\n    Macros: {analysis['macros']['calories']:.0f} kcal | "
                  f"P: {analysis['macros']['proteins']:.1f}g | "
                  f"C: {analysis['macros']['carbs']:.1f}g | "
                  f"F: {analysis['macros']['fats']:.1f}g")

        daily_analyses[f"day_{day}"] = {
            "totals": day_totals,
            "meals": meal_analyses
        }

    # Validation
    validation = meal_plan.validate_against_target()
    quality = meal_plan.calculate_quality_score()

    print(f"\n{'='*80}")
    print("SCORES DE QUALITÉ")
    print(f"{'='*80}")
    print(f"Score global: {quality['total_score']:.1f}/100 (Grade: {quality['grade']})")
    print(f"  - Nutrition: {quality['nutrition_score']:.1f}/100")
    print(f"  - Diversité: {quality['diversity_score']:.1f}/100")
    print(f"  - Palatabilité: {quality['palatability_score']:.1f}/100")
    print(f"  - Praticité: {quality['practicality_score']:.1f}/100")

    print(f"\nRecommandations:")
    for rec in quality['recommendations']:
        print(f"  - {rec}")

    print(f"\nValidation: {'[OK] VALIDE' if validation['is_valid'] else '[ERREUR] INVALIDE'}")

    return {
        "target": meal_plan.nutrition_target.to_dict(),
        "daily_analyses": daily_analyses,
        "validation": validation,
        "quality": quality
    }


def compare_with_professional_standards(analysis):
    """Compare avec les standards professionnels (MyFitnessPal, Yazio)."""
    print(f"\n{'='*80}")
    print("COMPARAISON AVEC STANDARDS PROFESSIONNELS")
    print(f"{'='*80}")

    issues = []

    # 1. Nombre d'aliments par repas
    print("\n1. NOMBRE D'ALIMENTS PAR REPAS")
    print("   Standard professionnel:")
    print("   - Petit-déjeuner: 3-5 aliments")
    print("   - Déjeuner/Dîner: 4-7 aliments")
    print("   - Collations: 1-3 aliments")

    print("\n   Notre génération:")
    for day_key, day_data in analysis['daily_analyses'].items():
        for meal in day_data['meals']:
            num_foods = meal['num_foods']
            meal_name = meal['name']

            if 'Petit-dejeuner' in meal_name or 'breakfast' in meal_name.lower():
                if not (3 <= num_foods <= 5):
                    issues.append(f"   [X] {meal_name}: {num_foods} aliments (hors norme 3-5)")
                else:
                    print(f"   [OK] {meal_name}: {num_foods} aliments")
            elif 'Collation' in meal_name or 'snack' in meal_name.lower() or 'Gouter' in meal_name:
                if not (1 <= num_foods <= 3):
                    issues.append(f"   [X] {meal_name}: {num_foods} aliments (hors norme 1-3)")
                else:
                    print(f"   [OK] {meal_name}: {num_foods} aliments")
            else:  # Déjeuner/Dîner
                if not (4 <= num_foods <= 7):
                    issues.append(f"   [X] {meal_name}: {num_foods} aliments (hors norme 4-7)")
                else:
                    print(f"   [OK] {meal_name}: {num_foods} aliments")

    # 2. Répartition des macros
    print("\n2. RÉPARTITION DES MACRONUTRIMENTS")
    print("   Standard professionnel:")
    print("   - Protéines: 15-30% des calories")
    print("   - Glucides: 45-65% des calories")
    print("   - Lipides: 20-35% des calories")

    for day_key, day_data in analysis['daily_analyses'].items():
        totals = day_data['totals']
        total_cal = totals['calories']

        if total_cal > 0:
            protein_pct = (totals['proteins'] * 4 / total_cal) * 100
            carbs_pct = (totals['carbs'] * 4 / total_cal) * 100
            fats_pct = (totals['fats'] * 9 / total_cal) * 100

            print(f"\n   {day_key}:")
            print(f"   - Proteines: {protein_pct:.1f}% ", end="")
            if 15 <= protein_pct <= 30:
                print("[OK]")
            else:
                print("[X] (hors norme)")
                issues.append(f"   {day_key}: Proteines {protein_pct:.1f}% hors norme")

            print(f"   - Glucides: {carbs_pct:.1f}% ", end="")
            if 45 <= carbs_pct <= 65:
                print("[OK]")
            else:
                print("[X] (hors norme)")
                issues.append(f"   {day_key}: Glucides {carbs_pct:.1f}% hors norme")

            print(f"   - Lipides: {fats_pct:.1f}% ", end="")
            if 20 <= fats_pct <= 35:
                print("[OK]")
            else:
                print("[X] (hors norme)")
                issues.append(f"   {day_key}: Lipides {fats_pct:.1f}% hors norme")

    # 3. Fibres
    print("\n3. APPORT EN FIBRES")
    print("   Standard professionnel: 25-30g/jour minimum")

    for day_key, day_data in analysis['daily_analyses'].items():
        fibers = day_data['totals']['fibers']
        print(f"   {day_key}: {fibers:.1f}g ", end="")
        if fibers >= 25:
            print("[OK]")
        else:
            print("[X] (insuffisant)")
            issues.append(f"   {day_key}: Fibres insuffisantes ({fibers:.1f}g < 25g)")

    # 4. Portions réalistes
    print("\n4. PORTIONS RÉALISTES")
    print("   Standard professionnel:")
    print("   - Pas de portions < 30g (sauf condiments/épices)")
    print("   - Pas de portions > 300g (sauf légumes)")

    portion_issues = []
    for day_key, day_data in analysis['daily_analyses'].items():
        for meal in day_data['meals']:
            for food_name, qty, unit_weight in meal['foods_detail']:
                category = ""  # On n'a pas la catégorie ici, simplification
                if qty < 30 and 'huile' not in food_name.lower() and 'epice' not in food_name.lower():
                    portion_issues.append(f"   [X] {food_name}: {qty:.0f}g trop petit")
                elif qty > 300 and 'legume' not in food_name.lower() and 'salade' not in food_name.lower():
                    portion_issues.append(f"   [X] {food_name}: {qty:.0f}g tres gros")

    if portion_issues:
        print(f"\n   Portions problematiques trouvees:")
        for issue in portion_issues[:10]:  # Limiter à 10
            print(issue)
        issues.extend(portion_issues)
    else:
        print("   [OK] Toutes les portions sont realistes")

    # Résumé
    print(f"\n{'='*80}")
    print("RÉSUMÉ DE LA CONFORMITÉ")
    print(f"{'='*80}")

    if not issues:
        print("[OK] Le plan est conforme aux standards professionnels!")
    else:
        print(f"[X] {len(issues)} problemes detectes:")
        for issue in issues[:15]:  # Limiter l'affichage
            print(issue)
        if len(issues) > 15:
            print(f"   ... et {len(issues) - 15} autres")

    return issues


def test_multiple_profiles():
    """Teste plusieurs profils nutritionnels."""

    db = DatabaseManager()
    all_foods = db.get_all_foods()

    print(f"Base de données: {len(all_foods)} aliments disponibles")

    # Profils de test
    test_profiles = [
        {
            "name": "Femme sédentaire - Perte de poids",
            "target": NutritionTarget(calories=1500, proteins=90, carbs=150, fats=50),
            "variety_level": 5
        },
        {
            "name": "Homme actif - Maintien",
            "target": NutritionTarget(calories=2200, proteins=140, carbs=250, fats=73),
            "variety_level": 7
        },
        {
            "name": "Sportif - Prise de masse",
            "target": NutritionTarget(calories=3000, proteins=200, carbs=375, fats=100),
            "variety_level": 4
        }
    ]

    all_results = []

    for profile in test_profiles:
        print(f"\n\n{'#'*80}")
        print(f"# PROFIL: {profile['name']}")
        print(f"# Objectif: {profile['target'].calories:.0f} kcal/jour")
        print(f"{'#'*80}")

        # Créer le générateur
        generator = FoodBasedGenerator(
            available_foods=all_foods,
            nutrition_target=profile['target'],
            variety_level=profile['variety_level'],
            use_ilp=True
        )

        # Créer le plan
        meal_plan = MealPlan(
            duration_days=1,
            nutrition_target=profile['target']
        )

        # Types de repas (3 repas + 1 collation)
        meal_types = [
            ("breakfast", 0.25),
            ("lunch", 0.40),
            ("afternoon_snack", 0.05),
            ("dinner", 0.30)
        ]

        generator.daily_accumulated_calories = 0.0

        for i, (meal_type, percentage) in enumerate(meal_types):
            import random
            if meal_type in ["breakfast", "snack", "afternoon_snack"]:
                min_foods = random.randint(3, 4)
                max_foods = random.randint(5, 6)
            else:
                min_foods = random.randint(4, 5)
                max_foods = random.randint(6, 8)

            is_last_meal = (i == len(meal_types) - 1)

            meal = generator.generate_meal(
                meal_type=meal_type,
                day_number=1,
                target_percentage=percentage,
                is_last_meal_of_day=is_last_meal,
                min_foods=min_foods,
                max_foods=max_foods
            )
            meal_plan.add_meal(meal)

        # Analyser le plan
        analysis = analyze_meal_plan(meal_plan)

        # Comparer avec standards
        issues = compare_with_professional_standards(analysis)

        all_results.append({
            "profile": profile['name'],
            "analysis": analysis,
            "num_issues": len(issues)
        })

    # Synthèse globale
    print(f"\n\n{'#'*80}")
    print("# SYNTHÈSE GLOBALE")
    print(f"{'#'*80}")

    for result in all_results:
        print(f"\n{result['profile']}:")
        print(f"  Score qualite: {result['analysis']['quality']['total_score']:.1f}/100 "
              f"({result['analysis']['quality']['grade']})")
        print(f"  Problemes detectes: {result['num_issues']}")
        print(f"  Validation: {'[OK]' if result['analysis']['validation']['is_valid'] else '[X]'}")

    # Identifier les axes d'amélioration
    print(f"\n{'='*80}")
    print("AXES D'AMÉLIORATION PRIORITAIRES")
    print(f"{'='*80}")

    avg_nutrition = sum(r['analysis']['quality']['nutrition_score'] for r in all_results) / len(all_results)
    avg_diversity = sum(r['analysis']['quality']['diversity_score'] for r in all_results) / len(all_results)
    avg_palatability = sum(r['analysis']['quality']['palatability_score'] for r in all_results) / len(all_results)
    avg_practicality = sum(r['analysis']['quality']['practicality_score'] for r in all_results) / len(all_results)

    improvements = [
        ("Nutrition", avg_nutrition),
        ("Diversité", avg_diversity),
        ("Palatabilité", avg_palatability),
        ("Praticité", avg_practicality)
    ]

    improvements.sort(key=lambda x: x[1])

    print("\nScores moyens (du plus faible au plus fort):")
    for name, score in improvements:
        status = "[OK] Bon" if score >= 80 else ("[!] Moyen" if score >= 70 else "[X] A ameliorer")
        print(f"  {name}: {score:.1f}/100 - {status}")

    print("\nRecommandations prioritaires:")
    if improvements[0][1] < 80:
        print(f"  1. Ameliorer le score de {improvements[0][0]} (actuellement {improvements[0][1]:.1f})")
    if improvements[1][1] < 80:
        print(f"  2. Ameliorer le score de {improvements[1][0]} (actuellement {improvements[1][1]:.1f})")

    return all_results


if __name__ == "__main__":
    results = test_multiple_profiles()
    print("\n\nTest terminé!")
