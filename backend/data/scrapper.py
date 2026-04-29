import asyncio
import sqlite3
from pathlib import Path
from database import setup_and_import
import aiohttp

# Konfiguracja
MAX_CONCURRENT_REQUESTS = 4
API_BASE = "https://www.themealdb.com/api/json/v1/1/"
API_IMG = "https://www.themealdb.com/images/ingredients/"


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict | None:
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


async def get_meal_ids(session: aiohttp.ClientSession) -> list[str]:
    """Pobiera unikalne ID wszystkich przepisów ze wszystkich kategorii."""
    print("Pobieram listę kategorii...")
    cat_data = await fetch_json(session, f"{API_BASE}list.php?c=list")
    if not cat_data: return []

    categories = [cat['strCategory'] for cat in cat_data['meals']]

    # Pobieramy listy id posiłków dla wszystkich kategorii konkurencyjnie
    tasks = [fetch_json(session, f"{API_BASE}filter.php?c={category}") for category in categories]
    results = await asyncio.gather(*tasks)

    meal_ids = set()  # Set, żeby uniknąć duplikatów
    for res in results:
        if res and res.get('meals'):
            for m in res['meals']:
                meal_ids.add(m['idMeal'])

    print(f"Znaleziono {len(meal_ids)} ID posiłków.")
    return list(meal_ids)


async def fetch_meal_details(
        session: aiohttp.ClientSession,
        meal_id: str,
        semaphore: asyncio.Semaphore
        ) -> dict | None:
    """Pobiera pełne dane przepisu z API; Zwraca sformatowany słownik."""

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
    try:
        setup_and_import(final_meals, API_IMG)
    except Exception as e:
        print(f"Import nie powiódł się: {e}")
    else:
        print("Gotowe! Dane są w bazie.")


if __name__ == "__main__":
    asyncio.run(main())