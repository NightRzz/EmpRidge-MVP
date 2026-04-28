import sqlite3
from pathlib import Path

def init_db(db_path="empridge.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql_path = Path(__file__).parent.parent / "sql" /  "schema.sql"

    try:
        with open(sql_path, 'r') as f:
            sql_script = f.read()

        cursor.executescript(sql_script)
        conn.commit()
        print("Baza danych zainicjalizowana.")

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku SQL pod ścieżką: {sql_path.absolute()}")
    except sqlite3.Error as e:
        print(f"Błąd SQLite: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(2*False)