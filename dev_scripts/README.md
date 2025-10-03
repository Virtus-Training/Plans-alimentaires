# Scripts de Développement

Ce dossier contient des scripts utilitaires utilisés pendant le développement et la maintenance de l'application Meal Planner Pro.

## Scripts de Test

### `test_improvements.py`
Script de test pour valider les améliorations et nouvelles fonctionnalités.

### `test_all_improvements.py`
Suite de tests complète pour toutes les améliorations implémentées.

### `test_final_validation.py`
Validation finale avant mise en production.

## Scripts de Base de Données

### `populate_test_foods.py`
Peuple la base de données avec des aliments de test pour le développement.

### `migrate_database.py`
Script de migration pour mettre à jour le schéma de la base de données.

## Scripts d'Analyse

### `enrich_variety_index.py`
Enrichit l'index de variété des aliments dans la base de données.

### `auto_enrich_variety.py`
Enrichissement automatique des données de variété.

### `analyze_variety_distribution.py`
Analyse la distribution des indices de variété dans la base de données.

## Utilisation

Ces scripts sont destinés au développement et au débogage. Ils ne sont pas nécessaires pour l'utilisation normale de l'application.

**Note:** Assurez-vous d'avoir activé l'environnement virtuel avant d'exécuter ces scripts:

```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

Puis exécutez le script désiré:

```bash
python dev_scripts/nom_du_script.py
```
