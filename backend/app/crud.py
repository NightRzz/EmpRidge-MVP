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

def list_ingredients(skip: int = 0, limit: int = 100) -> tuple[list[dict[str, Any]], int]:
    """Pobiera listę składników z bazy danych z obsługą paginacji.

    Args:
        skip: Liczba rekordów do pominięcia od początku listy. Domyślnie 0.
        limit: Maksymalna liczba rekordów do zwrócenia. Domyślnie 100.

    Returns:
        tuple[list[dict[str, Any]], int]: Krotka zawierająca listę słowników
        reprezentujących składniki, posortowanych alfabetycznie według nazwy,
        oraz całkowitą liczbę dostępnych składników.

    Raises:
        ValueError: Jeśli `skip` jest mniejsze niż 0 lub `limit` jest mniejsze lub równe 0.
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
        total_cursor = conn.cursor()
        total_cursor.execute("SELECT COUNT(*) FROM ingredients")
        total_count = total_cursor.fetchone()[0]
        items = [dict(row) for row in cursor.fetchall()]
        return items, total_count
    finally:
        conn.close()


def get_ingredient_by_id(ingredient_id: int) -> dict[str, Any] | None:
    """Pobiera pojedynczy składnik z bazy danych na podstawie jego unikalnego identyfikatora.

    Args:
        ingredient_id: Unikalny identyfikator (ID) składnika.

    Returns:
        dict[str, Any] | None: Słownik zawierający dane składnika (id, name, image_url),
        jeśli składnik o podanym ID istnieje; w przeciwnym razie None.

    Raises:
        ValueError: Jeśli `ingredient_id` jest mniejsze lub równe 0.
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
    """Tworzy nowy składnik w bazie danych.

    Args:
        name: Nazwa składnika. Musi być unikalna i niepusta.
        image_url: Adres URL obrazka składnika. Musi być unikalny i niepusty.

    Returns:
        dict[str, Any]: Słownik reprezentujący nowo utworzony składnik.

    Raises:
        ValueError: Jeśli nazwa lub URL obrazka są puste,
                    lub jeśli składnik o takiej nazwie/URL już istnieje (IntegrityError).
        RuntimeError: Jeśli nie udało się pobrać ID nowego składnika
                      lub odczytać utworzonego rekordu.
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
    """Aktualizuje wybrane pola istniejącego składnika w bazie danych.

    Args:
        ingredient_id: Unikalny identyfikator (ID) składnika do zaktualizowania.
        name: Opcjonalna nowa nazwa składnika. Jeśli podana, nie może być pusta.
        image_url: Opcjonalny nowy adres URL obrazka składnika. Jeśli podany, nie może być pusty.

    Returns:
        dict[str, Any] | None: Słownik zawierający zaktualizowane dane składnika,
        lub None, jeśli składnik o podanym ID nie istnieje.

    Raises:
        ValueError: Jeśli `ingredient_id` jest mniejsze lub równe 0,
                    lub jeśli nowa nazwa/URL obrazka jest pusta po usunięciu białych znaków,
                    lub jeśli aktualizacja narusza unikalność nazwy/URL obrazka (IntegrityError).
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
    """Usuwa składnik z bazy danych na podstawie jego identyfikatora.

    Args:
        ingredient_id: Unikalny identyfikator (ID) składnika do usunięcia.

    Returns:
        bool: True, jeśli składnik został pomyślnie usunięty; False, jeśli składnik o podanym ID nie istniał.

    Raises:
        ValueError: Jeśli `ingredient_id` jest mniejsze lub równe 0.
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

def list_recipes(skip: int = 0, limit: int = 50) -> tuple[list[dict[str, Any]], int]:
    """Pobiera listę przepisów z bazy danych z obsługą paginacji.

    Args:
        skip: Liczba rekordów do pominięcia od początku listy. Domyślnie 0.
        limit: Maksymalna liczba rekordów do zwrócenia. Domyślnie 50.

    Returns:
        tuple[list[dict[str, Any]], int]: Krotka zawierająca listę słowników
        reprezentujących przepisy, posortowanych alfabetycznie według tytułu,
        oraz całkowitą liczbę dostępnych przepisów.

    Raises:
        ValueError: Jeśli `skip` jest mniejsze niż 0 lub `limit` jest mniejsze lub równe 0.
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
        total_cursor = conn.cursor()
        total_cursor.execute("SELECT COUNT(*) FROM recipes")
        total_count = total_cursor.fetchone()[0]
        items = [dict(row) for row in cursor.fetchall()]
        return items, total_count
    finally:
        conn.close()


def get_recipe_by_id(recipe_id: int) -> dict[str, Any] | None:
    """Pobiera pojedynczy przepis z bazy danych na podstawie jego unikalnego identyfikatora,
    wraz z przypisanymi do niego składnikami.

    Args:
        recipe_id: Unikalny identyfikator (ID) przepisu.

    Returns:
        dict[str, Any] | None: Słownik zawierający dane przepisu (id, title, instructions,
        image_url, youtube_url, category_id, area_id) oraz zagnieżdżoną listę
        składników (`ingredients`), jeśli przepis o podanym ID istnieje; w przeciwnym razie None.
        Lista składników zawiera (ingredient_id, name, image_url, measure).

    Raises:
        ValueError: Jeśli `recipe_id` jest mniejsze lub równe 0.
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
        if row is None:
            return None
        recipe_dict = dict(row)
        cursor.execute(
            """
            SELECT i.id AS ingredient_id,
                   i.name AS name,
                   i.image_url AS image_url,
                   ri.measure AS measure
            FROM recipe_ingredients ri
            JOIN ingredients i ON i.id = ri.ingredient_id
            WHERE ri.recipe_id = ?
            ORDER BY i.name COLLATE NOCASE
            """,
            (recipe_id,),
        )
        recipe_dict["ingredients"] = [dict(item) for item in cursor.fetchall()]
        return recipe_dict
    finally:
        conn.close()


def replace_recipe_ingredients(
    recipe_id: int,
    lines: list[tuple[int, str | None]],
) -> dict[str, Any] | None:
    """Całkowicie zastępuje listę składników dla danego przepisu.
    Składniki muszą już istnieć w katalogu `ingredients`.

    Args:
        recipe_id: Identyfikator przepisu, dla którego składniki mają zostać zastąpione.
        lines: Lista krotek, gdzie każda krotka zawiera `(ingredient_id, measure)`.
               `ingredient_id` to ID istniejącego składnika, a `measure` to opcjonalna miara (np. "1 szklanka").

    Returns:
        dict[str, Any] | None: Zaktualizowany przepis (zawierający nową listę składników)
        lub None, jeśli przepis o podanym `recipe_id` nie istnieje.

    Raises:
        ValueError: Jeśli `recipe_id` jest mniejsze lub równe 0,
                    `ingredient_id` jest mniejsze lub równe 0,
                    lub jeśli lista `lines` zawiera zduplikowane `ingredient_id`.
    """
    if recipe_id <= 0:
        raise ValueError("Parametr recipe_id musi być > 0.")

    seen_ids: set[int] = set()
    for ingredient_id, _measure in lines:
        if ingredient_id <= 0:
            raise ValueError("Parametr ingredient_id musi być > 0.")
        if ingredient_id in seen_ids:
            raise ValueError("Lista składników zawiera duplikat tego samego składnika.")
        seen_ids.add(ingredient_id)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
        if cursor.fetchone() is None:
            return None

        cursor.execute(
            """
            DELETE FROM recipe_ingredients
            WHERE recipe_id = ?
            """,
            (recipe_id,),
        )
        for ingredient_id, measure in lines:
            cleaned: str | None
            if measure is None:
                cleaned = None
            else:
                trimmed = measure.strip()
                cleaned = trimmed if trimmed else None
            cursor.execute(
                """
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, measure)
                VALUES (?, ?, ?)
                """,
                (recipe_id, ingredient_id, cleaned),
            )
        conn.commit()
    finally:
        conn.close()

    return get_recipe_by_id(recipe_id)


def create_recipe(
    title: str,
    instructions: str | None = None,
    image_url: str | None = None,
    youtube_url: str | None = None,
    category_id: int | None = None,
    area_id: int | None = None,
) -> dict[str, Any]:
    """Tworzy nowy przepis w bazie danych.

    Args:
        title: Tytuł przepisu. Musi być niepusty po usunięciu białych znaków.
        instructions: Opcjonalne instrukcje przygotowania przepisu.
        image_url: Opcjonalny adres URL zdjęcia przepisu.
        youtube_url: Opcjonalny adres URL filmu YouTube powiązanego z przepisem.
        category_id: Opcjonalny identyfikator kategorii, do której należy przepis.
        area_id: Opcjonalny identyfikator obszaru geograficznego/kraju pochodzenia przepisu.

    Returns:
        dict[str, Any]: Słownik reprezentujący nowo utworzony przepis.

    Raises:
        ValueError: Jeśli `title` jest pusty po usunięciu białych znaków.
        RuntimeError: Jeśli nie udało się pobrać ID nowego przepisu
                      lub odczytać utworzonego rekordu.
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
    """Aktualizuje wybrane pola istniejącego przepisu w bazie danych.

    Args:
        recipe_id: Unikalny identyfikator (ID) przepisu do zaktualizowania.
        title: Opcjonalny nowy tytuł przepisu. Jeśli podany, nie może być pusta.
        instructions: Opcjonalne nowe instrukcje przygotowania.
        image_url: Opcjonalny nowy adres URL zdjęcia przepisu.
        youtube_url: Opcjonalny nowy adres URL filmu YouTube.
        category_id: Opcjonalny nowy identyfikator kategorii.
        area_id: Opcjonalny nowy identyfikator obszaru geograficznego/kraju.

    Returns:
        dict[str, Any] | None: Słownik zawierający zaktualizowane dane przepisu,
        lub None, jeśli przepis o podanym ID nie istnieje.

    Raises:
        ValueError: Jeśli `recipe_id` jest mniejsze lub równe 0,
                    lub jeśli nowy tytuł jest pusty po usunięciu białych znaków.
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
    """Usuwa przepis z bazy danych na podstawie jego identyfikatora.

    Args:
        recipe_id: Unikalny identyfikator (ID) przepisu do usunięcia.

    Returns:
        bool: True, jeśli przepis został pomyślnie usunięty; False, jeśli przepis o podanym ID nie istniał.

    Raises:
        ValueError: Jeśli `recipe_id` jest mniejsze lub równe 0.
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
    """Pobiera listę wszystkich kategorii z bazy danych.

    Returns:
        list[dict[str, Any]]: Lista słowników reprezentujących kategorie,
        posortowanych alfabetycznie według nazwy.
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
    """Pobiera pojedynczą kategorię z bazy danych na podstawie jej unikalnego identyfikatora.

    Args:
        category_id: Unikalny identyfikator (ID) kategorii.

    Returns:
        dict[str, Any] | None: Słownik zawierający dane kategorii (id, name),
        jeśli kategoria o podanym ID istnieje; w przeciwnym razie None.

    Raises:
        ValueError: Jeśli `category_id` jest mniejsze lub równe 0.
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
    """Tworzy nową kategorię w bazie danych.

    Args:
        name: Nazwa kategorii. Musi być unikalna i niepusta.

    Returns:
        dict[str, Any]: Słownik reprezentujący nowo utworzoną kategorię.

    Raises:
        ValueError: Jeśli nazwa kategorii jest pusta po usunięciu białych znaków.
        RuntimeError: Jeśli nie udało się pobrać ID nowej kategorii
                      lub odczytać utworzonego rekordu.
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
    """Aktualizuje nazwę istniejącej kategorii w bazie danych.

    Args:
        category_id: Unikalny identyfikator (ID) kategorii do zaktualizowania.
        name: Opcjonalna nowa nazwa kategorii. Jeśli podana, nie może być pusta.

    Returns:
        dict[str, Any] | None: Słownik zawierający zaktualizowane dane kategorii,
        lub None, jeśli kategoria o podanym ID nie istnieje.

    Raises:
        ValueError: Jeśli `category_id` jest mniejsze lub równe 0,
                    lub jeśli nowa nazwa kategorii jest pusta po usunięciu białych znaków,
                    lub jeśli aktualizacja narusza unikalność nazwy (IntegrityError).
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
    """Usuwa kategorię z bazy danych na podstawie jej identyfikatora.

    Args:
        category_id: Unikalny identyfikator (ID) kategorii do usunięcia.

    Returns:
        bool: True, jeśli kategoria została pomyślnie usunięta; False, jeśli kategoria o podanym ID nie istniała.

    Raises:
        ValueError: Jeśli `category_id` jest mniejsze lub równe 0.
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
    """Pobiera listę wszystkich obszarów geograficznych (area) z bazy danych.

    Returns:
        list[dict[str, Any]]: Lista słowników reprezentujących obszary,
        posortowanych alfabetycznie według nazwy.
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
    """Pobiera pojedynczy obszar geograficzny (area) z bazy danych na podstawie jego unikalnego identyfikatora.

    Args:
        area_id: Unikalny identyfikator (ID) obszaru.

    Returns:
        dict[str, Any] | None: Słownik zawierający dane obszaru (id, name),
        jeśli obszar o podanym ID istnieje; w przeciwnym razie None.

    Raises:
        ValueError: Jeśli `area_id` jest mniejsze lub równe 0.
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
    """Tworzy nowy obszar geograficzny (area) w bazie danych.

    Args:
        name: Nazwa obszaru/kraju. Musi być unikalna i niepusta.

    Returns:
        dict[str, Any]: Słownik reprezentujący nowo utworzony obszar.

    Raises:
        ValueError: Jeśli nazwa obszaru jest pusta po usunięciu białych znaków.
        RuntimeError: Jeśli nie udało się pobrać ID nowego obszaru
                      lub odczytać utworzonego rekordu.
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
    """Aktualizuje nazwę istniejącego obszaru geograficznego (area) w bazie danych.

    Args:
        area_id: Unikalny identyfikator (ID) obszaru do zaktualizowania.
        name: Opcjonalna nowa nazwa obszaru/kraju. Jeśli podana, nie może być pusta.

    Returns:
        dict[str, Any] | None: Słownik zawierający zaktualizowane dane obszaru,
        lub None, jeśli obszar o podanym ID nie istnieje.

    Raises:
        ValueError: Jeśli `area_id` jest mniejsze lub równe 0,
                    lub jeśli nowa nazwa obszaru jest pusta po usunięciu białych znaków,
                    lub jeśli aktualizacja narusza unikalność nazwy (IntegrityError).
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
    """Usuwa obszar geograficzny (area) z bazy danych na podstawie jego identyfikatora.

    Args:
        area_id: Unikalny identyfikator (ID) obszaru do usunięcia.

    Returns:
        bool: True, jeśli obszar został pomyślnie usunięty; False, jeśli obszar o podanym ID nie istniał.

    Raises:
        ValueError: Jeśli `area_id` jest mniejsze lub równe 0.
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

# ============ SEARCH ============

def search_recipes(
    ingredient_ids: list[int],
    category_id: int | None = None,
    area_id: int | None = None,
    min_matching_ratio: float = 0.0,
    max_total_ingredients: int | None = None,
    skip: int = 0,
    limit: int = 24,
) -> tuple[list[dict[str, Any]], int]:
    """Wyszukuje przepisy na podstawie listy składników, z opcjonalnymi filtrami
    kategorii i obszaru, oraz zwraca wyniki z obliczonym wskaźnikiem dopasowania.
    Obsługuje również paginację.

    Args:
        ingredient_ids: Lista identyfikatorów składników, które muszą być obecne w przepisie.
                        Lista nie może być pusta, a wszystkie ID muszą być > 0.
        category_id: Opcjonalny identyfikator kategorii do filtrowania przepisów.
        area_id: Opcjonalny identyfikator obszaru geograficznego do filtrowania przepisów.
        min_matching_ratio: Minimalny wymagany wskaźnik dopasowania (w procentach, od 0 do 100).
                            Przepisy o niższym wskaźniku zostaną odrzucone. Domyślnie 0.0.
        max_total_ingredients: Opcjonalna maksymalna liczba wszystkich składników w przepisie.
        skip: Liczba rekordów do pominięcia od początku listy. Domyślnie 0.
        limit: Maksymalna liczba rekordów do zwrócenia. Domyślnie 24.

    Returns:
        tuple[list[dict[str, Any]], int]: Krotka zawierająca listę słowników reprezentujących znalezione przepisy
        oraz całkowitą liczbę dopasowanych przepisów przed paginacją. Każdy przepis zawiera
        dodatkowe pola: `matched_count` (liczba dopasowanych składników z `ingredient_ids`),
        `total_count` (łączna liczba składników w przepisie) i `matching_ratio` (wskaźnik dopasowania w procentach).
        Wyniki są sortowane malejąco według `matching_ratio`, a następnie `matched_count`,
        a na końcu alfabetycznie według `title`.

    Raises:
        ValueError: Jeśli `ingredient_ids` jest puste, zawiera ID <= 0,
                    `min_matching_ratio` jest poza zakresem 0-100,
                    `max_total_ingredients` jest mniejsze lub równe 0,
                    `skip` jest mniejsze niż 0, lub `limit` jest mniejsze lub równe 0 albo większe niż 100.
    """

    if not ingredient_ids:
        raise ValueError("ingredient_ids nie może być puste.")
    if any(item <= 0 for item in ingredient_ids):
        raise ValueError("Wszystkie ingredient_ids muszą być > 0.")
    if min_matching_ratio < 0 or min_matching_ratio > 100:
        raise ValueError("min_matching_ratio musi być w zakresie 0-100.")
    if max_total_ingredients is not None and max_total_ingredients <= 0:
        raise ValueError("max_total_ingredients musi być > 0.")
    if skip < 0:
        raise ValueError("Parametr skip musi być >= 0.")
    if limit <= 0 or limit > 100:
        raise ValueError("Parametr limit musi być > 0 i <= 100.")

    placeholders = ",".join("?" for _ in ingredient_ids)

    filtered_sql = f"""
            SELECT
                r.id,
                r.title,
                r.instructions,
                r.image_url,
                r.youtube_url,
                r.category_id,
                r.area_id,
                SUM(CASE WHEN ri.ingredient_id IN ({placeholders}) THEN 1 ELSE 0 END) AS matched_count,
                COUNT(ri.ingredient_id) AS total_count,
                ROUND(
                    (SUM(CASE WHEN ri.ingredient_id IN ({placeholders}) THEN 1 ELSE 0 END) * 100.0)
                    / COUNT(ri.ingredient_id),
                    2
                ) AS matching_ratio
            FROM recipes r
            JOIN recipe_ingredients ri ON ri.recipe_id = r.id
            WHERE 1=1
    """

    params: list[Any] = ingredient_ids + ingredient_ids

    if category_id is not None:
        filtered_sql += " AND r.category_id = ?"
        params.append(category_id)

    if area_id is not None:
        filtered_sql += " AND r.area_id = ?"
        params.append(area_id)

    filtered_sql += """
            GROUP BY r.id
            HAVING matching_ratio >= ?
        """
    params.append(min_matching_ratio)

    if max_total_ingredients is not None:
        filtered_sql += " AND total_count <= ?"
        params.append(max_total_ingredients)

    count_sql = f"SELECT COUNT(*) AS c FROM (\n{filtered_sql}\n) AS _hits"

    ordered_sql = f"""
            {filtered_sql}
            ORDER BY matching_ratio DESC, matched_count DESC, r.title ASC
            LIMIT ? OFFSET ?
        """

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(count_sql, tuple(params))
        count_row = cursor.fetchone()
        total = int(count_row["c"]) if count_row else 0

        data_params = list(params) + [limit, skip]
        cursor.execute(ordered_sql, tuple(data_params))
        items = [dict(row) for row in cursor.fetchall()]
        return items, total
    finally:
        conn.close()


def suggest_ingredients(query: str, limit: int = 15) -> list[dict]:
    """Wyszukuje składniki, których nazwa pasuje do podanego ciągu zapytania (częściowe dopasowanie, bez uwzględniania wielkości liter).

    Args:
        query: Ciąg znaków do wyszukania w nazwach składników. Nie może być pusty.
        limit: Maksymalna liczba sugestii do zwrócenia. Domyślnie 15.

    Returns:
        list[dict]: Lista słowników reprezentujących pasujące składniki (id, name, image_url),
        posortowanych alfabetycznie według nazwy.

    Raises:
        ValueError: Jeśli `query` jest pusty po usunięciu białych znaków,
                    lub `limit` jest mniejsze lub równe 0, lub większe niż 20.
    """

    if not query.strip():
        raise ValueError("Nazwa query nie może być pusta.")

    if limit <= 0 or limit > 20:
        raise ValueError("Parametr limit musi być > 0 i <= 20.")


    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, image_url
            FROM ingredients
            WHERE name LIKE LOWER(?)
            ORDER BY name
            LIMIT ?
            """,
            (f"%{query}%", limit),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()