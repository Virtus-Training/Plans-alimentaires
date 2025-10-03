"""
Matrice de compatibilité alimentaire pour améliorer la palatabilité des repas.
Basée sur les principes culinaires et les combinaisons traditionnelles.
"""

from typing import Dict, Tuple

# Score de compatibilité entre 0.0 (incompatible) et 1.0 (excellent)
FOOD_COMPATIBILITY: Dict[Tuple[str, str], float] = {
    # Viandes et féculents
    ("poulet", "riz"): 1.0,
    ("poulet", "pâtes"): 0.9,
    ("poulet", "patate douce"): 0.9,
    ("poulet", "quinoa"): 0.8,

    # Poissons et accompagnements
    ("saumon", "riz"): 1.0,
    ("saumon", "quinoa"): 0.9,
    ("saumon", "patate douce"): 0.8,
    ("thon", "pâtes"): 0.9,
    ("maquereau", "riz"): 0.9,
    ("sardines", "riz"): 0.8,

    # Légumineuses et céréales
    ("tofu", "riz"): 1.0,
    ("tofu", "quinoa"): 0.9,
    ("tempeh", "riz"): 0.9,
    ("lentilles", "riz"): 1.0,
    ("pois chiches", "quinoa"): 0.9,
    ("haricots", "riz"): 0.9,

    # Petit-déjeuner classiques
    ("œufs", "pain"): 1.0,
    ("œufs", "flocons d'avoine"): 0.6,
    ("yaourt", "flocons d'avoine"): 1.0,
    ("yaourt", "fruits"): 1.0,
    ("pain", "fromage"): 0.9,
    ("pain", "avocat"): 0.9,

    # Protéines et légumes
    ("poulet", "brocoli"): 0.9,
    ("poulet", "épinards"): 0.8,
    ("poulet", "tomates"): 0.8,
    ("poisson", "légumes"): 0.9,
    ("saumon", "épinards"): 0.9,
    ("saumon", "brocoli"): 0.8,

    # Viandes supplémentaires
    ("boeuf", "pommes de terre"): 1.0,
    ("boeuf", "carottes"): 0.9,
    ("boeuf", "champignons"): 0.9,
    ("boeuf", "oignon"): 1.0,
    ("porc", "pommes"): 0.9,
    ("porc", "chou"): 0.9,
    ("dinde", "cranberries"): 1.0,

    # Poissons supplémentaires
    ("saumon", "citron"): 1.0,
    ("saumon", "aneth"): 1.0,
    ("saumon", "avocat"): 0.9,
    ("thon", "salade"): 0.9,
    ("thon", "maïs"): 0.8,
    ("cabillaud", "légumes"): 0.9,
    ("sardines", "tomates"): 0.9,
    ("crevettes", "ail"): 1.0,
    ("crevettes", "pâtes"): 0.9,

    # Légumineuses étendues
    ("lentilles", "curry"): 0.9,
    ("lentilles", "tomates"): 0.9,
    ("pois chiches", "tahini"): 1.0,
    ("pois chiches", "curry"): 0.9,
    ("haricots", "tomates"): 0.9,
    ("haricots", "maïs"): 0.8,
    ("seitan", "légumes"): 0.9,
    ("seitan", "sauce soja"): 0.9,
    ("tofu", "sésame"): 0.9,

    # Petit-déjeuner étendu
    ("œufs", "bacon"): 0.9,
    ("œufs", "avocat"): 0.9,
    ("œufs", "fromage"): 0.9,
    ("yaourt", "miel"): 0.9,
    ("yaourt", "granola"): 0.9,
    ("pain", "beurre de cacahuète"): 0.9,
    ("pain", "confiture"): 0.9,
    ("flocons d'avoine", "banane"): 0.9,
    ("flocons d'avoine", "fruits rouges"): 0.9,

    # Associations complémentaires
    ("riz", "légumes"): 0.9,
    ("pâtes", "tomates"): 1.0,
    ("pâtes", "basilic"): 1.0,
    ("quinoa", "légumes"): 0.9,
    ("pommes de terre", "fromage"): 0.8,
    ("tomates", "basilic"): 1.0,
    ("tomates", "mozzarella"): 1.0,
    ("épinards", "fromage"): 0.8,
    ("brocoli", "fromage"): 0.7,
    ("carottes", "gingembre"): 0.9,
    ("pomme", "cannelle"): 1.0,
    ("banane", "chocolat"): 0.9,
    ("fraises", "crème"): 0.9,
    ("amandes", "fruits"): 0.8,
    ("noix", "fromage"): 0.8,

    # Poulet étendu
    ("poulet", "citron"): 1.0,
    ("poulet", "miel"): 0.7,
    ("poulet", "curry"): 0.9,

    # Combinaisons à éviter (scores bas)
    ("poisson", "fromage"): 0.3,
    ("poisson", "yaourt"): 0.2,
    ("chocolat", "viande"): 0.1,
    ("fruits", "viande"): 0.4,
    ("lait", "poisson"): 0.3,
    ("orange", "lait"): 0.4,
    ("melon", "jambon"): 0.5,
    ("ananas", "pizza"): 0.3,
    ("ketchup", "pâtes"): 0.4,
    ("mayonnaise", "fruits"): 0.2,
    ("yaourt", "poisson"): 0.2,
}

# Catégories compatibles (pour les aliments non listés spécifiquement)
CATEGORY_COMPATIBILITY: Dict[Tuple[str, str], float] = {
    # Excellentes combinaisons
    ("viandes", "légumes"): 0.9,
    ("viandes", "féculents"): 0.9,
    ("poissons", "légumes"): 0.9,
    ("poissons", "féculents"): 0.9,
    ("légumineuses", "féculents"): 0.9,
    ("légumineuses", "légumes"): 0.9,
    ("céréales", "produits laitiers"): 0.9,
    ("fruits", "produits laitiers"): 0.9,
    ("œufs", "céréales"): 0.9,
    ("œufs", "légumes"): 0.8,

    # Bonnes combinaisons
    ("viandes", "produits laitiers"): 0.6,
    ("noix", "fruits"): 0.8,
    ("noix", "céréales"): 0.8,

    # Combinaisons moyennes
    ("légumes", "fruits"): 0.5,
    ("féculents", "fruits"): 0.4,

    # Combinaisons à éviter
    ("poissons", "produits laitiers"): 0.3,
    ("viandes", "fruits"): 0.4,
}


def get_compatibility_score(food1_name: str, food2_name: str,
                            food1_cat: str = "", food2_cat: str = "") -> float:
    """
    Retourne le score de compatibilité entre deux aliments.

    Args:
        food1_name: Nom du premier aliment
        food2_name: Nom du deuxième aliment
        food1_cat: Catégorie du premier aliment (optionnel)
        food2_cat: Catégorie du deuxième aliment (optionnel)

    Returns:
        Score entre 0.0 et 1.0 (1.0 = excellente compatibilité)
    """
    # Normaliser les noms (minuscules, sans accents)
    name1 = food1_name.lower().strip()
    name2 = food2_name.lower().strip()

    # Même aliment = parfaite compatibilité
    if name1 == name2:
        return 1.0

    # Chercher dans la matrice exacte (dans les deux sens)
    key1 = (name1, name2)
    key2 = (name2, name1)

    if key1 in FOOD_COMPATIBILITY:
        return FOOD_COMPATIBILITY[key1]
    if key2 in FOOD_COMPATIBILITY:
        return FOOD_COMPATIBILITY[key2]

    # Chercher par mots-clés partiels
    for (f1, f2), score in FOOD_COMPATIBILITY.items():
        if (f1 in name1 and f2 in name2) or (f2 in name1 and f1 in name2):
            return score

    # Si pas trouvé, utiliser la compatibilité par catégorie
    if food1_cat and food2_cat:
        cat1 = food1_cat.lower()
        cat2 = food2_cat.lower()

        key_cat1 = (cat1, cat2)
        key_cat2 = (cat2, cat1)

        if key_cat1 in CATEGORY_COMPATIBILITY:
            return CATEGORY_COMPATIBILITY[key_cat1]
        if key_cat2 in CATEGORY_COMPATIBILITY:
            return CATEGORY_COMPATIBILITY[key_cat2]

        # Chercher par mots-clés dans les catégories
        for (c1, c2), score in CATEGORY_COMPATIBILITY.items():
            if (c1 in cat1 and c2 in cat2) or (c2 in cat1 and c1 in cat2):
                return score

    # Par défaut : compatibilité neutre
    return 0.7


def calculate_meal_palatability(foods: list, categories: list = None) -> float:
    """
    Calcule le score de palatabilité global d'un repas.

    Args:
        foods: Liste de noms d'aliments
        categories: Liste optionnelle de catégories correspondantes

    Returns:
        Score entre 0.0 et 1.0 (1.0 = repas très harmonieux)
    """
    if len(foods) <= 1:
        return 1.0

    if categories is None:
        categories = [""] * len(foods)

    total_score = 0.0
    comparisons = 0

    # Calculer la compatibilité entre chaque paire d'aliments
    for i in range(len(foods)):
        for j in range(i + 1, len(foods)):
            score = get_compatibility_score(
                foods[i], foods[j],
                categories[i], categories[j]
            )
            total_score += score
            comparisons += 1

    # Moyenne des scores de compatibilité
    if comparisons == 0:
        return 1.0

    return total_score / comparisons


def get_incompatible_foods(food_name: str, food_cat: str = "") -> list:
    """
    Retourne la liste des aliments incompatibles avec l'aliment donné.

    Args:
        food_name: Nom de l'aliment
        food_cat: Catégorie de l'aliment

    Returns:
        Liste d'aliments à éviter (score < 0.4)
    """
    incompatible = []
    name = food_name.lower().strip()

    for (f1, f2), score in FOOD_COMPATIBILITY.items():
        if score < 0.4:
            if f1 in name:
                incompatible.append(f2)
            elif f2 in name:
                incompatible.append(f1)

    return incompatible
