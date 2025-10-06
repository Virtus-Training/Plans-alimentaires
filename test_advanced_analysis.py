"""
Suite de tests avancés pour identifier les faiblesses du générateur de repas
"""

from collections import defaultdict, Counter
from pathlib import Path
from typing import List, Dict, Tuple
import statistics

from meal_planner.models.database import DatabaseManager
from meal_planner.models.nutrition import NutritionTarget
from meal_planner.models.meal_plan import MealPlan
from meal_planner.services.meal_generators import FoodBasedGenerator
from meal_planner.config import DATABASE_PATH
from meal_planner.data.meal_coherence_rules import is_starch_food


class AdvancedMealPlanAnalyzer:
    """Analyseur avancé de plans alimentaires"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.foods = db_manager.get_all_foods()

    def generate_test_plans(self, num_plans: int = 5, days: int = 7) -> List[MealPlan]:
        """Génère plusieurs plans alimentaires pour l'analyse"""
        plans = []

        # Différents profils nutritionnels
        profiles = [
            ("Standard", NutritionTarget(2000, 150, 200, 67)),
            ("Haute protéine", NutritionTarget(2000, 180, 150, 70)),
            ("Faible glucides", NutritionTarget(2000, 150, 100, 100)),
            ("Végétarien équilibré", NutritionTarget(1800, 120, 220, 60)),
            ("Gain musculaire", NutritionTarget(2500, 200, 250, 80)),
        ]

        for profile_name, target in profiles[:num_plans]:
            print(f"\nGeneration plan '{profile_name}'...")

            generator = FoodBasedGenerator(
                available_foods=self.foods,
                nutrition_target=target,
                tolerance=0.15,
                price_level=5,
                health_index=5,
                variety_level=5,
                use_ilp=False
            )

            meal_plan = MealPlan(
                duration_days=days,
                nutrition_target=target,
                notes=f"Test Plan - {profile_name}"
            )

            for day in range(1, days + 1):
                generator.reset_used_foods()
                generator.daily_accumulated_calories = 0.0

                # Générer les repas de la journée
                breakfast = generator.generate_meal("breakfast", day, 0.25)
                lunch = generator.generate_meal("lunch", day, 0.40)
                dinner = generator.generate_meal("dinner", day, 0.30)
                snack = generator.generate_meal("snack", day, 0.05)

                meal_plan.add_meal(breakfast)
                meal_plan.add_meal(lunch)
                meal_plan.add_meal(dinner)
                meal_plan.add_meal(snack)

            plans.append((profile_name, meal_plan))

        return plans

    def analyze_food_diversity(self, plans: List[Tuple[str, MealPlan]]) -> Dict:
        """Analyse la diversité des aliments utilisés"""
        print("\n" + "="*70)
        print("ANALYSE 1: DIVERSITE DES ALIMENTS")
        print("="*70)

        results = {}

        for profile_name, plan in plans:
            food_usage = Counter()
            category_usage = Counter()
            total_foods = 0

            for day in range(1, plan.duration_days + 1):
                meals = plan.get_meals_for_day(day)
                for meal in meals:
                    for food, qty in meal.foods:
                        food_usage[food.name] += 1
                        category_usage[food.category] += 1
                        total_foods += 1

            unique_foods = len(food_usage)
            unique_categories = len(category_usage)
            avg_repetitions = total_foods / unique_foods if unique_foods > 0 else 0

            # Aliments les plus répétés
            most_repeated = food_usage.most_common(5)

            results[profile_name] = {
                "total_foods_instances": total_foods,
                "unique_foods": unique_foods,
                "unique_categories": unique_categories,
                "avg_repetitions": avg_repetitions,
                "most_repeated": most_repeated,
                "food_distribution": dict(food_usage)
            }

            print(f"\n--- {profile_name} ---")
            print(f"  Total d'aliments utilises: {total_foods}")
            print(f"  Aliments uniques: {unique_foods}")
            print(f"  Categories uniques: {unique_categories}")
            print(f"  Repetition moyenne: {avg_repetitions:.1f}x par aliment")
            print(f"  Aliments les plus repetes:")
            for food_name, count in most_repeated:
                print(f"    - {food_name}: {count}x ({count/total_foods*100:.1f}%)")

        return results

    def analyze_nutritional_consistency(self, plans: List[Tuple[str, MealPlan]]) -> Dict:
        """Analyse la cohérence nutritionnelle sur plusieurs jours"""
        print("\n" + "="*70)
        print("ANALYSE 2: COHERENCE NUTRITIONNELLE")
        print("="*70)

        results = {}

        for profile_name, plan in plans:
            daily_macros = []

            for day in range(1, plan.duration_days + 1):
                day_total = {"calories": 0, "proteins": 0, "carbs": 0, "fats": 0}
                meals = plan.get_meals_for_day(day)

                for meal in meals:
                    macros = meal.calculate_macros()
                    for key in day_total:
                        day_total[key] += macros[key]

                daily_macros.append(day_total)

            # Calculer statistiques
            stats = {}
            for macro in ["calories", "proteins", "carbs", "fats"]:
                values = [d[macro] for d in daily_macros]
                target_val = getattr(plan.nutrition_target, macro)

                stats[macro] = {
                    "mean": statistics.mean(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "target": target_val,
                    "mean_deviation": abs(statistics.mean(values) - target_val),
                    "deviation_percent": abs(statistics.mean(values) - target_val) / target_val * 100 if target_val > 0 else 0
                }

            results[profile_name] = stats

            print(f"\n--- {profile_name} ---")
            for macro in ["calories", "proteins", "carbs", "fats"]:
                s = stats[macro]
                print(f"  {macro.capitalize()}:")
                print(f"    Cible: {s['target']:.1f}")
                print(f"    Moyenne: {s['mean']:.1f} (ecart: {s['deviation_percent']:.1f}%)")
                print(f"    Ecart-type: {s['stdev']:.1f}")
                print(f"    Min-Max: {s['min']:.1f} - {s['max']:.1f}")

        return results

    def analyze_starch_coherence(self, plans: List[Tuple[str, MealPlan]]) -> Dict:
        """Analyse le respect de la règle un seul féculent par repas"""
        print("\n" + "="*70)
        print("ANALYSE 3: COHERENCE DES FECULENTS")
        print("="*70)

        results = {}

        for profile_name, plan in plans:
            total_meals = 0
            meals_with_multiple_starches = 0
            meals_with_one_starch = 0
            meals_with_no_starch = 0
            violations = []

            for day in range(1, plan.duration_days + 1):
                meals = plan.get_meals_for_day(day)

                for meal in meals:
                    total_meals += 1
                    starches = [
                        (food.name, qty) for food, qty in meal.foods
                        if is_starch_food(food.category, food.name)
                    ]

                    if len(starches) > 1:
                        meals_with_multiple_starches += 1
                        violations.append({
                            "day": day,
                            "meal_type": meal.meal_type,
                            "starches": starches
                        })
                    elif len(starches) == 1:
                        meals_with_one_starch += 1
                    else:
                        meals_with_no_starch += 1

            compliance_rate = (total_meals - meals_with_multiple_starches) / total_meals * 100 if total_meals > 0 else 0

            results[profile_name] = {
                "total_meals": total_meals,
                "violations": meals_with_multiple_starches,
                "one_starch": meals_with_one_starch,
                "no_starch": meals_with_no_starch,
                "compliance_rate": compliance_rate,
                "violation_details": violations
            }

            print(f"\n--- {profile_name} ---")
            print(f"  Total repas: {total_meals}")
            print(f"  Repas avec 1 feculent: {meals_with_one_starch} ({meals_with_one_starch/total_meals*100:.1f}%)")
            print(f"  Repas sans feculent: {meals_with_no_starch} ({meals_with_no_starch/total_meals*100:.1f}%)")
            print(f"  Repas avec >1 feculent: {meals_with_multiple_starches} ({meals_with_multiple_starches/total_meals*100:.1f}%)")
            print(f"  Taux de conformite: {compliance_rate:.1f}%")

            if violations:
                print(f"  Violations detectees:")
                for v in violations:
                    starches_str = ", ".join([f"{name} ({qty:.0f}g)" for name, qty in v["starches"]])
                    print(f"    - Jour {v['day']} - {v['meal_type']}: {starches_str}")

        return results

    def analyze_meal_size_consistency(self, plans: List[Tuple[str, MealPlan]]) -> Dict:
        """Analyse la cohérence de la taille des repas"""
        print("\n" + "="*70)
        print("ANALYSE 4: COHERENCE DES TAILLES DE REPAS")
        print("="*70)

        results = {}

        for profile_name, plan in plans:
            meal_sizes_by_type = defaultdict(list)

            for day in range(1, plan.duration_days + 1):
                meals = plan.get_meals_for_day(day)

                for meal in meals:
                    num_foods = len(meal.foods)
                    total_weight = sum(qty for _, qty in meal.foods)
                    calories = meal.calculate_macros()["calories"]

                    meal_sizes_by_type[meal.meal_type].append({
                        "num_foods": num_foods,
                        "total_weight": total_weight,
                        "calories": calories
                    })

            stats_by_type = {}
            for meal_type, sizes in meal_sizes_by_type.items():
                if sizes:
                    stats_by_type[meal_type] = {
                        "avg_num_foods": statistics.mean([s["num_foods"] for s in sizes]),
                        "stdev_num_foods": statistics.stdev([s["num_foods"] for s in sizes]) if len(sizes) > 1 else 0,
                        "avg_weight": statistics.mean([s["total_weight"] for s in sizes]),
                        "avg_calories": statistics.mean([s["calories"] for s in sizes]),
                        "stdev_calories": statistics.stdev([s["calories"] for s in sizes]) if len(sizes) > 1 else 0,
                    }

            results[profile_name] = stats_by_type

            print(f"\n--- {profile_name} ---")
            for meal_type, stats in stats_by_type.items():
                print(f"  {meal_type}:")
                print(f"    Nombre d'aliments: {stats['avg_num_foods']:.1f} ± {stats['stdev_num_foods']:.1f}")
                print(f"    Poids total: {stats['avg_weight']:.0f}g")
                print(f"    Calories: {stats['avg_calories']:.0f} ± {stats['stdev_calories']:.0f}")

        return results

    def analyze_category_balance(self, plans: List[Tuple[str, MealPlan]]) -> Dict:
        """Analyse l'équilibre entre les catégories d'aliments"""
        print("\n" + "="*70)
        print("ANALYSE 5: EQUILIBRE DES CATEGORIES")
        print("="*70)

        results = {}

        for profile_name, plan in plans:
            category_quantities = defaultdict(float)
            category_calories = defaultdict(float)
            total_weight = 0
            total_calories = 0

            for day in range(1, plan.duration_days + 1):
                meals = plan.get_meals_for_day(day)

                for meal in meals:
                    for food, qty in meal.foods:
                        category_quantities[food.category] += qty
                        macros = food.calculate_for_quantity(qty)
                        category_calories[food.category] += macros["calories"]
                        total_weight += qty
                        total_calories += macros["calories"]

            # Calculer les pourcentages
            category_stats = {}
            for cat in category_quantities:
                category_stats[cat] = {
                    "weight": category_quantities[cat],
                    "weight_percent": category_quantities[cat] / total_weight * 100 if total_weight > 0 else 0,
                    "calories": category_calories[cat],
                    "calories_percent": category_calories[cat] / total_calories * 100 if total_calories > 0 else 0
                }

            # Trier par calories
            sorted_categories = sorted(
                category_stats.items(),
                key=lambda x: x[1]["calories"],
                reverse=True
            )

            results[profile_name] = dict(category_stats)

            print(f"\n--- {profile_name} ---")
            print(f"  Repartition par calories:")
            for cat, stats in sorted_categories[:10]:  # Top 10
                print(f"    {cat}: {stats['calories']:.0f} kcal ({stats['calories_percent']:.1f}%)")

        return results

    def analyze_extreme_cases(self, plans: List[Tuple[str, MealPlan]]) -> Dict:
        """Analyse les cas extrêmes et anomalies"""
        print("\n" + "="*70)
        print("ANALYSE 6: CAS EXTREMES ET ANOMALIES")
        print("="*70)

        results = {}

        for profile_name, plan in plans:
            anomalies = {
                "very_small_portions": [],  # < 20g
                "very_large_portions": [],  # > 400g
                "meals_with_few_foods": [],  # < 3 aliments
                "meals_with_many_foods": [],  # > 10 aliments
                "high_calorie_variance": []  # écart > 50% de la cible
            }

            for day in range(1, plan.duration_days + 1):
                meals = plan.get_meals_for_day(day)

                for meal in meals:
                    # Portions extrêmes
                    for food, qty in meal.foods:
                        if qty < 20:
                            anomalies["very_small_portions"].append({
                                "day": day,
                                "meal": meal.meal_type,
                                "food": food.name,
                                "quantity": qty
                            })
                        if qty > 400:
                            anomalies["very_large_portions"].append({
                                "day": day,
                                "meal": meal.meal_type,
                                "food": food.name,
                                "quantity": qty
                            })

                    # Nombre d'aliments
                    num_foods = len(meal.foods)
                    if num_foods < 3:
                        anomalies["meals_with_few_foods"].append({
                            "day": day,
                            "meal": meal.meal_type,
                            "num_foods": num_foods
                        })
                    if num_foods > 10:
                        anomalies["meals_with_many_foods"].append({
                            "day": day,
                            "meal": meal.meal_type,
                            "num_foods": num_foods
                        })

                    # Variance calorique
                    macros = meal.calculate_macros()
                    target_cal = meal.target_calories
                    if target_cal > 0:
                        variance = abs(macros["calories"] - target_cal) / target_cal
                        if variance > 0.5:  # Plus de 50% d'écart
                            anomalies["high_calorie_variance"].append({
                                "day": day,
                                "meal": meal.meal_type,
                                "actual": macros["calories"],
                                "target": target_cal,
                                "variance_percent": variance * 100
                            })

            results[profile_name] = anomalies

            print(f"\n--- {profile_name} ---")
            total_anomalies = sum(len(v) for v in anomalies.values())
            print(f"  Total d'anomalies detectees: {total_anomalies}")

            for anomaly_type, items in anomalies.items():
                if items:
                    print(f"\n  {anomaly_type.replace('_', ' ').title()}: {len(items)}")
                    for item in items[:3]:  # Montrer 3 exemples max
                        if anomaly_type in ["very_small_portions", "very_large_portions"]:
                            print(f"    - Jour {item['day']} ({item['meal']}): {item['food']} = {item['quantity']:.0f}g")
                        elif anomaly_type in ["meals_with_few_foods", "meals_with_many_foods"]:
                            print(f"    - Jour {item['day']} ({item['meal']}): {item['num_foods']} aliments")
                        elif anomaly_type == "high_calorie_variance":
                            print(f"    - Jour {item['day']} ({item['meal']}): {item['actual']:.0f}/{item['target']:.0f} kcal (ecart {item['variance_percent']:.0f}%)")

        return results


def main():
    """Point d'entrée principal"""
    print("="*70)
    print("SUITE DE TESTS AVANCES - ANALYSE DU GENERATEUR DE REPAS")
    print("="*70)

    # Initialiser
    db_manager = DatabaseManager(DATABASE_PATH)
    analyzer = AdvancedMealPlanAnalyzer(db_manager)

    # Générer les plans de test
    print("\nGeneration de 5 plans alimentaires sur 7 jours...")
    plans = analyzer.generate_test_plans(num_plans=5, days=7)

    # Exécuter toutes les analyses
    diversity_results = analyzer.analyze_food_diversity(plans)
    nutrition_results = analyzer.analyze_nutritional_consistency(plans)
    starch_results = analyzer.analyze_starch_coherence(plans)
    size_results = analyzer.analyze_meal_size_consistency(plans)
    category_results = analyzer.analyze_category_balance(plans)
    extreme_results = analyzer.analyze_extreme_cases(plans)

    # Résumé global
    print("\n" + "="*70)
    print("RESUME GLOBAL DES FAIBLESSES DETECTEES")
    print("="*70)

    print("\n1. DIVERSITE:")
    for profile, data in diversity_results.items():
        print(f"  {profile}: {data['unique_foods']} aliments uniques, repetition moyenne {data['avg_repetitions']:.1f}x")

    print("\n2. COHERENCE NUTRITIONNELLE:")
    for profile, data in nutrition_results.items():
        cal_dev = data['calories']['deviation_percent']
        prot_dev = data['proteins']['deviation_percent']
        print(f"  {profile}: Ecart calories {cal_dev:.1f}%, proteines {prot_dev:.1f}%")

    print("\n3. FECULENTS:")
    for profile, data in starch_results.items():
        print(f"  {profile}: Conformite {data['compliance_rate']:.1f}% ({data['violations']} violations)")

    print("\n4. ANOMALIES:")
    for profile, data in extreme_results.items():
        total = sum(len(v) for v in data.values())
        print(f"  {profile}: {total} anomalies detectees")

    print("\n" + "="*70)
    print("FIN DE L'ANALYSE")
    print("="*70)


if __name__ == "__main__":
    main()
