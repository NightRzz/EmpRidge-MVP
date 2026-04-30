import asyncio
import re
from database import setup_and_import
import aiohttp

# Konfiguracja
MAX_CONCURRENT_REQUESTS = 4
API_BASE = "https://www.themealdb.com/api/json/v1/1/"
API_IMG = "https://www.themealdb.com/images/ingredients/"
MAX_RETRIES = 5
BASE_RETRY_DELAY_SECONDS = 2

DESCRIPTORS_RE = re.compile(r'\b(?:ground|granulated|dried|dry|hot|smoked|flaked|minced|lean|raw|frozen|tinned|unwaxed|pitted|stoned|powdered|icing|soft|light|brown|mixed|whole|shelled|shredded|melted|ready rolled|strong|white|red|green|yellow|small|jumbo|little|zest|powder|paste|puree|purée|stock|cube|stalks|leaves|flakes|seeds|balls|chunks|segments|chopped|diced|sliced|grated|beaten|freshly|cooked|ripe|chilled|cold|boiling|plain|all purpose|full fat|low fat|natural|organic|extra|free-range|liquid)\b', re.IGNORECASE)
SYNONYM_MAP = {
    # Literówki i warianty pisowni
    "hazlenut": "hazelnut",
    "cardomom": "cardamom",
    "chilly": "chili",
    "chilli": "chili",
    "appl": "apple",
    "fry": "fries",
    "peanut cooky": "peanut cookie",
    "asparagu": "asparagus",
    "hummu": "hummus",
    "challot": "shallot",
    "braeburn apple": "apple",
    "bramley apple": "apple",
    "baby new potato": "potato",
    "new potato": "potato",
}


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict | None:
    """Uniwersalna funkcja do pobierania JSONa z API."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    await asyncio.sleep(0.3)
                    return await response.json()

                if response.status == 429:
                    retry_delay = BASE_RETRY_DELAY_SECONDS * attempt
                    print(f"Rate limit (429) dla {url}. Próba {attempt}/{MAX_RETRIES}, czekam {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    continue

                print(f"Nieoczekiwany status {response.status} dla {url}")
                return None
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"Błąd przy {url} po {MAX_RETRIES} próbach: {e}")
                return None

            retry_delay = BASE_RETRY_DELAY_SECONDS * attempt
            print(f"Błąd przy {url}: {e}. Ponawiam za {retry_delay}s ({attempt}/{MAX_RETRIES})...")
            await asyncio.sleep(retry_delay)

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


def get_normalized_name(name: str) -> str:
    """Synchronalna funkcja do normalizacji składnika."""
    if not name:
        return ""

    # 1. Regex - usuwanie przymiotników
    clean = DESCRIPTORS_RE.sub('', name.lower()).strip()

    # 2. Usuwanie zbędnych spacji
    clean = " ".join(clean.split())

    # 3. Prosta lematyzacja (liczba mnoga)
    if clean.endswith('ies'):
        clean = clean[:-3] + 'y'
    elif clean.endswith('es') and len(clean) > 4:
        clean = clean[:-2]
    elif clean.endswith('s') and not clean.endswith('ss'):
        clean = clean[:-1]

    return SYNONYM_MAP.get(clean, clean)


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
            normalized_name = get_normalized_name(ing)
            ingredients.append({
                "name": normalized_name,
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