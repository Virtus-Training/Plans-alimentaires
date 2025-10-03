"""
Script de migration pour ajouter les nouvelles colonnes à la base de données
"""

import sqlite3
from pathlib import Path

def migrate_database():
    """Ajoute les nouvelles colonnes price_per_100g, health_index, variety_index."""

    db_path = Path("meal_planner/data/foods.db")

    if not db_path.exists():
        print(f"Base de données introuvable: {db_path}")
        return

    print(f"Migration de la base de données: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(foods)")
        columns = [row[1] for row in cursor.fetchall()]

        print(f"Colonnes actuelles: {columns}")

        # Ajouter price_per_100g si manquante
        if 'price_per_100g' not in columns:
            print("Ajout de la colonne price_per_100g...")
            cursor.execute("ALTER TABLE foods ADD COLUMN price_per_100g REAL DEFAULT 0.0")
            print("[OK] Colonne price_per_100g ajoutee")
        else:
            print("[OK] Colonne price_per_100g deja presente")

        # Ajouter health_index si manquante
        if 'health_index' not in columns:
            print("Ajout de la colonne health_index...")
            cursor.execute("ALTER TABLE foods ADD COLUMN health_index INTEGER DEFAULT 5")
            print("[OK] Colonne health_index ajoutee")
        else:
            print("[OK] Colonne health_index deja presente")

        # Ajouter variety_index si manquante
        if 'variety_index' not in columns:
            print("Ajout de la colonne variety_index...")
            cursor.execute("ALTER TABLE foods ADD COLUMN variety_index INTEGER DEFAULT 5")
            print("[OK] Colonne variety_index ajoutee")
        else:
            print("[OK] Colonne variety_index deja presente")

        conn.commit()
        print("\n[SUCCES] Migration terminee avec succes!")

        # Afficher les nouvelles colonnes
        cursor.execute("PRAGMA table_info(foods)")
        columns = cursor.fetchall()
        print("\nStructure de la table après migration:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

    except Exception as e:
        print(f"\n[ERREUR] Erreur lors de la migration: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
