import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "empridge.db"


def get_db_connection() -> sqlite3.Connection:
    """Tworzy połączenie SQLite z dostępem do kolumn po nazwie.

    Returns:
        sqlite3.Connection: Skonfigurowane połączenie SQLite.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ============ INGREDIENTS ============

def list_ingredients(skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """Zwraca listę składników z paginacją.

    Args:
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów do zwrócenia.

    Returns:
        list[dict[str, Any]]: Lista słowników ze składnikami.
    """
    if skip < 0:
        raise ValueError("Parametr skip musi być >= 0.")
    if limit <= 0:
        raise ValueError("Parametr limit musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, image_url
            FROM ingredients
            ORDER BY name ASC
            LIMIT ? OFFSET ?
            """,
            (limit, skip),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_ingredient_by_id(ingredient_id: int) -> dict[str, Any] | None:
    """Zwraca składnik po ID albo None, jeśli nie istnieje.

    Args:
        ingredient_id: Klucz główny składnika.

    Returns:
        dict[str, Any] | None: Słownik składnika lub None.
    """
    if ingredient_id <= 0:
        raise ValueError("Parametr ingredient_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, image_url
            FROM ingredients
            WHERE id = ?
            """,
            (ingredient_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_ingredient(name: str, image_url: str) -> dict[str, Any]:
    """Tworzy składnik i zwraca utworzony rekord.

    Args:
        name: Nazwa składnika.
        image_url: URL obrazka składnika.

    Returns:
        dict[str, Any]: Utworzony rekord składnika.
    """
    if not name.strip():
        raise ValueError("Nazwa składnika nie może być pusta.")
    if not image_url.strip():
        raise ValueError("Adres image_url nie może być pusty.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO ingredients (name, image_url)
                VALUES (?, ?)
                """,
                (name.strip(), image_url.strip()),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Składnik o takiej nazwie lub image_url już istnieje.") from exc

        ingredient_id = cursor.lastrowid
        if ingredient_id is None:
            raise RuntimeError("Nie udało się pobrać ID nowego składnika.")

        created = get_ingredient_by_id(ingredient_id)
        if created is None:
            raise RuntimeError("Nie udało się odczytać utworzonego składnika.")
        return created
    finally:
        conn.close()


def update_ingredient(
    ingredient_id: int,
    name: str | None = None,
    image_url: str | None = None,
) -> dict[str, Any] | None:
    """Aktualizuje pola składnika i zwraca zaktualizowany rekord.

    Args:
        ingredient_id: Klucz główny składnika.
        name: Nowa nazwa składnika.
        image_url: Nowy adres obrazka.

    Returns:
        dict[str, Any] | None: Zaktualizowany rekord lub None, jeśli składnik nie istnieje.
    """
    if ingredient_id <= 0:
        raise ValueError("Parametr ingredient_id musi być > 0.")

    updates: dict[str, str] = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Nazwa składnika nie może być pusta.")
        updates["name"] = name
    if image_url is not None:
        image_url = image_url.strip()
        if not image_url:
            raise ValueError("Adres image_url nie może być pusty.")
        updates["image_url"] = image_url

    if not updates:
        return get_ingredient_by_id(ingredient_id)

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = list(updates.values()) + [ingredient_id]

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                UPDATE ingredients
                SET {set_clause}
                WHERE id = ?
                """,
                tuple(values),
            )
            conn.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("Składnik o takiej nazwie lub image_url już istnieje.") from exc

        if cursor.rowcount == 0:
            return None

        return get_ingredient_by_id(ingredient_id)
    finally:
        conn.close()


def delete_ingredient(ingredient_id: int) -> bool:
    """Usuwa składnik po ID.

    Args:
        ingredient_id: Klucz główny składnika.

    Returns:
        bool: True, jeśli rekord usunięto; False, jeśli rekord nie istniał.
    """
    if ingredient_id <= 0:
        raise ValueError("Parametr ingredient_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM ingredients
            WHERE id = ?
            """,
            (ingredient_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ============ RECIPES ============

def list_recipes(skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
    """Zwraca listę przepisów z paginacją.

    Args:
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów do zwrócenia.

    Returns:
        list[dict[str, Any]]: Lista słowników z przepisami.
    """
    if skip < 0:
        raise ValueError("Parametr skip musi być >= 0.")
    if limit <= 0:
        raise ValueError("Parametr limit musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            SELECT id, title, instructions, image_url, youtube_url, category_id, area_id
            FROM recipes
            ORDER BY title
            LIMIT ? OFFSET ?
            """,
            (limit, skip),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_recipe_by_id(recipe_id: int) -> dict[str, Any] | None:
    """Zwraca przepis po ID albo None, jeśli nie istnieje.

    Args:
        recipe_id: Klucz główny przepisu.

    Returns:
        dict[str, Any] | None: Słownik przepisu lub None.
    """
    if recipe_id <= 0:
        raise ValueError("Parametr recipe_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT id, title, instructions, image_url, youtube_url, category_id, area_id
        FROM recipes
        WHERE id = ?
            """,
            (recipe_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_recipe(
    title: str,
    instructions: str | None = None,
    image_url: str | None = None,
    youtube_url: str | None = None,
    category_id: int | None = None,
    area_id: int | None = None,
) -> dict[str, Any]:
    """Tworzy nowy przepis i zwraca utworzony rekord.

    Args:
        title: Tytuł przepisu.
        instructions: Instrukcja przygotowania.
        image_url: URL zdjęcia przepisu.
        youtube_url: URL filmu YouTube.
        category_id: ID kategorii.
        area_id: ID kraju/obszaru pochodzenia.

    Returns:
        dict[str, Any]: Utworzony rekord przepisu.
    """
    if not title.strip():
        raise ValueError("Tytuł przepisu nie może być pusty.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
        INSERT INTO RECIPES (title, instructions, image_url, youtube_url, category_id, area_id)
        VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                instructions,
                image_url,
                youtube_url,
                category_id,
                area_id,
            ),
        )
        conn.commit()
        recipe_id = cursor.lastrowid
        if recipe_id is None:
            raise RuntimeError("Nie udało się pobrać ID nowego przepisu.")
        created = get_recipe_by_id(recipe_id)
        if created is None:
            raise RuntimeError("Nie udało się odczytać utworzonego przepisu.")
        return created
    finally:
        conn.close()


def update_recipe(
    recipe_id: int,
    title: str | None = None,
    instructions: str | None = None,
    image_url: str | None = None,
    youtube_url: str | None = None,
    category_id: int | None = None,
    area_id: int | None = None,
) -> dict[str, Any] | None:
    """Aktualizuje wybrane pola przepisu.

    Args:
        recipe_id: Klucz główny przepisu.
        title: Nowy tytuł przepisu.
        instructions: Nowa instrukcja.
        image_url: Nowy URL zdjęcia.
        youtube_url: Nowy URL YouTube.
        category_id: Nowe ID kategorii.
        area_id: Nowe ID kraju/obszaru.

    Returns:
        dict[str, Any] | None: Zaktualizowany rekord lub None.
    """
    if recipe_id <= 0:
        raise ValueError("Parametr recipe_id musi być > 0.")

    updates:dict[str, str | int] = {}
    if title is not None:
        title = title.strip()
        if not title:
            raise ValueError("Tytuł przepisu nie może być pusty.")
        updates["title"] = title
    if instructions is not None:
        updates["instructions"] = instructions
    if image_url is not None:
        updates["image_url"] = image_url
    if youtube_url is not None:
        updates["youtube_url"] = youtube_url
    if category_id is not None:
        updates["category_id"] = category_id
    if area_id is not None:
        updates["area_id"] = area_id

    if not updates:
        return get_recipe_by_id(recipe_id)

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = list(updates.values()) + [recipe_id]

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                f"""
            UPDATE recipes
            SET {set_clause}
            WHERE id = ?
                """,
            tuple(values),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None

        return get_recipe_by_id(recipe_id)
    finally:
        conn.close()




def delete_recipe(recipe_id: int) -> bool:
    """Usuwa przepis po ID.

    Args:
        recipe_id: Klucz główny przepisu.

    Returns:
        bool: True, jeśli rekord usunięto; False, jeśli rekord nie istniał.
    """
    if recipe_id <= 0:
        raise ValueError("Parametr recipe_id musi być > 0.")

    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            DELETE FROM recipes
            WHERE id = ?
                """,
            (recipe_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ============ CATEGORIES ============

def list_categories() -> list[dict[str, Any]]:
    """Zwraca listę wszystkich kategorii.

    Returns:
        list[dict[str, Any]]: Lista słowników z kategoriami.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            SELECT id, name 
            FROM categories
            ORDER BY name
                """,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    """Zwraca kategorię po ID albo None, jeśli nie istnieje.

    Args:
        category_id: Klucz główny kategorii.

    Returns:
        dict[str, Any] | None: Słownik kategorii lub None.
    """
    if category_id <= 0:
        raise ValueError("Parametr category_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            SELECT id, name
            FROM categories
            WHERE id = ?
                """,
            (category_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_category(name: str) -> dict[str, Any]:
    """Tworzy kategorię i zwraca utworzony rekord.

    Args:
        name: Nazwa kategorii.

    Returns:
        dict[str, Any]: Utworzony rekord kategorii.
    """
    if not name.strip():
        raise ValueError("Nazwa kategorii nie może być pusta.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            INSERT INTO categories (name)
            VALUES (?)
                """,
            (name,),
        )
        conn.commit()
        category_id = cursor.lastrowid
        if category_id is None:
            raise RuntimeError("Nie udało się pobrać ID nowej kategorii.")
        created = get_category_by_id(category_id)
        if created is None:
            raise RuntimeError("Nie udało się odczytać utworzonej kategorii")
        return created
    finally:
        conn.close()


def update_category(category_id: int, name: str | None = None) -> dict[str, Any] | None:
    """Aktualizuje nazwę kategorii.

    Args:
        category_id: Klucz główny kategorii.
        name: Nowa nazwa kategorii.

    Returns:
        dict[str, Any] | None: Zaktualizowany rekord lub None.
    """
    if category_id <= 0:
        raise ValueError("Parametr category_id musi być > 0.")

    updates: dict[str, str] = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Nazwa kategorii nie może być pusta.")
        updates["name"] = name

    if not updates:
        return get_category_by_id(category_id)

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = list(updates.values()) + [category_id]
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
            UPDATE categories
            SET {set_clause}
            WHERE id = ?
                """,
                tuple(values),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Kategoria o takiej nazwie już istnieje.") from exc
        conn.commit()
        if cursor.rowcount == 0:
            return None

        return get_category_by_id(category_id)
    finally:
        conn.close()


def delete_category(category_id: int) -> bool:
    """Usuwa kategorię po ID.

    Args:
        category_id: Klucz główny kategorii.

    Returns:
        bool: True, jeśli rekord usunięto; False, jeśli rekord nie istniał.
    """
    if category_id <= 0:
        raise ValueError("Parametr category_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            DELETE FROM categories
            WHERE id = ?
                """,
            (category_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ============ AREAS ============

def list_areas() -> list[dict[str, Any]]:
    """Zwraca listę wszystkich area/krajów pochodzenia.

    Returns:
        list[dict[str, Any]]: Lista słowników z area.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            SELECT id, name 
            FROM areas
            ORDER BY name
                """,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_area_by_id(area_id: int) -> dict[str, Any] | None:
    """Zwraca area po ID albo None, jeśli nie istnieje.

    Args:
        area_id: Klucz główny area.

    Returns:
        dict[str, Any] | None: Słownik area lub None.
    """
    if area_id <= 0:
        raise ValueError("Parametr area_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            SELECT id, name
            FROM areas
            WHERE id = ?
                """,
            (area_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_area(name: str) -> dict[str, Any]:
    """Tworzy area i zwraca utworzony rekord.

    Args:
        name: Nazwa area/kraju.

    Returns:
        dict[str, Any]: Utworzony rekord area.
    """
    if not name.strip():
        raise ValueError("Nazwa area nie może być pusta.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            INSERT INTO areas (name)
            VALUES (?)
                """,
            (name,),
        )
        conn.commit()
        area_id = cursor.lastrowid
        if area_id is None:
            raise RuntimeError("Nie udało się pobrać ID nowego area.")
        created = get_area_by_id(area_id)
        if created is None:
            raise RuntimeError("Nie udało się odczytać utworzonego area.")
        return created
    finally:
        conn.close()


def update_area(area_id: int, name: str | None = None) -> dict[str, Any] | None:
    """Aktualizuje nazwę area.

    Args:
        area_id: Klucz główny area.
        name: Nowa nazwa area/kraju.

    Returns:
        dict[str, Any] | None: Zaktualizowany rekord lub None.
    """
    if area_id <= 0:
        raise ValueError("Parametr area_id musi być > 0.")

    updates: dict[str, str] = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Nazwa area nie może być pusta.")
        updates["name"] = name

    if not updates:
        return get_area_by_id(area_id)

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = list(updates.values()) + [area_id]
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
            UPDATE areas
            SET {set_clause}
            WHERE id = ?
                """,
                tuple(values),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Area o takiej nazwie już istnieje.") from exc
        conn.commit()
        if cursor.rowcount == 0:
            return None

        return get_area_by_id(area_id)
    finally:
        conn.close()


def delete_area(area_id: int) -> bool:
    """Usuwa area po ID.

    Args:
        area_id: Klucz główny area.

    Returns:
        bool: True, jeśli rekord usunięto; False, jeśli rekord nie istniał.
    """
    if area_id <= 0:
        raise ValueError("Parametr area_id musi być > 0.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
                """
            DELETE FROM areas
            WHERE id = ?
                """,
            (area_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()