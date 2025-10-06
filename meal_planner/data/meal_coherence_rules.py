"""
Règles de cohérence pour les repas - matrice de compatibilité
Inspiré des standards professionnels de nutrition
"""

# Scores de cohérence pour les combinaisons catégories/type de repas
# Score de 0 (incompatible) à 1 (parfait)
MEAL_CATEGORY_COHERENCE = {
    "breakfast": {
        # Très cohérent au petit-déjeuner
        "céréales": 1.0,
        "pain": 1.0,
        "produits laitiers": 1.0,
        "œufs": 1.0,
        "fruits": 1.0,
        "miel": 1.0,
        "confiture": 1.0,
        "beurre": 0.9,
        "fromage": 0.8,
        "noix": 0.8,

        # Moyennement cohérent
        "légumes": 0.5,  # Ex: tomate, avocat OK mais pas courant
        "féculents": 0.4,  # Patate douce parfois

        # Peu cohérent au petit-déjeuner
        "viandes": 0.1,  # Très rare sauf produits fumés
        "poissons": 0.2,  # Sauf saumon fumé
        "légumineuses": 0.2,
        "tofu": 0.2,
    },

    "lunch": {
        # Très cohérent au déjeuner
        "viandes": 1.0,
        "poissons": 1.0,
        "légumes": 1.0,
        "féculents": 1.0,
        "légumineuses": 1.0,
        "tofu": 1.0,
        "œufs": 0.9,
        "fromage": 0.8,
        "noix": 0.6,

        # Moyennement cohérent
        "céréales": 0.5,  # Quinoa, riz OK
        "produits laitiers": 0.4,  # Rare sauf fromage
        "fruits": 0.3,  # Plutôt en dessert

        # Peu cohérent
        "pain": 0.4,  # Possible mais pas central
        "miel": 0.1,
        "confiture": 0.1,
    },

    "dinner": {
        # Identique au lunch en général
        "viandes": 1.0,
        "poissons": 1.0,
        "légumes": 1.0,
        "féculents": 0.9,  # Légèrement moins le soir
        "légumineuses": 1.0,
        "tofu": 1.0,
        "œufs": 0.9,
        "fromage": 0.7,
        "noix": 0.6,
        "céréales": 0.5,
        "produits laitiers": 0.4,
        "fruits": 0.3,
        "pain": 0.4,
        "miel": 0.1,
        "confiture": 0.1,
    },

    "snack": {
        # Très cohérent en collation
        "fruits": 1.0,
        "noix": 1.0,
        "produits laitiers": 1.0,
        "fromage": 0.8,
        "pain": 0.7,
        "céréales": 0.6,

        # Moyennement cohérent
        "légumes": 0.5,  # Bâtonnets de légumes OK
        "œufs": 0.3,

        # Peu cohérent
        "viandes": 0.1,
        "poissons": 0.1,
        "légumineuses": 0.2,
        "tofu": 0.2,
        "féculents": 0.3,
    },

    "afternoon_snack": {
        # Copie de snack avec quelques ajustements
        "fruits": 1.0,
        "noix": 1.0,
        "produits laitiers": 1.0,
        "fromage": 0.8,
        "pain": 0.7,
        "céréales": 0.7,  # Barre de céréales
        "miel": 0.6,
        "confiture": 0.5,
        "légumes": 0.4,
        "œufs": 0.2,
        "viandes": 0.1,
        "poissons": 0.1,
        "légumineuses": 0.2,
        "tofu": 0.2,
        "féculents": 0.3,
    },

    "morning_snack": {
        # Similaire à afternoon_snack
        "fruits": 1.0,
        "noix": 1.0,
        "produits laitiers": 1.0,
        "fromage": 0.7,
        "pain": 0.6,
        "céréales": 0.7,
        "miel": 0.6,
        "légumes": 0.4,
        "œufs": 0.3,
        "viandes": 0.1,
        "poissons": 0.1,
        "légumineuses": 0.2,
        "tofu": 0.2,
        "féculents": 0.3,
    },

    "evening_snack": {
        # Collation du soir: plus léger
        "fruits": 1.0,
        "produits laitiers": 1.0,
        "noix": 0.8,  # Moins car gras le soir
        "fromage": 0.6,
        "légumes": 0.5,
        "céréales": 0.5,
        "pain": 0.4,
        "œufs": 0.2,
        "viandes": 0.1,
        "poissons": 0.1,
        "légumineuses": 0.2,
        "tofu": 0.2,
        "féculents": 0.2,
    }
}

# Combinaisons d'aliments incohérentes (pénalités fortes)
# Format: (categorie1, categorie2): pénalité (0-1, où 1 = très mauvais)
INCOMPATIBLE_COMBINATIONS = {
    # Poisson + produits laitiers (sauf fromage en gratin)
    ("poissons", "produits laitiers"): 0.7,
    ("poissons", "lait"): 0.9,

    # Viande rouge + poisson dans le même repas
    ("viandes", "poissons"): 0.6,

    # Fruits + protéines fortes (sauf petit-déjeuner)
    ("fruits", "viandes"): 0.5,
    ("fruits", "poissons"): 0.5,
    ("fruits", "légumineuses"): 0.4,

    # Sucré + salé inapproprié
    ("miel", "viandes"): 0.8,
    ("miel", "poissons"): 0.8,
    ("confiture", "viandes"): 0.9,
    ("confiture", "poissons"): 0.9,

    # PALATABILITÉ: Éviter associations multiples de féculents (pénalité très forte)
    # Un seul type de féculent par repas pour simplifier et améliorer la palatabilité
    ("féculents", "féculents"): 0.95,  # Pénalité quasi-rédhibitoire
    ("riz", "pâtes"): 0.95,
    ("riz", "pain"): 0.9,
    ("riz", "pommes de terre"): 0.95,
    ("pâtes", "pain"): 0.9,
    ("pâtes", "pommes de terre"): 0.95,
    ("pain", "pommes de terre"): 0.85,
    ("quinoa", "riz"): 0.95,
    ("quinoa", "pâtes"): 0.95,
    ("boulgour", "riz"): 0.95,
    ("boulgour", "pâtes"): 0.95,
    ("semoule", "riz"): 0.95,
    ("semoule", "pâtes"): 0.95,
}


def get_meal_coherence_score(food_category: str, meal_type: str) -> float:
    """
    Retourne le score de cohérence d'un aliment pour un type de repas.

    Args:
        food_category: Catégorie de l'aliment
        meal_type: Type de repas

    Returns:
        Score de 0 (incohérent) à 1 (parfait)
    """
    # Normaliser
    meal_type = meal_type.lower()

    # Chercher dans la matrice
    meal_rules = MEAL_CATEGORY_COHERENCE.get(meal_type, {})

    # Chercher la meilleure correspondance partielle
    for rule_category, score in meal_rules.items():
        if rule_category.lower() in food_category.lower():
            return score

    # Pas de règle spécifique = score neutre
    return 0.5


# Liste des mots-clés identifiant les féculents
# Avec et sans accents pour plus de robustesse
STARCH_KEYWORDS = [
    "feculent", "féculent", "riz", "pate", "pâte", "pates", "pâtes",
    "pain", "pomme de terre", "pommes de terre", "patate",
    "quinoa", "boulgour", "semoule", "couscous", "ble", "blé", "orge", "epeautre", "épeautre",
    "sarrasin", "millet", "avoine", "polenta", "patate douce", "igname",
    "manioc", "taro", "cereale", "céréale", "cereales", "céréales",
    "flocons", "muesli", "müesli", "granola"
]


def is_starch_food(category: str, food_name: str = "") -> bool:
    """
    Détecte si un aliment est un féculent.

    Args:
        category: Catégorie de l'aliment
        food_name: Nom de l'aliment (optionnel pour plus de précision)

    Returns:
        True si c'est un féculent
    """
    combined = (category + " " + food_name).lower()
    return any(keyword in combined for keyword in STARCH_KEYWORDS)


def get_starch_base_name(food_name: str) -> str:
    """
    Retourne le nom de base d'un féculent pour identifier les variations.
    Ex: "Patate douce (cuite)" -> "patate douce"
        "Riz basmati (cuit)" -> "riz basmati"

    Args:
        food_name: Nom de l'aliment

    Returns:
        Nom de base normalisé
    """
    name_lower = food_name.lower()

    # Supprimer les suffixes de cuisson
    for suffix in [" (cuit)", " (cuite)", " (cuites)", " (cuits)",
                   " (roti)", " (rotie)", " (roties)", " (rotis)",
                   " (bouilli)", " (bouillie)"]:
        name_lower = name_lower.replace(suffix, "")

    # Identifier le féculent de base
    for keyword in STARCH_KEYWORDS:
        if keyword in name_lower:
            # Retourner le premier mot-clé trouvé comme base
            # Ex: "pâtes complètes" -> "pates"
            if keyword in ["riz", "pate", "pâte", "pates", "pâtes", "pain",
                          "patate", "quinoa", "boulgour", "millet", "semoule"]:
                return keyword

    # Si aucun mot-clé spécifique, retourner le nom nettoyé
    return name_lower.strip()


def get_combination_penalty(category1: str, category2: str, food1_name: str = "", food2_name: str = "") -> float:
    """
    Retourne la pénalité pour une combinaison de catégories.

    Args:
        category1: Première catégorie
        category2: Deuxième catégorie
        food1_name: Nom du premier aliment (optionnel)
        food2_name: Nom du deuxième aliment (optionnel)

    Returns:
        Pénalité de 0 (OK) à 1 (très mauvais)
    """
    # Normaliser
    cat1 = category1.lower()
    cat2 = category2.lower()

    # RÈGLE SPÉCIALE: Pénalité très forte si deux féculents dans le même repas
    if is_starch_food(cat1, food1_name) and is_starch_food(cat2, food2_name):
        # Ne pas pénaliser si c'est exactement le même aliment (peu probable mais sécurité)
        if food1_name.lower() != food2_name.lower():
            return 0.95  # Pénalité quasi-rédhibitoire

    # Chercher dans les deux sens pour les autres combinaisons
    for (c1, c2), penalty in INCOMPATIBLE_COMBINATIONS.items():
        if (c1 in cat1 and c2 in cat2) or (c1 in cat2 and c2 in cat1):
            return penalty

    # Pas de pénalité
    return 0.0
