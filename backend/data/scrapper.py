import asyncio
import sqlite3
from pathlib import Path

import aiohttp

# Konfiguracja
MAX_CONCURRENT_REQUESTS = 4
API_BASE = "https://www.themealdb.com/api/json/v1/1/"
API_IMG = "https://www.themealdb.com/images/ingredients/"

async def fetch_json(session, url):
    """Uniwersalna funkcja do pobierania JSONa z API."""
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                await asyncio.sleep(0.3)
                return await response.json()

            if response.status == 429:
                print("Rate limit! Czekam 5s...")
                await asyncio.sleep(5)
                return await fetch_json(session, url)
            return None
    except Exception as e:
        print(f"Błąd przy {url}: {e}")
        return None


async def get_meal_ids(session):
    """Pobiera unikalne ID wszystkich przepisów ze wszystkich kategorii."""
    print("Pobieram listę kategorii...")
    cat_data = await fetch_json(session, f"{API_BASE}list.php?c=list")
    if not cat_data: return []

    categories = [cat['strCategory'] for cat in cat_data['meals']]

    # Pobieramy listy posiłków dla wszystkich kategorii współbieżnie
    tasks = [fetch_json(session, f"{API_BASE}filter.php?c={category}") for category in categories]
    results = await asyncio.gather(*tasks)

    meal_ids = set()  # Set, żeby uniknąć duplikatów
    for res in results:
        if res and res.get('meals'):
            for m in res['meals']:
                meal_ids.add(m['idMeal'])

    print(f"Znaleziono {len(meal_ids)} unikalnych ID posiłków.")
    return list(meal_ids)


async def fetch_meal_details(session, meal_id, semaphore):
    """Pobiera pełne dane o przepisie"""
    async with semaphore:
        url = f"{API_BASE}lookup.php?i={meal_id}"
        data = await fetch_json(session, url)

        if not data or not data.get('meals'):
            return None

        meal = data['meals'][0]

        # ekstrakcja skladników i miar do listy par (składnik, miara)
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f'strIngredient{i}')
            meas = meal.get(f'strMeasure{i}')
            if ing and ing.strip():
                ingredients.append({
                    "name": ing.strip().lower(),
                    "measure": meas.strip() if meas else ""
                })

        return {
            "id": meal['idMeal'],
            "title": meal['strMeal'],
            "category": meal['strCategory'],
            "area": meal['strArea'],
            "instructions": meal['strInstructions'],
            "thumbnail": meal['strMealThumb'],
            "youtube":meal['strYoutube'],
            "ingredients": ingredients
        }


async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    final_meals = []

    async with aiohttp.ClientSession() as session:
        meal_ids = await get_meal_ids(session)
        if not meal_ids: return

        tasks = [fetch_meal_details(session, meal_id, semaphore) for meal_id in meal_ids]

        print(f"Pobieranie {len(meal_ids)} przepisów.")

        # as_completed dla wyświetlania postępu na bieżąco
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                final_meals.append(result)
                if len(final_meals) % 25 == 0:
                    print(f"Pobrano {len(final_meals)}/{len(meal_ids)}...")

    print("Zapisywanie danych do bazy SQLite...")
    import_to_database(final_meals)
    print("Gotowe! Dane są w bazie.")


def get_or_create_id(cursor, table, name, img_url=None):
    """Helper, zwraca ID rekordu, tworzy go jeśli nie istnieje."""
    columns = "(name, image_url)" if img_url else "(name)"
    params = [name, img_url] if img_url else [name]
    cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]


    cursor.execute(f"INSERT INTO {table} {columns}  VALUES ({'?'+ ',?' * bool(img_url)})", tuple(params))
    return cursor.lastrowid

def import_to_database(meals_list):
    conn = sqlite3.connect(Path(__file__).parent / "empridge.db")
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
                ing_id = get_or_create_id(cursor, "ingredients", ing['name'], f"{API_IMG}{ing['name']}.png")
                cursor.execute('''
                    INSERT OR REPLACE INTO recipe_ingredients (recipe_id, ingredient_id, measure)
                    VALUES (?, ?, ?)
                ''', (meal['id'], ing_id, ing['measure']))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Błąd podczas zapisu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())