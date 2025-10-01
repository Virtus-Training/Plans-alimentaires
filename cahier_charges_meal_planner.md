# Cahier des Charges - Générateur de Plans Alimentaires Personnalisés

## 1. Présentation du Projet

### 1.1 Contexte
Développement d'une application desktop en Python permettant la génération automatique de plans alimentaires personnalisés basés sur des objectifs macronutritionnels.

### 1.2 Objectifs
- Générer des plans alimentaires quotidiens/hebdomadaires respectant des macros définies
- Offrir une interface intuitive avec contrôles interactifs (sliders, cases à cocher)
- Permettre la sauvegarde et l'export des plans générés
- Faciliter la gestion d'une base de données d'aliments personnalisable

### 1.3 Utilisateur cible
Application mono-utilisateur destinée à un usage personnel.

---

## 2. Architecture Technique - Modèle MVC

### 2.1 Justification de l'architecture MVC
- **Séparation des responsabilités** : logique métier, interface et données séparées
- **Maintenabilité** : modifications facilitées sur chaque couche indépendamment
- **Testabilité** : tests unitaires simplifiés pour chaque composant
- **Évolutivité** : ajout de fonctionnalités sans refonte complète

### 2.2 Structure des répertoires
```
meal_planner/
│
├── main.py                      # Point d'entrée de l'application
├── requirements.txt             # Dépendances Python
├── config.py                    # Configuration globale
│
├── models/                      # Couche Modèle
│   ├── __init__.py
│   ├── food.py                  # Classe Food (aliment)
│   ├── meal.py                  # Classe Meal (repas)
│   ├── meal_plan.py             # Classe MealPlan (plan alimentaire)
│   ├── nutrition.py             # Classe NutritionTarget (objectifs macros)
│   └── database.py              # Gestion de la base de données
│
├── views/                       # Couche Vue
│   ├── __init__.py
│   ├── main_window.py           # Fenêtre principale
│   ├── settings_panel.py        # Panneau de paramétrage
│   ├── meal_plan_display.py    # Affichage du plan généré
│   ├── food_manager.py          # Gestion des aliments
│   └── widgets/                 # Composants réutilisables
│       ├── __init__.py
│       ├── macro_slider.py      # Slider personnalisé pour macros
│       └── meal_card.py         # Carte d'affichage de repas
│
├── controllers/                 # Couche Contrôleur
│   ├── __init__.py
│   ├── meal_plan_controller.py  # Contrôleur principal
│   ├── food_controller.py       # Gestion des aliments
│   └── export_controller.py     # Export des plans
│
├── services/                    # Services métier
│   ├── __init__.py
│   ├── meal_generator.py        # Algorithme de génération
│   ├── macro_calculator.py      # Calculs nutritionnels
│   └── optimizer.py             # Optimisation des combinaisons
│
├── data/                        # Données
│   ├── foods.db                 # Base de données SQLite
│   └── presets/                 # Préréglages
│       └── default_foods.json
│
└── utils/                       # Utilitaires
    ├── __init__.py
    ├── validators.py            # Validation des données
    └── exporters.py             # Export PDF/Excel
```

---

## 3. Spécifications Fonctionnelles

### 3.1 Gestion des Objectifs Macronutritionnels

#### 3.1.1 Paramètres ajustables (via sliders)
- **Calories totales** : 1200 - 4000 kcal (pas de 50)
- **Protéines** : 50g - 300g (pas de 5g)
- **Glucides** : 50g - 500g (pas de 10g)
- **Lipides** : 30g - 150g (pas de 5g)

#### 3.1.2 Affichage en temps réel
- Valeurs numériques à côté de chaque slider
- Pourcentage de répartition macronutritionnelle (P/G/L)
- Alerte visuelle si les macros sont déséquilibrées

### 3.2 Configuration du Plan

#### 3.2.1 Cases à cocher pour options
- **Nombre de repas** : ☐ 3 repas ☐ 4 repas ☐ 5 repas ☐ 6 repas
- **Répartition** : ☐ Équilibrée ☐ Petit-déjeuner léger ☐ Dîner léger
- **Préférences** : 
  - ☐ Végétarien
  - ☐ Sans lactose
  - ☐ Sans gluten
  - ☐ Faible en sodium
- **Types de repas** :
  - ☐ Inclure collations
  - ☐ Privilégier aliments simples
  - ☐ Autoriser répétitions

#### 3.2.2 Contraintes temporelles
- Période du plan : ☐ 1 jour ☐ 3 jours ☐ 7 jours ☐ 14 jours

### 3.3 Génération du Plan Alimentaire

#### 3.3.1 Algorithme de génération
L'algorithme doit :
1. Récupérer les objectifs macros et contraintes utilisateur
2. Filtrer les aliments selon les préférences (végétarien, allergies, etc.)
3. Répartir les macros sur les repas selon la distribution choisie
4. Sélectionner des combinaisons d'aliments optimisant :
   - Proximité avec les objectifs macros (tolérance ±5%)
   - Variété alimentaire
   - Équilibre micronutritionnel (si données disponibles)
5. Générer les quantités en grammes pour chaque aliment
6. Vérifier la cohérence nutritionnelle totale

#### 3.3.2 Boutons d'action
- **Générer** : création d'un nouveau plan
- **Régénérer un repas** : regénération d'un repas spécifique
- **Ajuster finement** : micro-ajustements manuels des quantités

### 3.4 Affichage du Plan Généré

#### 3.4.1 Vue principale
Pour chaque repas :
- **Nom du repas** (Petit-déjeuner, Déjeuner, Dîner, Collation)
- **Liste des aliments** avec quantités en grammes
- **Macros du repas** : Calories, Protéines, Glucides, Lipides
- **Icônes visuelles** pour identification rapide

#### 3.4.2 Récapitulatif journalier
- Total des macros consommées
- Comparaison objectifs vs réalisé (graphique en barres)
- Écart en % pour chaque macro

### 3.5 Gestion de la Base d'Aliments

#### 3.5.1 Consultation
- Liste scrollable des aliments disponibles
- Recherche par nom
- Filtres : catégorie, étiquettes diététiques
- Affichage des informations nutritionnelles complètes

#### 3.5.2 Ajout d'aliments
Formulaire avec champs :
- Nom de l'aliment (obligatoire)
- Catégorie : Viande, Poisson, Légume, Fruit, Féculents, Produits laitiers, Autres
- **Valeurs pour 100g** :
  - Calories (kcal)
  - Protéines (g)
  - Glucides (g)
  - Lipides (g)
  - Fibres (g) - optionnel
- Tags : ☐ Végétarien ☐ Végan ☐ Sans gluten ☐ Sans lactose

#### 3.5.3 Modification et suppression
- Édition des informations d'un aliment existant
- Suppression avec confirmation
- Import/export de la base (JSON/CSV)

### 3.6 Export et Sauvegarde

#### 3.6.1 Formats d'export
- **PDF** : plan formaté imprimable avec logo/titre personnalisable
- **Excel/CSV** : tableau avec détail des aliments et macros
- **JSON** : sauvegarde complète pour réimport

#### 3.6.2 Historique
- Sauvegarde automatique des 20 derniers plans générés
- Consultation et rechargement d'anciens plans
- Possibilité d'ajouter des notes à chaque plan

---

## 4. Spécifications Techniques

### 4.1 Technologies et Bibliothèques

#### 4.1.1 Langage et version
- **Python** : 3.10+

#### 4.1.2 Interface graphique
- **Tkinter** ou **PyQt6/PySide6** (recommandé pour interface moderne)
- **CustomTkinter** : alternative pour Tkinter avec apparence moderne

#### 4.1.3 Base de données
- **SQLite3** : base de données locale embarquée
- **SQLAlchemy** : ORM pour faciliter les interactions

#### 4.1.4 Traitement de données
- **Pandas** : manipulation de données nutritionnelles
- **NumPy** : calculs matriciels pour optimisation

#### 4.1.5 Génération/Export
- **ReportLab** ou **FPDF** : génération de PDF
- **openpyxl** : export Excel
- **Matplotlib/Plotly** : graphiques nutritionnels

#### 4.1.6 Optimisation
- **SciPy** (optimize) : algorithme d'optimisation pour sélection d'aliments

### 4.2 Détail de l'Architecture MVC

#### 4.2.1 MODÈLE (Model)

**Responsabilités** :
- Représentation des données métier
- Logique de gestion des données
- Interactions avec la base de données
- Validation des données

**Classes principales** :

```python
# models/food.py
class Food:
    - id: int
    - name: str
    - category: str
    - calories: float  # pour 100g
    - proteins: float
    - carbs: float
    - fats: float
    - fibers: float
    - tags: List[str]
    
    + validate()
    + to_dict()
    + from_dict()

# models/meal.py
class Meal:
    - id: int
    - name: str
    - meal_type: str  # breakfast, lunch, dinner, snack
    - foods: List[Tuple[Food, float]]  # (food, quantity_in_grams)
    - target_calories: float
    
    + calculate_macros()
    + add_food(food, quantity)
    + remove_food(food)
    + get_total_weight()

# models/meal_plan.py
class MealPlan:
    - id: int
    - date_created: datetime
    - duration_days: int
    - meals: List[Meal]
    - nutrition_target: NutritionTarget
    - notes: str
    
    + calculate_daily_totals()
    + validate_against_target()
    + get_macro_distribution()

# models/nutrition.py
class NutritionTarget:
    - calories: float
    - proteins: float
    - carbs: float
    - fats: float
    - num_meals: int
    - meal_distribution: dict
    - dietary_preferences: List[str]
    
    + validate_balance()
    + get_macro_percentages()
    + distribute_across_meals()
```

**Base de données** :
- Tables : `foods`, `meals`, `meal_plans`, `meal_foods` (association)
- Indexes sur colonnes fréquemment requêtées (name, category, tags)

#### 4.2.2 VUE (View)

**Responsabilités** :
- Affichage de l'interface utilisateur
- Capture des événements utilisateur (clics, modifications sliders)
- Mise à jour visuelle en réponse aux données du modèle
- Aucune logique métier

**Composants principaux** :

```python
# views/main_window.py
class MainWindow:
    + __init__(controller)
    + setup_ui()
    + show()
    
    # Zones de l'interface
    - settings_panel: SettingsPanel
    - meal_plan_display: MealPlanDisplay
    - food_manager_button
    - menu_bar
    
# views/settings_panel.py
class SettingsPanel:
    + __init__()
    + create_macro_sliders()
    + create_options_checkboxes()
    + get_user_inputs()
    
    # Widgets
    - calories_slider: MacroSlider
    - proteins_slider: MacroSlider
    - carbs_slider: MacroSlider
    - fats_slider: MacroSlider
    - num_meals_checkboxes
    - dietary_preferences_checkboxes
    - generate_button
    
    # Callbacks (connectés au contrôleur)
    + on_generate_clicked()
    + on_slider_changed(value)

# views/meal_plan_display.py
class MealPlanDisplay:
    + __init__()
    + display_meal_plan(meal_plan)
    + clear()
    + highlight_macro_difference(target, actual)
    
    # Composants
    - meal_cards: List[MealCard]
    - summary_panel
    - chart_widget

# views/food_manager.py
class FoodManagerWindow:
    + __init__(controller)
    + display_foods(foods)
    + show_add_food_dialog()
    + show_edit_food_dialog(food)
    
    # Actions
    + on_add_food()
    + on_edit_food(food_id)
    + on_delete_food(food_id)
    + on_import_foods()
    + on_export_foods()
```

**Principes de design** :
- Layout responsive avec redimensionnement
- Palette de couleurs cohérente
- Feedback visuel immédiat (changement sliders → affichage valeurs)
- Messages d'erreur/succès non-intrusifs

#### 4.2.3 CONTRÔLEUR (Controller)

**Responsabilités** :
- Liaison entre Vue et Modèle
- Traitement des actions utilisateur
- Orchestration des services métier
- Mise à jour de la Vue selon l'état du Modèle

**Classes principales** :

```python
# controllers/meal_plan_controller.py
class MealPlanController:
    + __init__(model, view)
    
    - meal_generator: MealGenerator
    - current_meal_plan: MealPlan
    
    + generate_meal_plan(nutrition_target, preferences)
    + regenerate_meal(meal_index)
    + save_meal_plan()
    + load_meal_plan(plan_id)
    + adjust_meal_quantity(meal_id, food_id, new_quantity)
    
    # Handlers des événements Vue
    + handle_generate_button()
    + handle_slider_change()
    + handle_regenerate_meal(meal_id)

# controllers/food_controller.py
class FoodController:
    + __init__(model, view)
    
    + get_all_foods()
    + search_foods(query, filters)
    + add_food(food_data)
    + update_food(food_id, food_data)
    + delete_food(food_id)
    + import_foods(file_path)
    + export_foods(file_path, format)

# controllers/export_controller.py
class ExportController:
    + __init__()
    
    + export_to_pdf(meal_plan, file_path)
    + export_to_excel(meal_plan, file_path)
    + export_to_json(meal_plan, file_path)
```

**Communication** :
- Vue → Contrôleur : via callbacks/signals
- Contrôleur → Modèle : appels de méthodes directs
- Modèle → Vue : via le Contrôleur (pattern Observer optionnel)

### 4.3 Services Métier

#### 4.3.1 Générateur de repas (MealGenerator)

```python
class MealGenerator:
    + generate(nutrition_target, food_database, preferences)
    
    # Méthodes privées
    - filter_foods_by_preferences(foods, preferences)
    - distribute_macros_across_meals(nutrition_target)
    - select_foods_for_meal(meal_target, available_foods)
    - optimize_food_quantities(selected_foods, meal_target)
```

**Algorithme de sélection** :
1. **Filtrage initial** : élimination des aliments non conformes aux préférences
2. **Sélection par catégorie** : choix d'aliments variés (protéines, glucides, lipides, légumes)
3. **Optimisation** : utilisation de `scipy.optimize.minimize` pour trouver les quantités
   - Fonction objective : minimiser l'écart avec les macros cibles
   - Contraintes : quantités min/max réalistes (50g - 500g par aliment)
4. **Validation** : vérification de la cohérence nutritionnelle

#### 4.3.2 Calculateur de macros (MacroCalculator)

```python
class MacroCalculator:
    + calculate_meal_macros(foods_with_quantities)
    + calculate_daily_totals(meal_plan)
    + compare_with_target(actual, target)
    + calculate_macro_percentages(proteins, carbs, fats)
```

### 4.4 Gestion des Données

#### 4.4.1 Schéma de base de données

```sql
-- Table des aliments
CREATE TABLE foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    calories REAL,
    proteins REAL,
    carbs REAL,
    fats REAL,
    fibers REAL,
    tags TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des plans alimentaires
CREATE TABLE meal_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_days INTEGER,
    target_calories REAL,
    target_proteins REAL,
    target_carbs REAL,
    target_fats REAL,
    preferences TEXT,  -- JSON
    notes TEXT
);

-- Table des repas
CREATE TABLE meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_plan_id INTEGER,
    name TEXT,
    meal_type TEXT,
    day_number INTEGER,
    FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id)
);

-- Table d'association repas-aliments
CREATE TABLE meal_foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id INTEGER,
    food_id INTEGER,
    quantity_grams REAL,
    FOREIGN KEY (meal_id) REFERENCES meals(id),
    FOREIGN KEY (food_id) REFERENCES foods(id)
);
```

#### 4.4.2 Fichier de configuration (config.py)

```python
# Configuration de l'application
APP_NAME = "Meal Planner Pro"
VERSION = "1.0.0"

# Chemins
DATABASE_PATH = "data/foods.db"
EXPORT_DIRECTORY = "exports/"
BACKUP_DIRECTORY = "backups/"

# Limites nutritionnelles
MACRO_RANGES = {
    "calories": (1200, 4000, 50),  # (min, max, step)
    "proteins": (50, 300, 5),
    "carbs": (50, 500, 10),
    "fats": (30, 150, 5)
}

# Tolérance d'optimisation
MACRO_TOLERANCE = 0.05  # ±5%

# Préréglages
DEFAULT_MEAL_DISTRIBUTION = {
    3: {"breakfast": 0.30, "lunch": 0.40, "dinner": 0.30},
    4: {"breakfast": 0.25, "lunch": 0.35, "snack": 0.10, "dinner": 0.30},
    5: {"breakfast": 0.20, "snack1": 0.10, "lunch": 0.35, "snack2": 0.10, "dinner": 0.25}
}

FOOD_CATEGORIES = [
    "Viandes", "Poissons", "Œufs", "Produits laitiers",
    "Féculents", "Légumes", "Fruits", "Légumineuses",
    "Noix et graines", "Matières grasses", "Autres"
]

DIETARY_TAGS = [
    "vegetarian", "vegan", "gluten_free", "lactose_free",
    "low_sodium", "high_protein", "low_carb"
]
```

---

## 5. Spécifications Non-Fonctionnelles

### 5.1 Performance
- Génération d'un plan alimentaire : < 3 secondes
- Recherche dans la base d'aliments : < 0.5 seconde
- Temps de démarrage de l'application : < 2 secondes
- Support d'une base de données jusqu'à 5000 aliments sans dégradation

### 5.2 Utilisabilité
- Interface intuitive ne nécessitant pas de formation
- Raccourcis clavier pour actions fréquentes (Ctrl+G : générer, Ctrl+S : sauvegarder, etc.)
- Tooltips sur tous les contrôles
- Messages d'erreur explicites avec suggestions

### 5.3 Fiabilité
- Validation de toutes les entrées utilisateur
- Gestion des erreurs avec messages appropriés (pas de crash)
- Sauvegarde automatique toutes les 5 minutes
- Backup automatique de la base de données hebdomadaire

### 5.4 Maintenabilité
- Code commenté (docstrings pour toutes les classes et méthodes)
- Respect de PEP 8 (conventions Python)
- Logging des événements importants et erreurs
- Tests unitaires pour fonctions critiques (couverture > 70%)

### 5.5 Portabilité
- Compatibilité : Windows 10/11, macOS 11+, Linux (Ubuntu 20.04+)
- Installation simplifiée via requirements.txt
- Possibilité de création d'exécutable autonome (PyInstaller)

### 5.6 Sécurité
- Validation et sanitization des entrées
- Pas de stockage de données sensibles
- Exports sécurisés (permissions fichiers appropriées)

---

## 6. Étapes de Développement

### Phase 1 : Fondations (2 semaines)
- [ ] Configuration de l'environnement de développement
- [ ] Création de la structure MVC
- [ ] Mise en place de la base de données SQLite
- [ ] Implémentation des modèles de base (Food, Meal, MealPlan)
- [ ] Création d'un dataset initial d'aliments (50-100 aliments communs)

### Phase 2 : Interface de base (2 semaines)
- [ ] Développement de la fenêtre principale
- [ ] Création des sliders pour macros
- [ ] Implémentation des cases à cocher
- [ ] Panneau d'affichage simple des repas générés
- [ ] Connexion Vue-Contrôleur pour actions basiques

### Phase 3 : Logique de génération (3 semaines)
- [ ] Développement de l'algorithme de sélection d'aliments
- [ ] Implémentation de l'optimisation des quantités
- [ ] Intégration des préférences et contraintes
- [ ] Tests et ajustements de l'algorithme
- [ ] Gestion de la variété alimentaire

### Phase 4 : Gestion des aliments (1 semaine)
- [ ] Interface de consultation des aliments
- [ ] Formulaires d'ajout/modification
- [ ] Fonction de recherche et filtres
- [ ] Import/export de la base d'aliments

### Phase 5 : Export et sauvegarde (1 semaine)
- [ ] Export PDF avec mise en forme
- [ ] Export Excel/CSV
- [ ] Historique des plans générés
- [ ] Système de notes et annotations

### Phase 6 : Peaufinage (2 semaines)
- [ ] Amélioration de l'interface graphique
- [ ] Ajout de graphiques nutritionnels
- [ ] Optimisation des performances
- [ ] Correction de bugs
- [ ] Documentation utilisateur
- [ ] Tests d'intégration

---

## 7. Livrables

### 7.1 Code source
- Repository Git avec historique de développement
- Code organisé selon architecture MVC
- Fichier requirements.txt
- README.md avec instructions d'installation

### 7.2 Base de données
- Fichier SQLite avec schéma complet
- Dataset d'aliments préchargés (minimum 100 aliments)
- Scripts de migration si nécessaire

### 7.3 Documentation
- Documentation technique (architecture, API des classes)
- Guide utilisateur (format PDF)
- Commentaires inline dans le code

### 7.4 Exécutable (optionnel)
- Application packagée (.exe pour Windows, .app pour macOS)
- Installeur si nécessaire

---

## 8. Critères d'Acceptance

### 8.1 Fonctionnels
✓ L'utilisateur peut définir des objectifs macros via sliders  
✓ L'utilisateur peut sélectionner nombre de repas et préférences via cases à cocher  
✓ L'application génère un plan alimentaire respectant les macros (±5%)  
✓ L'utilisateur peut régénérer un repas spécifique  
✓ L'utilisateur peut ajouter/modifier/supprimer des aliments  
✓ L'utilisateur peut exporter le plan en PDF et Excel  
✓ L'application sauvegarde automatiquement les plans générés  

### 8.2 Techniques
✓ Architecture MVC strictement respectée  
✓ Séparation claire des responsabilités  
✓ Aucune logique métier dans la Vue  
✓ Base de données SQLite fonctionnelle  
✓ Code conforme à PEP 8  
✓ Gestion d'erreurs robuste  

### 8.3 Qualité
✓ Interface intuitive et responsive  
✓ Temps de génération < 3 secondes  
✓ Aucun crash durant l'utilisation normale  
✓ Documentation complète et claire  

---

## 9. Exemples d'Utilisation

### Scénario 1 : Génération d'un plan de prise de masse
1. L'utilisateur ouvre l'application
2. Ajuste le slider calories à 3200 kcal
3. Ajuste protéines : 200g, glucides : 400g, lipides : 80g
4. Coche "5 repas" et "Inclure collations"
5. Coche "Privilégier aliments simples"
6. Clique sur "Générer"
7. Le plan s'affiche avec 5 repas équilibrés
8. L'utilisateur exporte en PDF pour impression

### Scénario 2 : Plan végétarien pour sèche
1. L'utilisateur ajuste calories à 1800 kcal
2. Protéines : 140g, glucides : 150g, lipides : 60g
3. Coche "Végétarien" et "4 repas"
4. Génère le plan
5. N'aime pas le déjeuner proposé → clique sur "Régénérer ce repas"
6. Satisfait du résultat, sauvegarde le plan avec note "Semaine 1 - Sèche"

### Scénario 3 : Ajout d'un aliment personnalisé
1. L'utilisateur clique sur "Gérer les aliments"
2. Clique sur "Ajouter un aliment"
3. Remplit : Nom = "Tofu bio", Catégorie = "Protéines végétales"
4. Valeurs pour 100g : 120 kcal, 12g protéines, 2g glucides, 7g lipides
5. Coche tags : "Végétarien", "Végan"
6. Sauvegarde
7. L'aliment est maintenant disponible dans les générations

---

## 10. Évolutions Futures (Post-V1)

### Fonctionnalités avancées
- Gestion des micronutriments (vitamines, minéraux)
- Planification de courses automatique
- Calcul du coût estimé des repas
- Intégration de recettes (multi-ingrédients)
- Mode "reste de frigo" (génération à partir d'aliments disponibles)
- Synchronisation cloud multi-appareils
- Version mobile (React Native / Flutter)
- Suggestions basées sur historique et saisons
- Intégration API de bases nutritionnelles publiques (USDA, Ciqual)

### Améliorations techniques
- Migration vers PostgreSQL pour base plus robuste
- API REST pour accès externe
- Architecture microservices
- Tests automatisés (CI/CD)
- Containerisation (Docker)

---

## Annexes

### A. Exemples de données d'aliments

```json
{
  "name": "Poulet (blanc, grillé)",
  "category": "Viandes",
  "calories": 165,
  "proteins": 31,
  "carbs": 0,
  "fats": 3.6,
  "fibers": 0,
  "tags": ["high_protein", "low_carb"]
}
```

### B. Formules de calcul

**Calories totales d'un repas** :  
`Total = Σ(Aliment_i.calories × Quantité_i / 100)`

**Pourcentage macro** :  
`%P = (Protéines × 4) / Calories_totales × 100`  
`%G = (Glucides × 4) / Calories_totales × 100`  
`%L = (Lipides × 9) / Calories_totales × 100`

**Écart avec objectif** :  
`Écart(%) = |Réalisé - Objectif| / Objectif × 100`

### C. Bibliographie technique
- Documentation PyQt6 : https://doc.qt.io
- SQLAlchemy ORM : https://docs.sqlalchemy.org
- SciPy Optimization : https://docs.scipy.org/doc/scipy/reference/optimize.html
- ReportLab PDF : https://www.reportlab.com/docs/reportlab-userguide.pdf
- PEP 8 Style Guide : https://peps.python.org/pep-0008/

---

## 11. Spécifications Détaillées des Composants

### 11.1 Modèle - Implémentation détaillée

#### 11.1.1 Classe Food - Spécifications complètes

```python
# models/food.py
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

@dataclass
class Food:
    """
    Représente un aliment avec ses valeurs nutritionnelles pour 100g
    """
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    calories: float = 0.0
    proteins: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0
    fibers: float = 0.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def validate(self) -> tuple[bool, str]:
        """
        Valide les données de l'aliment
        Returns: (is_valid, error_message)
        """
        if not self.name or len(self.name.strip()) == 0:
            return False, "Le nom de l'aliment est obligatoire"
        
        if self.calories < 0 or self.proteins < 0 or self.carbs < 0 or self.fats < 0:
            return False, "Les valeurs nutritionnelles ne peuvent pas être négatives"
        
        # Vérification cohérence énergétique (approximative)
        calculated_calories = (self.proteins * 4) + (self.carbs * 4) + (self.fats * 9)
        if abs(calculated_calories - self.calories) > self.calories * 0.15:
            return False, "Incohérence entre calories et macronutriments"
        
        return True, ""
    
    def calculate_for_quantity(self, quantity_grams: float) -> Dict[str, float]:
        """
        Calcule les valeurs nutritionnelles pour une quantité donnée
        """
        factor = quantity_grams / 100.0
        return {
            "calories": self.calories * factor,
            "proteins": self.proteins * factor,
            "carbs": self.carbs * factor,
            "fats": self.fats * factor,
            "fibers": self.fibers * factor
        }
    
    def has_tag(self, tag: str) -> bool:
        """Vérifie si l'aliment possède un tag spécifique"""
        return tag in self.tags
    
    def to_dict(self) -> Dict:
        """Sérialisation en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "calories": self.calories,
            "proteins": self.proteins,
            "carbs": self.carbs,
            "fats": self.fats,
            "fibers": self.fibers,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Food':
        """Désérialisation depuis dictionnaire"""
        return cls(**data)
    
    def __str__(self) -> str:
        return f"{self.name} - {self.calories}kcal/100g (P:{self.proteins}g G:{self.carbs}g L:{self.fats}g)"
```

#### 11.1.2 Classe Meal - Spécifications complètes

```python
# models/meal.py
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from models.food import Food

@dataclass
class Meal:
    """
    Représente un repas composé de plusieurs aliments avec leurs quantités
    """
    id: Optional[int] = None
    name: str = ""
    meal_type: str = ""  # breakfast, lunch, dinner, snack
    foods: List[Tuple[Food, float]] = field(default_factory=list)  # (Food, quantity_in_grams)
    target_calories: float = 0.0
    day_number: int = 1
    
    def add_food(self, food: Food, quantity: float) -> None:
        """Ajoute un aliment au repas"""
        if quantity <= 0:
            raise ValueError("La quantité doit être positive")
        self.foods.append((food, quantity))
    
    def remove_food(self, food: Food) -> bool:
        """
        Retire un aliment du repas
        Returns: True si l'aliment a été trouvé et retiré
        """
        for i, (f, q) in enumerate(self.foods):
            if f.id == food.id:
                self.foods.pop(i)
                return True
        return False
    
    def update_food_quantity(self, food: Food, new_quantity: float) -> bool:
        """
        Met à jour la quantité d'un aliment dans le repas
        Returns: True si l'aliment a été trouvé et modifié
        """
        if new_quantity <= 0:
            raise ValueError("La quantité doit être positive")
        
        for i, (f, q) in enumerate(self.foods):
            if f.id == food.id:
                self.foods[i] = (f, new_quantity)
                return True
        return False
    
    def calculate_macros(self) -> Dict[str, float]:
        """
        Calcule les macros totaux du repas
        Returns: dict avec calories, proteins, carbs, fats, fibers
        """
        totals = {
            "calories": 0.0,
            "proteins": 0.0,
            "carbs": 0.0,
            "fats": 0.0,
            "fibers": 0.0
        }
        
        for food, quantity in self.foods:
            macros = food.calculate_for_quantity(quantity)
            for key in totals:
                totals[key] += macros[key]
        
        return totals
    
    def get_total_weight(self) -> float:
        """Retourne le poids total du repas en grammes"""
        return sum(quantity for _, quantity in self.foods)
    
    def get_food_count(self) -> int:
        """Retourne le nombre d'aliments différents dans le repas"""
        return len(self.foods)
    
    def get_deviation_from_target(self) -> float:
        """
        Calcule l'écart en % entre calories réelles et cible
        Returns: écart en pourcentage (positif si au-dessus, négatif si en-dessous)
        """
        if self.target_calories == 0:
            return 0.0
        
        actual_calories = self.calculate_macros()["calories"]
        return ((actual_calories - self.target_calories) / self.target_calories) * 100
    
    def to_dict(self) -> Dict:
        """Sérialisation en dictionnaire"""
        return {
            "id": self.id,
            "name": self.name,
            "meal_type": self.meal_type,
            "foods": [(f.to_dict(), q) for f, q in self.foods],
            "target_calories": self.target_calories,
            "day_number": self.day_number,
            "macros": self.calculate_macros()
        }
    
    def __str__(self) -> str:
        macros = self.calculate_macros()
        return f"{self.name} ({self.meal_type}) - {macros['calories']:.0f}kcal - {len(self.foods)} aliments"
```

#### 11.1.3 Classe MealPlan - Spécifications complètes

```python
# models/meal_plan.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from models.meal import Meal
from models.nutrition import NutritionTarget

@dataclass
class MealPlan:
    """
    Représente un plan alimentaire complet sur une ou plusieurs journées
    """
    id: Optional[int] = None
    date_created: datetime = field(default_factory=datetime.now)
    duration_days: int = 1
    meals: List[Meal] = field(default_factory=list)
    nutrition_target: Optional[NutritionTarget] = None
    notes: str = ""
    name: str = ""
    
    def add_meal(self, meal: Meal) -> None:
        """Ajoute un repas au plan"""
        self.meals.append(meal)
    
    def get_meals_by_day(self, day: int) -> List[Meal]:
        """Retourne tous les repas d'une journée spécifique"""
        return [m for m in self.meals if m.day_number == day]
    
    def get_meals_by_type(self, meal_type: str) -> List[Meal]:
        """Retourne tous les repas d'un type donné"""
        return [m for m in self.meals if m.meal_type == meal_type]
    
    def calculate_daily_totals(self, day: int = 1) -> Dict[str, float]:
        """
        Calcule les totaux nutritionnels pour une journée
        """
        day_meals = self.get_meals_by_day(day)
        
        totals = {
            "calories": 0.0,
            "proteins": 0.0,
            "carbs": 0.0,
            "fats": 0.0,
            "fibers": 0.0
        }
        
        for meal in day_meals:
            macros = meal.calculate_macros()
            for key in totals:
                totals[key] += macros[key]
        
        return totals
    
    def calculate_average_daily_totals(self) -> Dict[str, float]:
        """
        Calcule la moyenne des totaux sur tous les jours du plan
        """
        if self.duration_days == 0:
            return {"calories": 0, "proteins": 0, "carbs": 0, "fats": 0, "fibers": 0}
        
        total_sum = {"calories": 0.0, "proteins": 0.0, "carbs": 0.0, "fats": 0.0, "fibers": 0.0}
        
        for day in range(1, self.duration_days + 1):
            day_totals = self.calculate_daily_totals(day)
            for key in total_sum:
                total_sum[key] += day_totals[key]
        
        return {key: value / self.duration_days for key, value in total_sum.items()}
    
    def validate_against_target(self, tolerance: float = 0.05) -> Dict[str, any]:
        """
        Valide le plan par rapport aux objectifs nutritionnels
        Args:
            tolerance: tolérance en pourcentage (0.05 = ±5%)
        Returns:
            dict avec is_valid et détails des écarts
        """
        if not self.nutrition_target:
            return {"is_valid": False, "error": "Aucun objectif nutritionnel défini"}
        
        avg_totals = self.calculate_average_daily_totals()
        target = self.nutrition_target
        
        deviations = {
            "calories": (avg_totals["calories"] - target.calories) / target.calories,
            "proteins": (avg_totals["proteins"] - target.proteins) / target.proteins,
            "carbs": (avg_totals["carbs"] - target.carbs) / target.carbs,
            "fats": (avg_totals["fats"] - target.fats) / target.fats
        }
        
        is_valid = all(abs(dev) <= tolerance for dev in deviations.values())
        
        return {
            "is_valid": is_valid,
            "deviations": {k: v * 100 for k, v in deviations.items()},  # en %
            "actual": avg_totals,
            "target": target.to_dict()
        }
    
    def get_macro_distribution(self) -> Dict[str, float]:
        """
        Calcule la répartition en % des macronutriments
        Returns: dict avec pourcentages de protéines, glucides, lipides
        """
        avg_totals = self.calculate_average_daily_totals()
        
        total_calories = avg_totals["calories"]
        if total_calories == 0:
            return {"proteins": 0, "carbs": 0, "fats": 0}
        
        return {
            "proteins": (avg_totals["proteins"] * 4 / total_calories) * 100,
            "carbs": (avg_totals["carbs"] * 4 / total_calories) * 100,
            "fats": (avg_totals["fats"] * 9 / total_calories) * 100
        }
    
    def get_summary(self) -> str:
        """Génère un résumé textuel du plan"""
        avg = self.calculate_average_daily_totals()
        distribution = self.get_macro_distribution()
        
        summary = f"Plan alimentaire: {self.name or 'Sans nom'}\n"
        summary += f"Durée: {self.duration_days} jour(s)\n"
        summary += f"Nombre de repas: {len(self.meals)}\n\n"
        summary += f"Moyennes journalières:\n"
        summary += f"  Calories: {avg['calories']:.0f} kcal\n"
        summary += f"  Protéines: {avg['proteins']:.1f}g ({distribution['proteins']:.1f}%)\n"
        summary += f"  Glucides: {avg['carbs']:.1f}g ({distribution['carbs']:.1f}%)\n"
        summary += f"  Lipides: {avg['fats']:.1f}g ({distribution['fats']:.1f}%)\n"
        
        if self.notes:
            summary += f"\nNotes: {self.notes}"
        
        return summary
    
    def to_dict(self) -> Dict:
        """Sérialisation complète du plan"""
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created.isoformat(),
            "duration_days": self.duration_days,
            "meals": [m.to_dict() for m in self.meals],
            "nutrition_target": self.nutrition_target.to_dict() if self.nutrition_target else None,
            "notes": self.notes,
            "summary": {
                "daily_averages": self.calculate_average_daily_totals(),
                "macro_distribution": self.get_macro_distribution(),
                "validation": self.validate_against_target()
            }
        }
```

#### 11.1.4 Classe NutritionTarget - Spécifications complètes

```python
# models/nutrition.py
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class NutritionTarget:
    """
    Représente les objectifs nutritionnels journaliers
    """
    calories: float = 2000.0
    proteins: float = 150.0
    carbs: float = 200.0
    fats: float = 65.0
    num_meals: int = 3
    meal_distribution: Dict[str, float] = field(default_factory=dict)
    dietary_preferences: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialise la distribution par défaut si non fournie"""
        if not self.meal_distribution:
            self.meal_distribution = self._get_default_distribution()
    
    def _get_default_distribution(self) -> Dict[str, float]:
        """
        Retourne une distribution par défaut selon le nombre de repas
        """
        distributions = {
            3: {"breakfast": 0.30, "lunch": 0.40, "dinner": 0.30},
            4: {"breakfast": 0.25, "lunch": 0.35, "snack": 0.10, "dinner": 0.30},
            5: {"breakfast": 0.20, "snack1": 0.10, "lunch": 0.35, "snack2": 0.10, "dinner": 0.25},
            6: {"breakfast": 0.20, "snack1": 0.10, "lunch": 0.30, "snack2": 0.10, "dinner": 0.20, "snack3": 0.10}
        }
        return distributions.get(self.num_meals, distributions[3])
    
    def validate_balance(self) -> tuple[bool, str]:
        """
        Valide l'équilibre des macronutriments
        Returns: (is_valid, message)
        """
        # Vérification des valeurs positives
        if any(v <= 0 for v in [self.calories, self.proteins, self.carbs, self.fats]):
            return False, "Toutes les valeurs doivent être positives"
        
        # Calcul des calories théoriques
        calculated_calories = (self.proteins * 4) + (self.carbs * 4) + (self.fats * 9)
        
        # Tolérance de 10% sur la cohérence énergétique
        if abs(calculated_calories - self.calories) > self.calories * 0.10:
            return False, f"Incohérence: les macros donnent {calculated_calories:.0f}kcal mais l'objectif est {self.calories:.0f}kcal"
        
        # Vérification distribution des repas
        if abs(sum(self.meal_distribution.values()) - 1.0) > 0.01:
            return False, "La distribution des repas doit totaliser 100%"
        
        return True, "Objectifs valides"
    
    def get_macro_percentages(self) -> Dict[str, float]:
        """
        Calcule le pourcentage de chaque macro dans l'apport calorique
        """
        if self.calories == 0:
            return {"proteins": 0, "carbs": 0, "fats": 0}
        
        return {
            "proteins": (self.proteins * 4 / self.calories) * 100,
            "carbs": (self.carbs * 4 / self.calories) * 100,
            "fats": (self.fats * 9 / self.calories) * 100
        }
    
    def distribute_across_meals(self) -> Dict[str, Dict[str, float]]:
        """
        Répartit les macros sur les différents repas selon la distribution
        Returns: dict {meal_name: {calories, proteins, carbs, fats}}
        """
        meal_targets = {}
        
        for meal_name, proportion in self.meal_distribution.items():
            meal_targets[meal_name] = {
                "calories": self.calories * proportion,
                "proteins": self.proteins * proportion,
                "carbs": self.carbs * proportion,
                "fats": self.fats * proportion
            }
        
        return meal_targets
    
    def adjust_for_activity(self, activity_factor: float) -> 'NutritionTarget':
        """
        Crée un nouvel objectif ajusté selon le niveau d'activité
        Args:
            activity_factor: multiplicateur (1.2 = sédentaire, 1.9 = très actif)
        """
        return NutritionTarget(
            calories=self.calories * activity_factor,
            proteins=self.proteins * activity_factor,
            carbs=self.carbs * activity_factor,
            fats=self.fats * activity_factor,
            num_meals=self.num_meals,
            meal_distribution=self.meal_distribution.copy(),
            dietary_preferences=self.dietary_preferences.copy()
        )
    
    def has_preference(self, preference: str) -> bool:
        """Vérifie si une préférence diététique est active"""
        return preference in self.dietary_preferences
    
    def to_dict(self) -> Dict:
        """Sérialisation"""
        return {
            "calories": self.calories,
            "proteins": self.proteins,
            "carbs": self.carbs,
            "fats": self.fats,
            "num_meals": self.num_meals,
            "meal_distribution": self.meal_distribution,
            "dietary_preferences": self.dietary_preferences,
            "macro_percentages": self.get_macro_percentages()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NutritionTarget':
        """Désérialisation"""
        return cls(**data)
    
    def __str__(self) -> str:
        percentages = self.get_macro_percentages()
        return (f"Objectif: {self.calories:.0f}kcal - "
                f"P:{self.proteins:.0f}g ({percentages['proteins']:.0f}%) "
                f"G:{self.carbs:.0f}g ({percentages['carbs']:.0f}%) "
                f"L:{self.fats:.0f}g ({percentages['fats']:.0f}%)")
```

---

### 11.2 Services - Implémentation détaillée

#### 11.2.1 MealGenerator - Algorithme complet

```python
# services/meal_generator.py
import random
from typing import List, Dict, Tuple
import numpy as np
from scipy.optimize import minimize, LinearConstraint
from models.food import Food
from models.meal import Meal
from models.nutrition import NutritionTarget

class MealGenerator:
    """
    Service de génération de repas optimisés
    """
    
    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance
        self.min_food_quantity = 30  # grammes minimum par aliment
        self.max_food_quantity = 500  # grammes maximum par aliment
        self.max_foods_per_meal = 8  # nombre max d'aliments par repas
    
    def generate_meal_plan(
        self,
        nutrition_target: NutritionTarget,
        food_database: List[Food],
        duration_days: int = 1
    ) -> 'MealPlan':
        """
        Génère un plan alimentaire complet
        """
        from models.meal_plan import MealPlan
        
        plan = MealPlan(
            duration_days=duration_days,
            nutrition_target=nutrition_target
        )
        
        # Filtre les aliments selon préférences
        available_foods = self._filter_foods_by_preferences(
            food_database,
            nutrition_target.dietary_preferences
        )
        
        if len(available_foods) < 10:
            raise ValueError("Pas assez d'aliments disponibles pour générer un plan")
        
        # Récupère la distribution des repas
        meal_targets = nutrition_target.distribute_across_meals()
        
        # Génère les repas pour chaque jour
        for day in range(1, duration_days + 1):
            for meal_name, targets in meal_targets.items():
                meal = self._generate_single_meal(
                    meal_name=meal_name,
                    meal_type=self._get_meal_type(meal_name),
                    targets=targets,
                    available_foods=available_foods,
                    day_number=day
                )
                plan.add_meal(meal)
        
        return plan
    
    def _filter_foods_by_preferences(
        self,
        foods: List[Food],
        preferences: List[str]
    ) -> List[Food]:
        """
        Filtre les aliments selon les préférences diététiques
        """
        if not preferences:
            return foods
        
        filtered = []
        for food in foods:
            # Si végétarien, exclure viandes et poissons
            if "vegetarian" in preferences:
                if food.category in ["Viandes", "Poissons"]:
                    continue
            
            # Si végan, exclure en plus les produits laitiers et œufs
            if "vegan" in preferences:
                if food.category in ["Viandes", "Poissons", "Produits laitiers", "Œufs"]:
                    continue
            
            # Si sans gluten, vérifier les tags
            if "gluten_free" in preferences:
                if not food.has_tag("gluten_free") and food.category == "Féculents":
                    continue
            
            # Si sans lactose
            if "lactose_free" in preferences:
                if food.category == "Produits laitiers" and not food.has_tag("lactose_free"):
                    continue
            
            filtered.append(food)
        
        return filtered
    
    def _get_meal_type(self, meal_name: str) -> str:
        """Détermine le type de repas à partir du nom"""
        meal_name_lower = meal_name.lower()
        if "breakfast" in meal_name_lower or "petit" in meal_name_lower:
            return "breakfast"
        elif "lunch" in meal_name_lower or "déjeuner" in meal_name_lower:
            return "lunch"
        elif "dinner" in meal_name_lower or "dîner" in meal_name_lower:
            return "dinner"
        else:
            return "snack"
    
    def _generate_single_meal(
        self,
        meal_name: str,
        meal_type: str,
        targets: Dict[str, float],
        available_foods: List[Food],
        day_number: int
    ) -> Meal:
        """
        Génère un repas unique optimisé
        """
        meal = Meal(
            name=meal_name,
            meal_type=meal_type,
            target_calories=targets["calories"],
            day_number=day_number
        )
        
        # Sélectionne un sous-ensemble d'aliments appropriés
        selected_foods = self._select_foods_for_meal(
            meal_type,
            available_foods,
            targets
        )
        
        # Optimise les quantités
        optimized_quantities = self._optimize_food_quantities(
            selected_foods,
            targets
        )
        
        # Ajoute les aliments au repas
        for food, quantity in zip(selected_foods, optimized_quantities):
            if quantity > self.min_food_quantity:
                meal.add_food(food, round(quantity, 1))
        
        return meal
    
    def _select_foods_for_meal(
        self,
        meal_type: str,
        available_foods: List[Food],
        targets: Dict[str, float]
    ) -> List[Food]:
        """
        Sélectionne un ensemble d'aliments variés pour un repas
        Stratégie: équilibrer sources de protéines, glucides, lipides et légumes
        """
        selected = []
        
        # Catégorisation des aliments
        categories = {
            "proteins": [f for f in available_foods if f.category in ["Viandes", "Poissons", "Œufs", "Légumineuses"] or f.proteins > 15],
            "carbs": [f for f in available_foods if f.category in ["Féculents", "Fruits"] or f.carbs > 15],
            "fats": [f for f in available_foods if f.category in ["Matières grasses", "Noix et graines"] or f.fats > 10],
            "vegetables": [f for f in available_foods if f.category == "Légumes"],
            "dairy": [f for f in available_foods if f.category == "Produits laitiers"]
        }
        
        # Stratégie selon type de repas
        if meal_type == "breakfast":
            # Petit-déj: produits laitiers, fruits, féculents
            selected.extend(random.sample(categories["dairy"], min(1, len(categories["dairy"]))))
            selected.extend(random.sample(categories["carbs"], min(2, len(categories["carbs"]))))
            if categories["fats"]:
                selected.extend(random.sample(categories["fats"], 1))
        
        elif meal_type in ["lunch", "dinner"]:
            # Repas principaux: protéines, féculents, légumes, lipides
            selected.extend(random.sample(categories["proteins"], min(1, len(categories["proteins"]))))
            selected.extend(random.sample(categories["carbs"], min(1, len(categories["carbs"]))))
            selected.extend(random.sample(categories["vegetables"], min(2, len(categories["vegetables"]))))
            if categories["fats"]:
                selected.extend(random.sample(categories["fats"], 1))
        
        else:  # snack
            # Collation: 2-3 aliments simples
            pool = categories["carbs"] + categories["proteins"] + categories["dairy"]
            selected.extend(random.sample(pool, min(3, len(pool))))
        
        # Limite le nombre total d'aliments
        if len(selected) > self.max_foods_per_meal:
            selected = random.sample(selected, self.max_foods_per_meal)
        
        # Assure un minimum d'aliments
        if len(selected) < 3:
            additional = [f for f in available_foods if f not in selected]
            selected.extend(random.sample(additional, min(3 - len(selected), len(additional))))
        
        return selected
    
    def _optimize_food_quantities(
        self,
        foods: List[Food],
        targets: Dict[str, float]
    ) -> np.ndarray:
        """
        Optimise les quantités d'aliments pour atteindre les cibles macro
        Utilise scipy.optimize pour résoudre le problème d'optimisation
        """
        n_foods = len(foods)
        
        # Fonction objective: minimiser l'écart avec les cibles
        def objective(quantities):
            total_cals = sum(f.calories * q / 100 for f, q in zip(foods, quantities))
            total_prots = sum(f.proteins * q / 100 for f, q in zip(foods, quantities))
            total_carbs = sum(f.carbs * q / 100 for f, q in zip(foods, quantities))
            total_fats = sum(f.fats * q / 100 for f, q in zip(foods, quantities))
            
            # Écarts relatifs pondérés
            error_cals = ((total_cals - targets["calories"]) / targets["calories"]) ** 2
            error_prots = ((total_prots - targets["proteins"]) / targets["proteins"]) ** 2
            error_carbs = ((total_carbs - targets["carbs"]) / targets["carbs"]) ** 2
            error_fats = ((total_fats - targets["fats"]) / targets["fats"]) ** 2
            
            return error_cals + error_prots + error_carbs + error_fats
        
        # Contraintes: quantités entre min et max
        bounds = [(self.min_food_quantity, self.max_food_quantity) for _ in range(n_foods)]
        
        # Point de départ: quantités moyennes
        x0 = np.full(n_foods, 100.0)
        
        # Optimisation
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            options={'maxiter': 500}
        )
        
        if result.success:
            return result.x
        else:
            # Si l'optimisation échoue, retourne des quantités par défaut
            return np.full(n_foods, 100.0)
    
    def regenerate_meal(
        self,
        meal_plan: 'MealPlan',
        meal_index: int,
        food_database: List[Food]
    ) -> Meal:
        """
        Régénère un repas spécifique dans un plan
        """
        if meal_index >= len(meal_plan.meals):
            raise IndexError("Index de repas invalide")
        
        old_meal = meal_plan.meals[meal_index]
        
        # Filtre les aliments
        available_foods = self._filter_foods_by_preferences(
            food_database,
            meal_plan.nutrition_target.dietary_preferences
        )
        
        # Cible pour ce repas
        targets = {
            "calories": old_meal.target_calories,
            "proteins": meal_plan.nutrition_target.proteins * (old_meal.target_calories / meal_plan.nutrition_target.calories),
            "carbs": meal_plan.nutrition_target.carbs * (old_meal.target_calories / meal_plan.nutrition_target.calories),
            "fats": meal_plan.nutrition_target.fats * (old_meal.target_calories / meal_plan.nutrition_target.calories)
        }
        
        # Génère nouveau repas
        new_meal = self._generate_single_meal(
            meal_name=old_meal.name,
            meal_type=old_meal.meal_type,
            targets=targets,
            available_foods=available_foods,
            day_number=old_meal.day_number
        )
        
        return new_meal
```

---

### 11.3 Couche Database - Implémentation

#### 11.3.1 DatabaseManager - Gestion complète de la BD

```python
# models/database.py
import sqlite3
from typing import List, Optional, Dict
import json
from contextlib import contextmanager
from models.food import Food
from models.meal_plan import MealPlan
from models.meal import Meal
from models.nutrition import NutritionTarget

class DatabaseManager:
    """
    Gestionnaire de la base de données SQLite
    """
    
    def __init__(self, db_path: str = "data/foods.db"):
        self.db_path = db_path
        self._initialize_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager pour connexions DB"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Crée les tables si elles n'existent pas"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table foods
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS foods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT,
                    calories REAL NOT NULL,
                    proteins REAL NOT NULL,
                    carbs REAL NOT NULL,
                    fats REAL NOT NULL,
                    fibers REAL DEFAULT 0,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Index pour recherches rapides
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_food_name 
                ON foods(name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_food_category 
                ON foods(category)
            ''')
            
            # Table meal_plans
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration_days INTEGER NOT NULL,
                    target_calories REAL,
                    target_proteins REAL,
                    target_carbs REAL,
                    target_fats REAL,
                    num_meals INTEGER,
                    meal_distribution TEXT,
                    dietary_preferences TEXT,
                    notes TEXT
                )
            ''')
            
            # Table meals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_plan_id INTEGER,
                    name TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    day_number INTEGER DEFAULT 1,
                    target_calories REAL,
                    FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id) ON DELETE CASCADE
                )
            ''')
            
            # Table meal_foods (association)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meal_foods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_id INTEGER NOT NULL,
                    food_id INTEGER NOT NULL,
                    quantity_grams REAL NOT NULL,
                    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
                    FOREIGN KEY (food_id) REFERENCES foods(id)
                )
            ''')
            
            conn.commit()
    
    # ==================== FOODS ====================
    
    def add_food(self, food: Food) -> int:
        """
        Ajoute un aliment à la base de données
        Returns: ID de l'aliment créé
        """
        is_valid, error = food.validate()
        if not is_valid:
            raise ValueError(f"Aliment invalide: {error}")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO foods (name, category, calories, proteins, carbs, fats, fibers, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                food.name,
                food.category,
                food.calories,
                food.proteins,
                food.carbs,
                food.fats,
                food.fibers,
                json.dumps(food.tags)
            ))
            return cursor.lastrowid
    
    def get_food(self, food_id: int) -> Optional[Food]:
        """Récupère un aliment par son ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM foods WHERE id = ?', (food_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_food(row)
            return None
    
    def get_all_foods(self) -> List[Food]:
        """Récupère tous les aliments"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM foods ORDER BY name')
            rows = cursor.fetchall()
            return [self._row_to_food(row) for row in rows]
    
    def search_foods(self, query: str = "", category: str = None, tags: List[str] = None) -> List[Food]:
        """
        Recherche des aliments selon critères
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            sql = 'SELECT * FROM foods WHERE 1=1'
            params = []
            
            if query:
                sql += ' AND name LIKE ?'
                params.append(f'%{query}%')
            
            if category:
                sql += ' AND category = ?'
                params.append(category)
            
            sql += ' ORDER BY name'
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            foods = [self._row_to_food(row) for row in rows]
            
            # Filtre par tags si nécessaire
            if tags:
                foods = [f for f in foods if any(tag in f.tags for tag in tags)]
            
            return foods
    
    def update_food(self, food: Food) -> bool:
        """
        Met à jour un aliment existant
        Returns: True si succès
        """
        if not food.id:
            raise ValueError("L'aliment doit avoir un ID pour être mis à jour")
        
        is_valid, error = food.validate()
        if not is_valid:
            raise ValueError(f"Aliment invalide: {error}")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE foods 
                SET name=?, category=?, calories=?, proteins=?, carbs=?, fats=?, fibers=?, tags=?
                WHERE id=?
            ''', (
                food.name,
                food.category,
                food.calories,
                food.proteins,
                food.carbs,
                food.fats,
                food.fibers,
                json.dumps(food.tags),
                food.id
            ))
            return cursor.rowcount > 0
    
    def delete_food(self, food_id: int) -> bool:
        """
        Supprime un aliment
        Returns: True si succès
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM foods WHERE id = ?', (food_id,))
            return cursor.rowcount > 0
    
    def _row_to_food(self, row) -> Food:
        """Convertit une ligne DB en objet Food"""
        return Food(
            id=row['id'],
            name=row['name'],
            category=row['category'],
            calories=row['calories'],
            proteins=row['proteins'],
            carbs=row['carbs'],
            fats=row['fats'],
            fibers=row['fibers'] or 0.0,
            tags=json.loads(row['tags']) if row['tags'] else []
        )
    
    # ==================== MEAL PLANS ====================
    
    def save_meal_plan(self, meal_plan: MealPlan) -> int:
        """
        Sauvegarde un plan alimentaire complet
        Returns: ID du plan créé
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sauvegarde le plan
            target = meal_plan.nutrition_target
            cursor.execute('''
                INSERT INTO meal_plans 
                (name, duration_days, target_calories, target_proteins, target_carbs, target_fats,
                 num_meals, meal_distribution, dietary_preferences, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meal_plan.name,
                meal_plan.duration_days,
                target.calories if target else None,
                target.proteins if target else None,
                target.carbs if target else None,
                target.fats if target else None,
                target.num_meals if target else None,
                json.dumps(target.meal_distribution) if target else None,
                json.dumps(target.dietary_preferences) if target else None,
                meal_plan.notes
            ))
            plan_id = cursor.lastrowid
            
            # Sauvegarde les repas
            for meal in meal_plan.meals:
                cursor.execute('''
                    INSERT INTO meals (meal_plan_id, name, meal_type, day_number, target_calories)
                    VALUES (?, ?, ?, ?, ?)
                ''', (plan_id, meal.name, meal.meal_type, meal.day_number, meal.target_calories))
                meal_id = cursor.lastrowid
                
                # Sauvegarde les aliments du repas
                for food, quantity in meal.foods:
                    cursor.execute('''
                        INSERT INTO meal_foods (meal_id, food_id, quantity_grams)
                        VALUES (?, ?, ?)
                    ''', (meal_id, food.id, quantity))
            
            return plan_id
    
    def get_meal_plan(self, plan_id: int) -> Optional[MealPlan]:
        """Récupère un plan alimentaire complet par son ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Récupère le plan
            cursor.execute('SELECT * FROM meal_plans WHERE id = ?', (plan_id,))
            plan_row = cursor.fetchone()
            
            if not plan_row:
                return None
            
            # Reconstruit le NutritionTarget
            target = NutritionTarget(
                calories=plan_row['target_calories'],
                proteins=plan_row['target_proteins'],
                carbs=plan_row['target_carbs'],
                fats=plan_row['target_fats'],
                num_meals=plan_row['num_meals'],
                meal_distribution=json.loads(plan_row['meal_distribution']) if plan_row['meal_distribution'] else {},
                dietary_preferences=json.loads(plan_row['dietary_preferences']) if plan_row['dietary_preferences'] else []
            )
            
            # Crée le MealPlan
            meal_plan = MealPlan(
                id=plan_row['id'],
                name=plan_row['name'],
                duration_days=plan_row['duration_days'],
                nutrition_target=target,
                notes=plan_row['notes']
            )
            
            # Récupère les repas
            cursor.execute('''
                SELECT * FROM meals WHERE meal_plan_id = ? ORDER BY day_number, id
            ''', (plan_id,))
            meal_rows = cursor.fetchall()
            
            for meal_row in meal_rows:
                meal = Meal(
                    id=meal_row['id'],
                    name=meal_row['name'],
                    meal_type=meal_row['meal_type'],
                    day_number=meal_row['day_number'],
                    target_calories=meal_row['target_calories']
                )
                
                # Récupère les aliments du repas
                cursor.execute('''
                    SELECT f.*, mf.quantity_grams
                    FROM meal_foods mf
                    JOIN foods f ON mf.food_id = f.id
                    WHERE mf.meal_id = ?
                ''', (meal_row['id'],))
                food_rows = cursor.fetchall()
                
                for food_row in food_rows:
                    food = self._row_to_food(food_row)
                    meal.add_food(food, food_row['quantity_grams'])
                
                meal_plan.add_meal(meal)
            
            return meal_plan
    
    def get_all_meal_plans(self, limit: int = 20) -> List[Dict]:
        """
        Récupère la liste des plans (métadonnées seulement)
        Returns: Liste de dictionnaires avec infos résumées
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, date_created, duration_days, target_calories, notes
                FROM meal_plans
                ORDER BY date_created DESC
                LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'name': row['name'],
                'date_created': row['date_created'],
                'duration_days': row['duration_days'],
                'target_calories': row['target_calories'],
                'notes': row['notes']
            } for row in rows]
    
    def delete_meal_plan(self, plan_id: int) -> bool:
        """
        Supprime un plan alimentaire (cascade sur repas et aliments)
        Returns: True si succès
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM meal_plans WHERE id = ?', (plan_id,))
            return cursor.rowcount > 0
    
    # ==================== IMPORT/EXPORT ====================
    
    def import_foods_from_json(self, file_path: str) -> int:
        """
        Importe des aliments depuis un fichier JSON
        Returns: nombre d'aliments importés
        """
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        
        count = 0
        for food_dict in foods_data:
            try:
                food = Food.from_dict(food_dict)
                self.add_food(food)
                count += 1
            except Exception as e:
                print(f"Erreur import {food_dict.get('name', 'Unknown')}: {e}")
        
        return count
    
    def export_foods_to_json(self, file_path: str) -> int:
        """
        Exporte tous les aliments vers un fichier JSON
        Returns: nombre d'aliments exportés
        """
        import json
        
        foods = self.get_all_foods()
        foods_data = [food.to_dict() for food in foods]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(foods_data, f, ensure_ascii=False, indent=2)
        
        return len(foods_data)
```

---

### 11.4 Contrôleurs - Implémentation détaillée

#### 11.4.1 MealPlanController - Contrôleur principal

```python
# controllers/meal_plan_controller.py
from typing import Optional, List
from models.nutrition import NutritionTarget
from models.meal_plan import MealPlan
from models.database import DatabaseManager
from services.meal_generator import MealGenerator
from views.main_window import MainWindow

class MealPlanController:
    """
    Contrôleur principal de l'application
    Orchestre les interactions entre Vue, Modèle et Services
    """
    
    def __init__(self, db_manager: DatabaseManager, view: MainWindow):
        self.db = db_manager
        self.view = view
        self.generator = MealGenerator()
        self.current_meal_plan: Optional[MealPlan] = None
        
        # Connexion des événements de la vue
        self._connect_view_events()
    
    def _connect_view_events(self):
        """Connecte les signaux de la vue aux handlers du contrôleur"""
        self.view.on_generate_clicked = self.handle_generate_plan
        self.view.on_regenerate_meal_clicked = self.handle_regenerate_meal
        self.view.on_save_plan_clicked = self.handle_save_plan
        self.view.on_load_plan_clicked = self.handle_load_plan
        self.view.on_export_clicked = self.handle_export
    
    def handle_generate_plan(self):
        """
        Génère un nouveau plan alimentaire à partir des paramètres de la vue
        """
        try:
            # Récupère les paramètres depuis la vue
            settings = self.view.get_settings()
            
            # Crée le NutritionTarget
            nutrition_target = NutritionTarget(
                calories=settings['calories'],
                proteins=settings['proteins'],
                carbs=settings['carbs'],
                fats=settings['fats'],
                num_meals=settings['num_meals'],
                dietary_preferences=settings['dietary_preferences']
            )
            
            # Valide les objectifs
            is_valid, message = nutrition_target.validate_balance()
            if not is_valid:
                self.view.show_error(f"Objectifs invalides: {message}")
                return
            
            # Récupère la base d'aliments
            food_database = self.db.get_all_foods()
            
            if len(food_database) < 20:
                self.view.show_error("Base d'aliments insuffisante. Ajoutez plus d'aliments.")
                return
            
            # Affiche un indicateur de chargement
            self.view.show_loading(True)
            
            # Génère le plan
            duration = settings.get('duration_days', 1)
            self.current_meal_plan = self.generator.generate_meal_plan(
                nutrition_target=nutrition_target,
                food_database=food_database,
                duration_days=duration
            )
            
            # Masque le chargement
            self.view.show_loading(False)
            
            # Affiche le plan dans la vue
            self.view.display_meal_plan(self.current_meal_plan)
            
            # Message de succès
            validation = self.current_meal_plan.validate_against_target()
            if validation['is_valid']:
                self.view.show_success("Plan généré avec succès!")
            else:
                self.view.show_warning("Plan généré, mais certains objectifs ne sont pas atteints parfaitement.")
        
        except Exception as e:
            self.view.show_loading(False)
            self.view.show_error(f"Erreur lors de la génération: {str(e)}")
    
    def handle_regenerate_meal(self, meal_index: int):
        """
        Régénère un repas spécifique
        """
        if not self.current_meal_plan:
            self.view.show_error("Aucun plan actif")
            return
        
        try:
            food_database = self.db.get_all_foods()
            
            new_meal = self.generator.regenerate_meal(
                meal_plan=self.current_meal_plan,
                meal_index=meal_index,
                food_database=food_database
            )
            
            # Remplace le repas dans le plan
            self.current_meal_plan.meals[meal_index] = new_meal
            
            # Rafraîchit l'affichage
            self.view.display_meal_plan(self.current_meal_plan)
            self.view.show_success(f"Repas '{new_meal.name}' régénéré")
        
        except Exception as e:
            self.view.show_error(f"Erreur régénération: {str(e)}")
    
    def handle_save_plan(self, plan_name: str = ""):
        """
        Sauvegarde le plan actuel dans la base de données
        """
        if not self.current_meal_plan:
            self.view.show_error("Aucun plan à sauvegarder")
            return
        
        try:
            if plan_name:
                self.current_meal_plan.name = plan_name
            
            plan_id = self.db.save_meal_plan(self.current_meal_plan)
            self.current_meal_plan.id = plan_id
            
            self.view.show_success(f"Plan sauvegardé (ID: {plan_id})")
        
        except Exception as e:
            self.view.show_error(f"Erreur sauvegarde: {str(e)}")
    
    def handle_load_plan(self, plan_id: int):
        """
        Charge un plan existant depuis la base de données
        """
        try:
            meal_plan = self.db.get_meal_plan(plan_id)
            
            if meal_plan:
                self.current_meal_plan = meal_plan
                self.view.display_meal_plan(meal_plan)
                self.view.show_success(f"Plan '{meal_plan.name}' chargé")
            else:
                self.view.show_error("Plan introuvable")
        
        except Exception as e:
            self.view.show_error(f"Erreur chargement: {str(e)}")
    
    def handle_export(self, export_format: str, file_path: str):
        """
        Exporte le plan actuel dans le format demandé
        """
        if not self.current_meal_plan:
            self.view.show_error("Aucun plan à exporter")
            return
        
        try:
            from controllers.export_controller import ExportController
            exporter = ExportController()
            
            if export_format == "pdf":
                exporter.export_to_pdf(self.current_meal_plan, file_path)
            elif export_format == "excel":
                exporter.export_to_excel(self.current_meal_plan, file_path)
            elif export_format == "json":
                exporter.export_to_json(self.current_meal_plan, file_path)
            else:
                raise ValueError(f"Format non supporté: {export_format}")
            
            self.view.show_success(f"Exporté vers {file_path}")
        
        except Exception as e:
            self.view.show_error(f"Erreur export: {str(e)}")
    
    def handle_adjust_meal_quantity(self, meal_index: int, food_index: int, new_quantity: float):
        """
        Ajuste manuellement la quantité d'un aliment dans un repas
        """
        if not self.current_meal_plan:
            return
        
        try:
            meal = self.current_meal_plan.meals[meal_index]
            food, old_quantity = meal.foods[food_index]
            
            meal.update_food_quantity(food, new_quantity)
            
            # Rafraîchit l'affichage
            self.view.update_meal_display(meal_index, meal)
            self.view.show_success("Quantité ajustée")
        
        except Exception as e:
            self.view.show_error(f"Erreur ajustement: {str(e)}")
    
    def get_plan_history(self, limit: int = 20) -> List[dict]:
        """
        Récupère l'historique des plans sauvegardés
        """
        return self.db.get_all_meal_plans(limit)
```

---

### 11.5 Vue - Exemple d'implémentation (PyQt6)

#### 11.5.1 MainWindow - Fenêtre principale

```python
# views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from views.settings_panel import SettingsPanel
from views.meal_plan_display import MealPlanDisplay
from models.meal_plan import MealPlan

class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application
    """
    
    # Signaux
    generate_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meal Planner Pro")
        self.setMinimumSize(1200, 800)
        
        # Callbacks (seront connectés par le contrôleur)
        self.on_generate_clicked = None
        self.on_regenerate_meal_clicked = None
        self.on_save_plan_clicked = None
        self.on_load_plan_clicked = None
        self.on_export_clicked = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Panneau de gauche: paramètres
        self.settings_panel = SettingsPanel()
        main_layout.addWidget(self.settings_panel, stretch=1)
        
        # Panneau de droite: affichage du plan
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        # Zone d'affichage du plan
        self.meal_plan_display = MealPlanDisplay()
        right_layout.addWidget(self.meal_plan_display)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Générer le plan")
        self.btn_generate.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn_generate.clicked.connect(self._on_generate_button)
        
        self.btn_save = QPushButton("Sauvegarder")
        self.btn_save.clicked.connect(self._on_save_button)
        
        self.btn_export = QPushButton("Exporter")
        self.btn_export.clicked.connect(self._on_export_button)
        
        buttons_layout.addWidget(self.btn_generate)
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_export)
        buttons_layout.addStretch()
        
        right_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(right_panel, stretch=2)
        
        # Menu bar
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        file_menu.addAction("Nouveau plan", self._on_generate_button)
        file_menu.addAction("Charger un plan", self._on_load_button)
        file_menu.addAction("Gérer les aliments", self._on_manage_foods_button)
        file_menu.addSeparator()
        file_menu.addAction("Quitter", self.close)
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        help_menu.addAction("Documentation", self._show_documentation)
        help_menu.addAction("À propos", self._show_about)
    
    def get_settings(self) -> dict:
        """Récupère les paramètres depuis le panneau de settings"""
        return self.settings_panel.get_values()
    
    def display_meal_plan(self, meal_plan: MealPlan):
        """Affiche un plan alimentaire"""
        self.meal_plan_display.show_plan(meal_plan)
    
    def update_meal_display(self, meal_index: int, meal):
        """Met à jour l'affichage d'un repas spécifique"""
        self.meal