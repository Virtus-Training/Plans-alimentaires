"""
Script de migration pour ajouter la colonne unit_weight à la table foods
"""

import sqlite3
from pathlib import Path
from meal_planner.config import DATABASE_PATH

def migrate_add_unit_weight():
    """Ajoute la colonne unit_weight à la table foods."""

    print(f"Migration de la base de données: {DATABASE_PATH}")

    # Connexion à la base
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(foods)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'unit_weight' in columns:
            print("[OK] La colonne unit_weight existe deja")
        else:
            # Ajouter la colonne
            cursor.execute("ALTER TABLE foods ADD COLUMN unit_weight REAL")
            print("[OK] Colonne unit_weight ajoutee avec succes")

        # Mettre à jour quelques aliments courants avec leurs poids unitaires
        unit_weights = {
            # Fruits (poids moyens en grammes)
            'Pomme': 150,
            'Banane': 120,
            'Orange': 140,
            'Poire': 150,
            'Pêche': 150,
            'Abricot': 40,
            'Prune': 50,
            'Kiwi': 80,
            'Mandarine': 80,
            'Clémentine': 70,

            # Œufs
            'Œuf': 50,
            'Oeuf': 50,

            # Légumes unitaires
            'Tomate': 120,
            'Concombre': 300,
            'Courgette': 250,
            'Aubergine': 300,
            'Poivron': 150,
            'Carotte': 80,
            'Oignon': 100,
            'Pomme de terre': 150,
        }

        for food_name, weight in unit_weights.items():
            cursor.execute(
                "UPDATE foods SET unit_weight = ? WHERE name LIKE ?",
                (weight, f"%{food_name}%")
            )

        conn.commit()
        print(f"[OK] {len(unit_weights)} poids unitaires configures")

        # Afficher quelques exemples
        cursor.execute("""
            SELECT name, unit_weight
            FROM foods
            WHERE unit_weight IS NOT NULL
            LIMIT 10
        """)

        print("\nExemples d'aliments avec poids unitaire:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}g")

    except Exception as e:
        print(f"[ERREUR] Erreur lors de la migration: {e}")
        conn.rollback()
    finally:
        conn.close()

    print("\n[OK] Migration terminee")

if __name__ == "__main__":
    migrate_add_unit_weight()
