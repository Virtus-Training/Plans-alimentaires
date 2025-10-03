"""
Script pour peupler la base de données avec des aliments de test
incluant les attributs prix, santé et variété
"""

from pathlib import Path
from meal_planner.models.database import DatabaseManager
from meal_planner.models.food import Food

def populate_test_foods():
    """Ajoute des aliments de test avec des valeurs réalistes."""

    db_path = Path("meal_planner/data/foods.db")
    db_manager = DatabaseManager(db_path)

    # Aliments de test avec prix, santé et variété
    test_foods = [
        # Petit-déjeuner
        Food(
            name="Flocons d'avoine",
            category="Céréales",
            calories=389,
            proteins=16.9,
            carbs=66.3,
            fats=6.9,
            fibers=10.6,
            tags=["vegetarian", "vegan", "breakfast"],
            price_per_100g=0.30,
            health_index=9,
            variety_index=2
        ),
        Food(
            name="Pain complet",
            category="Céréales",
            calories=247,
            proteins=13.0,
            carbs=41.0,
            fats=3.4,
            fibers=7.0,
            tags=["vegetarian", "breakfast", "lunch", "snack"],
            price_per_100g=0.25,
            health_index=7,
            variety_index=1
        ),
        Food(
            name="Œufs",
            category="Œufs",
            calories=143,
            proteins=12.6,
            carbs=0.7,
            fats=9.9,
            fibers=0.0,
            tags=["breakfast", "lunch", "dinner"],
            price_per_100g=0.40,
            health_index=8,
            variety_index=1
        ),
        Food(
            name="Lait demi-écrémé",
            category="Produits laitiers",
            calories=49,
            proteins=3.4,
            carbs=4.8,
            fats=1.6,
            fibers=0.0,
            tags=["vegetarian", "breakfast", "snack"],
            price_per_100g=0.12,
            health_index=6,
            variety_index=1
        ),
        Food(
            name="Yaourt grec",
            category="Produits laitiers",
            calories=97,
            proteins=9.0,
            carbs=3.6,
            fats=5.0,
            fibers=0.0,
            tags=["vegetarian", "breakfast", "snack"],
            price_per_100g=0.80,
            health_index=8,
            variety_index=3
        ),

        # Protéines
        Food(
            name="Poulet (blanc)",
            category="Viandes",
            calories=165,
            proteins=31.0,
            carbs=0.0,
            fats=3.6,
            fibers=0.0,
            tags=["lunch", "dinner"],
            price_per_100g=1.20,
            health_index=8,
            variety_index=1
        ),
        Food(
            name="Saumon",
            category="Poissons",
            calories=208,
            proteins=20.0,
            carbs=0.0,
            fats=13.0,
            fibers=0.0,
            tags=["lunch", "dinner"],
            price_per_100g=2.50,
            health_index=9,
            variety_index=4
        ),
        Food(
            name="Thon (conserve)",
            category="Poissons",
            calories=116,
            proteins=26.0,
            carbs=0.0,
            fats=1.0,
            fibers=0.0,
            tags=["lunch", "dinner", "snack"],
            price_per_100g=0.70,
            health_index=7,
            variety_index=2
        ),
        Food(
            name="Tofu",
            category="Légumineuses",
            calories=76,
            proteins=8.0,
            carbs=1.9,
            fats=4.8,
            fibers=0.3,
            tags=["vegetarian", "vegan", "lunch", "dinner"],
            price_per_100g=0.60,
            health_index=8,
            variety_index=5
        ),

        # Glucides
        Food(
            name="Riz basmati",
            category="Féculents",
            calories=350,
            proteins=7.5,
            carbs=77.0,
            fats=0.6,
            fibers=1.0,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=0.35,
            health_index=6,
            variety_index=2
        ),
        Food(
            name="Pâtes complètes",
            category="Féculents",
            calories=348,
            proteins=13.0,
            carbs=64.0,
            fats=2.5,
            fibers=11.0,
            tags=["vegetarian", "vegan", "lunch", "dinner"],
            price_per_100g=0.40,
            health_index=7,
            variety_index=2
        ),
        Food(
            name="Patate douce",
            category="Féculents",
            calories=86,
            proteins=1.6,
            carbs=20.0,
            fats=0.1,
            fibers=3.0,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=0.30,
            health_index=9,
            variety_index=4
        ),
        Food(
            name="Quinoa",
            category="Féculents",
            calories=368,
            proteins=14.0,
            carbs=64.0,
            fats=6.0,
            fibers=7.0,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=0.90,
            health_index=9,
            variety_index=6
        ),

        # Légumes
        Food(
            name="Brocoli",
            category="Légumes",
            calories=34,
            proteins=2.8,
            carbs=7.0,
            fats=0.4,
            fibers=2.6,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=0.35,
            health_index=10,
            variety_index=2
        ),
        Food(
            name="Épinards",
            category="Légumes",
            calories=23,
            proteins=2.9,
            carbs=3.6,
            fats=0.4,
            fibers=2.2,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=0.40,
            health_index=10,
            variety_index=2
        ),
        Food(
            name="Tomates",
            category="Légumes",
            calories=18,
            proteins=0.9,
            carbs=3.9,
            fats=0.2,
            fibers=1.2,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner", "snack"],
            price_per_100g=0.25,
            health_index=9,
            variety_index=1
        ),
        Food(
            name="Carottes",
            category="Légumes",
            calories=41,
            proteins=0.9,
            carbs=10.0,
            fats=0.2,
            fibers=2.8,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner", "snack"],
            price_per_100g=0.20,
            health_index=9,
            variety_index=1
        ),

        # Fruits
        Food(
            name="Banane",
            category="Fruits",
            calories=89,
            proteins=1.1,
            carbs=23.0,
            fats=0.3,
            fibers=2.6,
            tags=["vegetarian", "vegan", "gluten_free", "breakfast", "snack"],
            price_per_100g=0.30,
            health_index=7,
            variety_index=1
        ),
        Food(
            name="Pomme",
            category="Fruits",
            calories=52,
            proteins=0.3,
            carbs=14.0,
            fats=0.2,
            fibers=2.4,
            tags=["vegetarian", "vegan", "gluten_free", "breakfast", "snack"],
            price_per_100g=0.35,
            health_index=8,
            variety_index=1
        ),
        Food(
            name="Myrtilles",
            category="Fruits",
            calories=57,
            proteins=0.7,
            carbs=14.0,
            fats=0.3,
            fibers=2.4,
            tags=["vegetarian", "vegan", "gluten_free", "breakfast", "snack"],
            price_per_100g=1.50,
            health_index=10,
            variety_index=5
        ),

        # Matières grasses
        Food(
            name="Huile d'olive",
            category="Matières grasses",
            calories=884,
            proteins=0.0,
            carbs=0.0,
            fats=100.0,
            fibers=0.0,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=1.20,
            health_index=9,
            variety_index=2
        ),
        Food(
            name="Avocat",
            category="Fruits",
            calories=160,
            proteins=2.0,
            carbs=9.0,
            fats=15.0,
            fibers=7.0,
            tags=["vegetarian", "vegan", "gluten_free", "breakfast", "lunch", "snack"],
            price_per_100g=0.80,
            health_index=9,
            variety_index=4
        ),
        Food(
            name="Amandes",
            category="Noix",
            calories=579,
            proteins=21.0,
            carbs=22.0,
            fats=50.0,
            fibers=12.0,
            tags=["vegetarian", "vegan", "gluten_free", "snack"],
            price_per_100g=2.00,
            health_index=9,
            variety_index=3
        ),

        # Aliments exotiques/rares (pour tester la variété)
        Food(
            name="Tempeh",
            category="Légumineuses",
            calories=193,
            proteins=19.0,
            carbs=9.0,
            fats=11.0,
            fibers=5.0,
            tags=["vegetarian", "vegan", "lunch", "dinner"],
            price_per_100g=1.50,
            health_index=9,
            variety_index=8
        ),
        Food(
            name="Edamame",
            category="Légumineuses",
            calories=122,
            proteins=11.0,
            carbs=9.0,
            fats=5.0,
            fibers=5.0,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner", "snack"],
            price_per_100g=0.90,
            health_index=9,
            variety_index=7
        ),
        Food(
            name="Chou kale",
            category="Légumes",
            calories=49,
            proteins=4.3,
            carbs=9.0,
            fats=0.9,
            fibers=2.0,
            tags=["vegetarian", "vegan", "gluten_free", "lunch", "dinner"],
            price_per_100g=0.70,
            health_index=10,
            variety_index=6
        ),
    ]

    print("Ajout des aliments de test...\n")

    added_count = 0
    updated_count = 0

    for food in test_foods:
        try:
            # Vérifier si l'aliment existe déjà
            existing = db_manager.get_food_by_name(food.name)

            if existing:
                # Mettre à jour l'aliment existant
                food.id = existing.id
                db_manager.update_food(food)
                print(f"[MAJ] {food.name} - Prix: {food.price_per_100g}€, Santé: {food.health_index}/10, Variété: {food.variety_index}/10")
                updated_count += 1
            else:
                # Ajouter le nouvel aliment
                db_manager.add_food(food)
                print(f"[+] {food.name} - Prix: {food.price_per_100g}€, Santé: {food.health_index}/10, Variété: {food.variety_index}/10")
                added_count += 1

        except Exception as e:
            print(f"[ERREUR] {food.name}: {e}")

    print(f"\n[SUCCES] {added_count} aliments ajoutés, {updated_count} mis à jour")

    # Afficher les statistiques
    stats = db_manager.get_statistics()
    print(f"\nTotal d'aliments en base: {stats['total_foods']}")
    print(f"Catégories: {len(stats['categories'])}")
    for category, count in sorted(stats['categories'].items()):
        print(f"  - {category}: {count}")

if __name__ == "__main__":
    populate_test_foods()
