import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DEFAULT_DB_PATH = BASE_DIR / "empridge.db"


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Inicjalizuje strukture bazy danych SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql_path = BASE_DIR.parent / "sql" / "schema.sql"

    try:
        with open(sql_path, 'r') as f:
            sql_script = f.read()

        cursor.executescript(sql_script)
        conn.commit()
        print("Baza danych zainicjalizowana.")

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku SQL pod ścieżką: {sql_path.absolute()}")
        raise
    except sqlite3.Error as e:
        print(f"Błąd SQLite: {e}")
        raise
    finally:
        conn.close()


def get_or_create_id(
        cursor: sqlite3.Cursor,
        table: str,
        name: str,
        img_url: str | None = None
        ) -> int:
    """Helper, zwraca ID rekordu, tworzy go, jeśli nie istnieje."""

    columns = "(name, image_url)" if img_url else "(name)"
    params = [name, img_url] if img_url else [name]
    placeholders = ", ".join(["?"] * len(params))
    cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute(f"INSERT INTO {table} {columns} VALUES ({placeholders})", tuple(params))

    if cursor.lastrowid is None:
        raise RuntimeError(f"Nie udało się pobrać ID dla {name} z tabeli {table}")

    return cursor.lastrowid


def import_to_database(
        meals_list: list[dict],
        img_url: str,
        db_path: Path = DEFAULT_DB_PATH
        ) -> None:
    """Wprowadza dane do bazy danych SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("BEGIN TRANSACTION;")

        for meal in meals_list:
            category_id = get_or_create_id(cursor, "categories", meal['category'])
            area_id = get_or_create_id(cursor, "areas", meal['area'])

            cursor.execute('''
                INSERT OR REPLACE INTO recipes (id, title, instructions, image_url, youtube_url, category_id, area_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (meal['id'], meal['title'], meal['instructions'], meal['thumbnail'], meal['youtube'], category_id, area_id))

            for ing in meal['ingredients']:
                ing_id = get_or_create_id(cursor, "ingredients", ing['name'], f"{img_url}{ing['name']}.png")
                cursor.execute('''
                    INSERT OR REPLACE INTO recipe_ingredients (recipe_id, ingredient_id, measure)
                    VALUES (?, ?, ?)
                ''', (meal['id'], ing_id, ing['measure']))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Błąd podczas zapisu: {e}")
        raise
    finally:
        conn.close()


def setup_and_import(
        meals_list: list[dict],
        img_url: str,
        db_path: Path = DEFAULT_DB_PATH):
    """Inicjalizuje bazę i zapisuje dane."""
    try:
        init_db(db_path)
        import_to_database(meals_list, img_url, db_path)
    except Exception as e:
        print(f"Błąd podczas inicjalizacji lub importu danych: {e}")
        raise


if __name__ == "__main__":
    init_db()