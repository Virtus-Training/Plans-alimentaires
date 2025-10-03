"""
Module de gestion de la saisonnalité des aliments.
Favorise les aliments de saison pour des repas plus écologiques et économiques.
"""

from typing import Dict, List
from datetime import datetime
from enum import Enum


class Season(Enum):
    """Énumération des saisons."""
    SPRING = "spring"  # Mars, Avril, Mai
    SUMMER = "summer"  # Juin, Juillet, Août
    FALL = "fall"      # Septembre, Octobre, Novembre
    WINTER = "winter"  # Décembre, Janvier, Février


# Aliments de saison par mois (France/Europe)
SEASONAL_FOODS: Dict[str, List[str]] = {
    # Printemps (Mars-Mai)
    "spring": [
        # Légumes
        "asperges", "artichaut", "épinards", "radis", "petits pois",
        "fèves", "laitue", "cresson", "oseille", "blettes",
        # Fruits
        "fraises", "rhubarbe", "cerises",
    ],

    # Été (Juin-Août)
    "summer": [
        # Légumes
        "tomates", "courgettes", "aubergines", "poivrons", "concombre",
        "haricots verts", "maïs", "fenouil", "laitue", "roquette",
        # Fruits
        "fraises", "framboises", "myrtilles", "cerises", "abricots",
        "pêches", "nectarines", "melons", "pastèque", "prunes",
    ],

    # Automne (Septembre-Novembre)
    "fall": [
        # Légumes
        "potiron", "courge", "champignons", "poireaux", "choux",
        "betterave", "céleri", "panais", "topinambour", "rutabaga",
        "brocoli", "chou-fleur", "épinards",
        # Fruits
        "pommes", "poires", "raisins", "figues", "coings",
        "châtaignes", "noix", "noisettes",
    ],

    # Hiver (Décembre-Février)
    "winter": [
        # Légumes
        "choux", "poireaux", "carottes", "navets", "céleri",
        "endives", "mâche", "potiron", "courge", "topinambour",
        "panais", "rutabaga", "salsifis",
        # Fruits
        "pommes", "poires", "oranges", "clémentines", "mandarines",
        "pamplemousses", "kiwis", "châtaignes",
    ],
}

# Aliments disponibles toute l'année
ALL_YEAR_FOODS: List[str] = [
    # Protéines
    "poulet", "boeuf", "porc", "dinde", "œufs",
    "saumon", "thon", "cabillaud", "sardines",
    "tofu", "tempeh", "seitan",
    "lentilles", "pois chiches", "haricots",

    # Féculents
    "riz", "pâtes", "pain", "quinoa", "boulgour",
    "pommes de terre",

    # Produits laitiers
    "lait", "yaourt", "fromage", "fromage blanc",

    # Basiques
    "oignons", "ail", "échalotes",
]


def get_current_season() -> Season:
    """
    Détermine la saison actuelle basée sur la date.

    Returns:
        Season: La saison actuelle
    """
    month = datetime.now().month

    if 3 <= month <= 5:
        return Season.SPRING
    elif 6 <= month <= 8:
        return Season.SUMMER
    elif 9 <= month <= 11:
        return Season.FALL
    else:  # 12, 1, 2
        return Season.WINTER


def is_food_in_season(food_name: str, season: Season = None) -> bool:
    """
    Vérifie si un aliment est de saison.

    Args:
        food_name: Nom de l'aliment
        season: Saison à vérifier (None = saison actuelle)

    Returns:
        bool: True si l'aliment est de saison ou disponible toute l'année
    """
    if season is None:
        season = get_current_season()

    # Normaliser le nom de l'aliment
    food_lower = food_name.lower().strip()

    # Vérifier si c'est un aliment toute l'année
    if any(food_lower in all_year.lower() for all_year in ALL_YEAR_FOODS):
        return True

    # Vérifier si c'est un aliment de saison
    seasonal_list = SEASONAL_FOODS.get(season.value, [])
    return any(food_lower in seasonal.lower() for seasonal in seasonal_list)


def get_seasonal_bonus(food_name: str, season: Season = None) -> float:
    """
    Calcule un bonus de saisonnalité pour un aliment.

    Args:
        food_name: Nom de l'aliment
        season: Saison à vérifier (None = saison actuelle)

    Returns:
        float: Bonus entre 1.0 (pas de bonus) et 1.5 (fort bonus)
    """
    if is_food_in_season(food_name, season):
        return 1.3  # Bonus de 30% pour les aliments de saison
    else:
        return 0.8  # Malus de 20% pour les aliments hors saison


def get_seasonal_foods_list(season: Season = None) -> List[str]:
    """
    Retourne la liste des aliments de saison.

    Args:
        season: Saison à vérifier (None = saison actuelle)

    Returns:
        List[str]: Liste des aliments de saison + aliments toute l'année
    """
    if season is None:
        season = get_current_season()

    seasonal = SEASONAL_FOODS.get(season.value, [])
    return seasonal + ALL_YEAR_FOODS


def get_season_name(season: Season = None) -> str:
    """
    Retourne le nom de la saison en français.

    Args:
        season: Saison (None = saison actuelle)

    Returns:
        str: Nom de la saison en français
    """
    if season is None:
        season = get_current_season()

    names = {
        Season.SPRING: "Printemps",
        Season.SUMMER: "Été",
        Season.FALL: "Automne",
        Season.WINTER: "Hiver"
    }

    return names.get(season, "Inconnu")


def get_seasonal_info() -> Dict:
    """
    Retourne les informations de saisonnalité actuelles.

    Returns:
        Dict: Informations sur la saison actuelle
    """
    season = get_current_season()
    seasonal_foods = SEASONAL_FOODS.get(season.value, [])

    return {
        "season": season.value,
        "season_name": get_season_name(season),
        "month": datetime.now().month,
        "seasonal_foods_count": len(seasonal_foods),
        "all_year_foods_count": len(ALL_YEAR_FOODS),
        "seasonal_foods": seasonal_foods[:10],  # Premiers 10
    }


# Pour faciliter l'intégration
def apply_seasonal_boost_to_foods(foods: List, season: Season = None) -> List:
    """
    Applique un boost de variété aux aliments de saison.

    Args:
        foods: Liste d'objets Food
        season: Saison à considérer (None = actuelle)

    Returns:
        List: Liste modifiée (modification in-place aussi)
    """
    for food in foods:
        bonus = get_seasonal_bonus(food.name, season)
        # Augmenter l'indice de variété pour les aliments de saison
        if bonus > 1.0:
            food.variety_index = min(10, food.variety_index + 2)
        elif bonus < 1.0:
            food.variety_index = max(1, food.variety_index - 1)

    return foods
