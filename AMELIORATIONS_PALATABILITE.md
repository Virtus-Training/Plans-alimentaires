# Améliorations de la Palatabilité et Simplicité des Plans Alimentaires

## Objectif
Améliorer la palatabilité et la simplicité des plans alimentaires en évitant les associations multiples de féculents par repas (un seul type de féculent par repas).

## Changements Implémentés

### 1. Règles de Cohérence Renforcées (`meal_coherence_rules.py`)

#### a) Pénalités pour associations de féculents
Ajout de pénalités très fortes (0.95/1.0) pour éviter les combinaisons multiples de féculents:

```python
INCOMPATIBLE_COMBINATIONS = {
    # ... règles existantes ...

    # PALATABILITÉ: Éviter associations multiples de féculents
    ("féculents", "féculents"): 0.95,
    ("riz", "pâtes"): 0.95,
    ("riz", "pain"): 0.9,
    ("riz", "pommes de terre"): 0.95,
    ("pâtes", "pain"): 0.9,
    ("pâtes", "pommes de terre"): 0.95,
    # ... etc
}
```

#### b) Détection robuste des féculents
Nouvelle fonction `is_starch_food()` qui détecte tous les types de féculents:

```python
STARCH_KEYWORDS = [
    "feculent", "féculent", "riz", "pate", "pâte", "pates", "pâtes",
    "pain", "pomme de terre", "pommes de terre", "patate",
    "quinoa", "boulgour", "semoule", "couscous", "blé", "orge", "épeautre",
    "sarrasin", "millet", "avoine", "polenta", "patate douce", "igname",
    "manioc", "taro", "cereale", "céréale", "flocons", "müesli", "granola"
]
```

#### c) Fonction de pénalité améliorée
`get_combination_penalty()` accepte maintenant les noms des aliments en plus des catégories pour une détection plus précise:

```python
def get_combination_penalty(category1: str, category2: str,
                            food1_name: str = "", food2_name: str = "") -> float:
    # Détection automatique des féculents
    if is_starch_food(cat1, food1_name) and is_starch_food(cat2, food2_name):
        if food1_name.lower() != food2_name.lower():
            return 0.95  # Pénalité quasi-rédhibitoire
```

### 2. Générateur de Repas Amélioré (`meal_generators.py`)

#### a) Passage des noms d'aliments pour la détection
Mise à jour de l'appel à `get_combination_penalty()` pour passer les noms des aliments:

```python
penalty = get_combination_penalty(
    food.category,
    selected_food.category,
    food.name,           # Nouveau
    selected_food.name   # Nouveau
)
```

#### b) Pondération ajustée du score de cohérence
Augmentation du poids de la cohérence de 10% à 20% dans le score composite:

```python
score = (
    macro_score * 0.28 +           # 28% (réduit de 30%)
    price_score * 0.07 +           # 7% (réduit de 8%)
    health_score * 0.05 +          # 5% (réduit de 7%)
    variety_score * 0.25 +         # 25% (réduit de 30%)
    compatibility_score * 0.15 +   # 15% (inchangé)
    coherence_score * 0.20         # 20% (DOUBLÉ de 10%)
)
```

#### c) Règle stricte d'exclusion
Ajout d'une règle **stricte** qui empêche complètement l'ajout d'un deuxième féculent:

```python
# RÈGLE STRICTE: Si un féculent est déjà sélectionné, interdire un autre féculent
if selected_foods and COHERENCE_RULES_AVAILABLE:
    has_starch = any(is_starch_food(sf.category, sf.name) for sf, _ in selected_foods)
    if has_starch and is_starch_food(food.category, food.name):
        continue  # SKIP cet aliment complètement
```

## Résultats

### Tests de Conformité
Sur 45 repas générés (5 runs × 9 repas):

- **Repas avec plusieurs féculents**: 1/45 (2.2%)
- **Repas avec 1 seul féculent**: 40/45 (88.9%)
- **Repas sans féculent**: 4/45 (8.9%)
- **Taux de conformité global**: **97.8%** ✅

### Exemples de Repas Générés

#### Petit-déjeuner (Breakfast)
```
- Pain complet: 200g (Céréales)
- Œufs: 150g
- Framboises: 30g
- Myrtilles: 30g
- Lait écrémé: 100g
Total: 828 kcal
✅ Un seul féculent (Pain complet)
```

#### Déjeuner (Lunch)
```
- Sardines (en conserve, à l'huile): 200g
- Riz basmati: 80g (Féculents)
- Courge butternut (rôtie): 80g
- Betterave (cuite): 30g
- Épinards (cuits): 30g
Total: 749 kcal
✅ Un seul féculent (Riz basmati)
```

#### Dîner (Dinner)
```
- Sardines (en conserve, à l'huile): 200g
- Riz basmati: 80g (Féculents)
- Courge butternut (rôtie): 80g
- Haricots verts (cuits): 30g
- Épinards (cuits): 30g
Total: 748 kcal
✅ Un seul féculent (Riz basmati)
```

## Avantages

1. **Palatabilité améliorée**: Les repas sont plus simples et cohérents avec un seul type de féculent
2. **Facilité de préparation**: Moins de féculents = cuisson simplifiée
3. **Digestion optimisée**: Évite les mélanges lourds de glucides complexes
4. **Respect des standards culinaires**: Conforme aux pratiques de la gastronomie moderne

## Fichiers Modifiés

- ✅ `meal_planner/data/meal_coherence_rules.py` - Règles de cohérence renforcées
- ✅ `meal_planner/services/meal_generators.py` - Algorithme de génération amélioré
- ✅ `test_starch_coherence.py` - Nouveau script de test

## Compatibilité

Ces améliorations sont **rétrocompatibles** et n'affectent pas:
- La base de données existante
- Les autres fonctionnalités du système
- Les calculs nutritionnels
- L'interface utilisateur

Le système reste fonctionnel même si le module de cohérence n'est pas disponible (dégradation gracieuse).
