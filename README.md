# Meal Planner Pro - Phase 1

Générateur de plans alimentaires personnalisés avec architecture MVC stricte.

## 📋 Statut du Projet

**Phase 1 : TERMINÉE** ✓

L'application possède toutes les fondations nécessaires et se lance sans erreur.

## ✅ Fonctionnalités Implémentées (Phase 1)

### Architecture
- ✓ Structure MVC complète et fonctionnelle
- ✓ Séparation stricte des responsabilités (Modèle / Vue / Contrôleur)
- ✓ Configuration centralisée
- ✓ Système de logging complet

### Modèles
- ✓ `Food` : Représentation des aliments avec validation
- ✓ `NutritionTarget` : Objectifs nutritionnels
- ✓ `Meal` : Repas avec calculs de macros
- ✓ `MealPlan` : Plan alimentaire complet
- ✓ `DatabaseManager` : Gestion SQLite avec SQLAlchemy

### Base de Données
- ✓ Base SQLite initialisée automatiquement
- ✓ 69 aliments pré-chargés dans 9 catégories
- ✓ CRUD complet sur les aliments
- ✓ Support des tags (végétarien, végan, sans gluten, etc.)

### Interface Utilisateur (PyQt6)
- ✓ Fenêtre principale avec layout responsive
- ✓ Panneau de paramètres avec sliders interactifs
- ✓ Configuration des macros (calories, protéines, glucides, lipides)
- ✓ Affichage en temps réel de la répartition en %
- ✓ Sélection du nombre de repas (3-6)
- ✓ Sélection de la durée (1-14 jours)
- ✓ Cases à cocher pour préférences diététiques
- ✓ Barre de menu et barre de statut
- ✓ Panneau d'affichage des plans (structure prête)

### Validation
- ✓ Validation robuste de toutes les entrées
- ✓ Gestion d'erreurs complète
- ✓ Messages d'erreur clairs pour l'utilisateur

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## 💻 Lancement

```bash
python main.py
```

Au premier lancement, l'application :
1. Crée automatiquement la base de données SQLite
2. Charge 69 aliments par défaut
3. Affiche la fenêtre principale

## 🏗️ Structure du Projet

```
meal_planner/
├── main.py                    # Point d'entrée
├── requirements.txt           # Dépendances
├── README.md                  # Ce fichier
├── meal_planner/
│   ├── config.py             # Configuration
│   ├── models/               # Couche Modèle
│   │   ├── food.py          # Classe Food
│   │   ├── meal.py          # Classe Meal
│   │   ├── meal_plan.py     # Classe MealPlan
│   │   ├── nutrition.py     # Classe NutritionTarget
│   │   └── database.py      # DatabaseManager
│   ├── views/                # Couche Vue
│   │   ├── main_window.py   # Fenêtre principale
│   │   ├── settings_panel.py    # Panneau paramètres
│   │   └── meal_plan_display.py # Affichage plans
│   ├── controllers/          # Couche Contrôleur
│   │   └── meal_plan_controller.py
│   ├── services/             # Services (Phase 2)
│   ├── utils/                # Utilitaires
│   │   ├── validators.py    # Validation
│   │   └── logger.py        # Logging
│   └── data/
│       ├── foods.db         # Base SQLite (créée auto)
│       └── presets/
│           └── default_foods.json  # Aliments par défaut
```

## 📊 Base de Données

### Catégories d'aliments disponibles
- Viandes et poissons (10)
- Légumineuses (6)
- Céréales et féculents (10)
- Légumes (10)
- Fruits (10)
- Produits laitiers (8)
- Noix et graines (10)
- Huiles et matières grasses (3)
- Autres (2)

### Tags supportés
- `vegetarian` : Végétarien
- `vegan` : Végan
- `gluten_free` : Sans gluten
- `lactose_free` : Sans lactose

## 🎯 Utilisation

### Configurer les objectifs
1. Ajustez les sliders pour définir vos macros :
   - Calories : 1200-4000 kcal
   - Protéines : 50-300g
   - Glucides : 50-500g
   - Lipides : 30-150g

2. La répartition en % s'affiche en temps réel

3. Sélectionnez le nombre de repas par jour (3-6)

4. Définissez la durée du plan (1-14 jours)

5. Cochez vos préférences diététiques si nécessaire

### Générer un plan
Cliquez sur **"Générer le Plan Alimentaire"**

**Note Phase 1** : L'algorithme de génération n'est pas encore implémenté. Le bouton affiche une notification indiquant que cette fonctionnalité sera disponible en Phase 2.

## 🔧 Développement

### Code Quality
- Respect strict de PEP 8
- Type hints sur toutes les fonctions
- Docstrings complètes
- Architecture MVC rigoureuse
- Gestion d'erreurs élégante

### Logging
Les logs sont enregistrés dans `meal_planner.log` à la racine du projet.

## 📝 Prochaines Étapes (Phase 2)

- ❌ Algorithme de génération optimisée (scipy.optimize)
- ❌ Génération de repas complets et variés
- ❌ Respect des contraintes nutritionnelles (±5%)
- ❌ Affichage des repas générés
- ❌ Régénération par repas

## 📦 Phase 3 (Future)

- Export PDF (ReportLab)
- Export Excel (openpyxl)
- Gestionnaire d'aliments complet (CRUD depuis l'interface)
- Import/Export JSON
- Sauvegarde/Chargement de plans

## 🐛 Problèmes Connus

Aucun problème bloquant. L'application se lance et fonctionne correctement.

## 📄 Licence

Projet personnel - Tous droits réservés

---

**Version** : 0.1.0 (Phase 1 - Fondations)
**Dernière mise à jour** : 2025-10-01
