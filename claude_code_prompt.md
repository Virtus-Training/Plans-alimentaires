# Prompt pour Claude Code - Développement Meal Planner Pro

Bonjour Claude Code,

Je souhaite développer un **générateur de plans alimentaires personnalisés** en Python avec une architecture MVC stricte. Voici le contexte complet du projet :

## 🎯 Objectif du Projet

Créer une application desktop permettant de générer automatiquement des plans alimentaires quotidiens/hebdomadaires basés sur des objectifs macronutritionnels (calories, protéines, glucides, lipides). L'application est destinée à un usage personnel mono-utilisateur.

## 🏗️ Architecture Technique

**Stack technologique :**
- Python 3.10+
- PyQt6 pour l'interface graphique
- SQLite3 avec SQLAlchemy pour la base de données
- SciPy pour l'optimisation
- ReportLab pour export PDF
- openpyxl pour export Excel

**Architecture MVC stricte :**
```
meal_planner/
├── main.py                 # Point d'entrée
├── config.py              # Configuration
├── requirements.txt
├── models/                # Couche Modèle
│   ├── food.py           # Classe Food
│   ├── meal.py           # Classe Meal
│   ├── meal_plan.py      # Classe MealPlan
│   ├── nutrition.py      # Classe NutritionTarget
│   └── database.py       # DatabaseManager
├── views/                 # Couche Vue
│   ├── main_window.py    # Fenêtre principale
│   ├── settings_panel.py # Panneau paramètres
│   ├── meal_plan_display.py
│   └── food_manager.py
├── controllers/           # Couche Contrôleur
│   ├── meal_plan_controller.py
│   ├── food_controller.py
│   └── export_controller.py
├── services/              # Services métier
│   ├── meal_generator.py # Algorithme génération
│   ├── macro_calculator.py
│   └── optimizer.py
├── utils/
│   ├── validators.py
│   └── logger.py
└── data/
    ├── foods.db          # Base SQLite
    └── presets/
        └── default_foods.json
```

## 📋 Fonctionnalités Principales

### 1. Configuration des Objectifs (via sliders PyQt6)
- Calories : 1200-4000 kcal (pas de 50)
- Protéines : 50-300g (pas de 5g)
- Glucides : 50-500g (pas de 10g)
- Lipides : 30-150g (pas de 5g)
- Affichage en temps réel de la répartition en %

### 2. Options via cases à cocher
- Nombre de repas : 3, 4, 5 ou 6
- Préférences : Végétarien, Végan, Sans gluten, Sans lactose
- Durée du plan : 1 à 14 jours

### 3. Génération Automatique
- Algorithme d'optimisation (scipy.optimize.minimize)
- Respect des macros (tolérance ±5%)
- Variété alimentaire
- Filtrage selon préférences

### 4. Gestion de la Base d'Aliments
- CRUD complet sur les aliments
- Import/export JSON
- Recherche et filtres

### 5. Export
- PDF formaté (ReportLab)
- Excel avec feuilles par jour (openpyxl)
- JSON pour sauvegarde

## 🔧 Spécifications Techniques Détaillées

### Modèle Food
```python
@dataclass
class Food:
    id: Optional[int]
    name: str
    category: str
    calories: float      # pour 100g
    proteins: float
    carbs: float
    fats: float
    fibers: float
    tags: List[str]      # vegetarian, vegan, gluten_free, etc.
    
    def validate() -> tuple[bool, str]
    def calculate_for_quantity(quantity_grams: float) -> Dict[str, float]
```

### Modèle Meal
```python
@dataclass
class Meal:
    id: Optional[int]
    name: str
    meal_type: str       # breakfast, lunch, dinner, snack
    foods: List[Tuple[Food, float]]  # (Food, quantity)
    target_calories: float
    day_number: int
    
    def calculate_macros() -> Dict[str, float]
    def add_food(food: Food, quantity: float)
```

### Modèle MealPlan
```python
@dataclass
class MealPlan:
    id: Optional[int]
    duration_days: int
    meals: List[Meal]
    nutrition_target: NutritionTarget
    notes: str
    
    def calculate_daily_totals(day: int) -> Dict[str, float]
    def validate_against_target(tolerance: float) -> Dict
```

### Algorithme de Génération (services/meal_generator.py)
L'algorithme doit :
1. Filtrer les aliments selon préférences diététiques
2. Répartir les macros sur les repas selon distribution choisie
3. Pour chaque repas :
   - Sélectionner 3-8 aliments variés (protéines, glucides, légumes, lipides)
   - Utiliser scipy.optimize.minimize pour optimiser les quantités
   - Fonction objective : minimiser écart avec macros cibles
   - Contraintes : 30g-500g par aliment
4. Valider le plan complet (tolérance ±5%)

### Base de Données SQLite
```sql
-- Tables
CREATE TABLE foods (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    category TEXT,
    calories REAL,
    proteins REAL,
    carbs REAL,
    fats REAL,
    fibers REAL,
    tags TEXT  -- JSON
);

CREATE TABLE meal_plans (...);
CREATE TABLE meals (...);
CREATE TABLE meal_foods (...);  -- Association
```

## 🎨 Interface Utilisateur (PyQt6)

### Fenêtre Principale (QMainWindow)
- **Panneau gauche (1/3)** : SettingsPanel
  - Sliders pour chaque macro avec affichage valeur
  - ComboBox nombre de repas
  - QCheckBox pour préférences
  - Bouton "Générer le plan" (gros, vert)

- **Panneau droit (2/3)** : MealPlanDisplay
  - ScrollArea avec liste des repas
  - Pour chaque repas : nom, aliments+quantités, macros
  - Bouton régénérer par repas
  - Récapitulatif journalier en bas

### Menu Bar
- Fichier : Nouveau, Charger, Gérer aliments, Quitter
- Export : PDF, Excel, JSON
- Aide : Documentation, À propos

## 📦 Ce que je souhaite que tu développes en PRIORITÉ

**Phase 1 - Fondations (À FAIRE MAINTENANT) :**

1. **Structure du projet**
   - Créer tous les dossiers et fichiers __init__.py
   - Générer requirements.txt
   - Créer config.py avec constantes

2. **Modèles de base**
   - `models/food.py` : Classe Food complète avec validation
   - `models/meal.py` : Classe Meal avec calculs
   - `models/meal_plan.py` : Classe MealPlan
   - `models/nutrition.py` : Classe NutritionTarget
   - `models/database.py` : DatabaseManager avec CRUD

3. **Base de données**
   - Créer schéma SQLite complet
   - Implémenter DatabaseManager
   - Créer default_foods.json avec 50-100 aliments courants

4. **Interface de base**
   - `main.py` : Point d'entrée avec initialisation
   - `views/main_window.py` : Structure fenêtre principale
   - `views/settings_panel.py` : Panneau avec sliders fonctionnels
   - Connexion basique Vue → Contrôleur (juste afficher valeurs pour l'instant)

## ⚠️ Contraintes Importantes

- **Architecture MVC stricte** : Pas de logique métier dans la Vue, pas d'accès direct Vue ↔ Modèle
- **Validation robuste** : Toutes les entrées utilisateur doivent être validées
- **Gestion d'erreurs** : Try-catch partout avec messages clairs, jamais de crash
- **PEP 8** : Code conforme aux standards Python
- **Docstrings** : Toutes classes et méthodes documentées
- **Type hints** : Utiliser les annotations de type

## 🎯 Résultat Attendu pour Phase 1

À la fin de cette première phase, l'application doit :
- ✅ Se lancer sans erreur
- ✅ Afficher la fenêtre principale avec panneau de paramètres
- ✅ Permettre d'ajuster les sliders et voir les valeurs
- ✅ Avoir une base de données initialisée avec des aliments
- ✅ Avoir tous les modèles fonctionnels et testables

**Ne pas implémenter encore :**
- ❌ Algorithme de génération (Phase 2)
- ❌ Affichage des repas générés (Phase 2)
- ❌ Export PDF/Excel (Phase 3)
- ❌ Gestionnaire d'aliments complet (Phase 3)

## 🚀 Instructions de Démarrage

1. Crée la structure complète du projet
2. Génère requirements.txt avec toutes les dépendances
3. Implémente les modèles avec validation complète
4. Crée la base de données avec schéma et données exemple
5. Développe l'interface basique fonctionnelle
6. Assure-toi que tout se lance sans erreur

**Style de code attendu :**
- Clean code, lisible, commenté
- Séparation claire des responsabilités
- Code réutilisable et maintenable
- Gestion des erreurs élégante

## 📝 Questions à clarifier si besoin

- Préfères-tu une approche minimaliste d'abord ou tout implémenter d'un coup ?
- Veux-tu que je génère aussi des tests unitaires pour les modèles ?
- Faut-il un système de logging dès le début ?

Merci de développer cette Phase 1 en respectant scrupuleusement l'architecture MVC et en produisant du code de qualité production !

---

**Note importante :** J'ai un cahier des charges complet de 200+ lignes détaillant chaque aspect. Si tu as besoin de précisions sur l'algorithme d'optimisation, les détails d'implémentation des contrôleurs, ou tout autre aspect, demande-moi !