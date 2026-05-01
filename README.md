# EmpRidge MVP

https://github.com/user-attachments/assets/7d26e760-4a2e-484a-aa52-f4eeb0ce474c


**Aplikacja do wyszukiwania przepisów na podstawie składników, które masz w domu.**

Aplikacja do wyszukiwania przepisów kulinarnych na podstawie posiadanych składników. Technologia dopasowuje przepisy i pokazuje, ile procent składników do nich pasuje.

## Funkcje

-  **Wyszukiwanie przepisów** — na podstawie wybranych składników
-  **Współczynnik dopasowania** — procent dopasowania składników do każdego przepisu
-  **Filtry** — kategoria, kraj pochodzenia, liczba składników
-  **Autouzupełnianie** — podpowiedzi składników podczas wpisywania
-  **Szczegóły przepisu** — instrukcje, zdjęcia, linki YouTube
-  **Frontend** — React + Vite + MUI (gotowy w zakresie MVP)

##  Stack technologiczny

### Backend
- **Python 3.11+**
- **FastAPI** — framework REST API
- **SQLite** — baza danych  
- **Pydantic** — walidacja i serializacja danych
- **uvicorn** — serwer ASGI

### Frontend
- **React 18+**
- **Vite** — narzędzie budowania
- **Material-UI (MUI)** — komponenty UI

### Zewnętrzne API
- **TheMealDB** — źródło przepisów (scrapper)

## Struktura projektu

```
EmpRidge-MVP/
├── backend/
│   ├── app/                          # FastAPI aplikacja
│   │   ├── __init__.py
│   │   ├── main.py                   # Główna aplikacja
│   │   ├── schemas.py                # Modele Pydantic (Request/Response)
│   │   ├── crud.py                   # Operacje na bazie danych
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── recipes.py            # Endpointy przepisów
│   │       ├── ingredients.py        # Endpointy składników + sugestie
│   │       ├── categories.py         # Endpointy kategorii
│   │       ├── areas.py              # Endpointy area
│   │       └── search.py             # Endpoint wyszukiwania przepisów
│   ├── tests/
│   │   └── test_smoke_search.py      # Smoke test endpointu search
│   ├── data/
│   │   ├── database.py               # DB helpers (legacy)
│   │   ├── scrapper.py               # Import danych z TheMealDB
│   │   └── empridge.db               # SQLite plik
│   └── sql/
│       └── schema.sql                # Schemat bazy danych
├── frontend/                         # React app
│   ├── public/                       # Statyczne zasoby
│   ├── src/                          # Kod źródłowy React
│   │   ├── app/                      # Główna konfiguracja (router, theme, App)
│   │   ├── assets/                   # Statyczne zasoby (obrazy, ikony)
│   │   ├── components/               # Ogólne komponenty UI
│   │   ├── hooks/                    # Customowe hooki React
│   │   ├── pages/                    # Komponenty stron/widoków
│   │   ├── services/                 # Warstwa komunikacji z API
│   │   ├── types/                    # Definicje typów TypeScript
│   │   └── main.tsx                  # Punkt wejścia aplikacji
│   ├── index.html                    # Główny plik HTML
│   ├── package.json                  # Zależności i skrypty npm
│   ├── tsconfig.json                 # Konfiguracja TypeScript
│   └── vite.config.ts                # Konfiguracja Vite
├── requirements.txt                  # Python dependencies
├── README.md                         # Dokumentacja (ten plik)
└── .cursor/rules/                    # Reguły Cursor (konwencje backendu)
```

## Baza danych

### Tabele
- `recipes` — przepisy kulinarnych
- `ingredients` — składniki
- `categories` — kategorie (np. Breakfast, Lunch)
- `areas` — kraje pochodzenia (np. Italian, Polish)
- `recipe_ingredients` — relacja Many-to-Many z miarą

### Schema
Zdefiniowany w `backend/sql/schema.sql` — ustalony z uwzględnieniem relacji i constraints.

## Uruchomienie

### Backend

1. **Zainstaluj zależności**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uruchom serwer**
   ```bash
   python -m uvicorn backend.app.main:app --reload
   ```

3. **API będzie dostępne na**
   - API: `http://localhost:8000`
   - Dokumentacja interaktywna: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

4. **(Opcjonalnie) Zasilenie bazy danymi z TheMealDB**
   ```bash
   python backend/data/scrapper.py
   ```

### Frontend
Szczegółowa instrukcja - /frontend/README.md
```bash
cd frontend
npm install
npm run dev
```

##  Endpointy API

### Przepisy
- `GET /recipes` — lista przepisów (paginacja)
- `GET /recipes/{id}` — szczegóły przepisu
- `POST /recipes` — tworzenie przepisu
- `PUT /recipes/{id}` — edycja przepisu
- `DELETE /recipes/{id}` — usuwanie przepisu

### Składniki
- `GET /ingredients` — lista składników (paginacja)
- `GET /ingredients/suggestions?query={text}&limit={n}` — podpowiedzi składników (autocomplete)
- `GET /ingredients/{id}` — szczegóły składnika
- `POST /ingredients` — tworzenie składnika
- `PUT /ingredients/{id}` — edycja składnika
- `DELETE /ingredients/{id}` — usuwanie składnika

### Kategorie
- `GET /categories` — lista kategorii
- `GET /categories/{id}` — szczegóły kategorii
- `POST /categories` — tworzenie kategorii
- `PUT /categories/{id}` — edycja kategorii
- `DELETE /categories/{id}` — usuwanie kategorii

### Area / kraje pochodzenia
- `GET /areas` — lista area
- `GET /areas/{id}` — szczegóły area
- `POST /areas` — tworzenie area
- `PUT /areas/{id}` — edycja area
- `DELETE /areas/{id}` — usuwanie area

### Wyszukiwanie przepisów
- `POST /search-recipes` — wyszukiwanie po składnikach + matching ratio + filtry

## Status

### Zrobione
- [x] Backend (Python FastAPI SQLite)
   - [x] Schemat bazy danych
   - [x] Import danych z TheMealDB (scrapper)
   - [x] Modele Pydantic
   - [x] CRUD funkcje w bazie
   - [x] Konfiguracja FastAPI
   - [x] CRUD endpointy (recipes, ingredients, categories, areas)
   - [x] Endpoint podpowiedzi składników (`/ingredients/suggestions`)
   - [x] Endpoint wyszukiwania
   - [x] Współczynnik dopasowania
   - [x] Filtry
   - [x] Silnik wyszukiwania
   - [x] CORS pod frontend dev (`localhost:5173`)
   - [x] Smoke testy backendu (search)
   - [x] Dokumentacja API

- [x] Frontend (React + Vite + MUI)
   - [x] Inicjalizacja projektu (Vite, React, TS, zależności)
   - [x] Konfiguracja routingu, MUI theme, layoutu i QueryClient
   - [x] Warstwa API do komunikacji z backendem
   - [x] Strona główna z wyszukiwaniem i filtrami
   - [x] Strona szczegółów przepisu
   - [x] Autocomplete składników + wybór składników
   - [x] Uproszczony CRUD dla przepisów i składników (admin)
   - [x] Loading/error/empty states, snackbar i confirm dialog
   - [x] Dokumentacja frontendu (`frontend/README.md`)
   - [x] Smoke testy frontendu (layout, strony główne, szczegóły przepisów)


## Ciekawsze rozwiązania poza MVP

Poniżej kierunki, które mogłyby zastąpić obecne proste rozwiązania MVP:

### Backend / dane
- **PostgreSQL zamiast SQLite** - lepsza współbieżność, indeksowanie i skalowalność.
- **SQLAlchemy + Alembic** - wygodniejsze modelowanie domeny i migracje schematu.
- **Redis cache** - szybsze odpowiedzi dla często wywoływanych endpointów.

### Wyszukiwanie i ranking
- **Fuzzy matching + synonimy** - lepsze wyniki przy literówkach i wariantach nazw.

### Jakość i DevOps
- **Testy E2E (Playwright/Cypress)** - pełne scenariusze użytkownika.
- **Observability (Sentry + metryki + tracing)** - szybsze wykrywanie i analiza problemów.
- **CI/CD** - automatyczne lint/test/build/deploy.
- **Docker Compose** - spójne środowisko lokalne i prostszy onboarding.

## Gotowe funkcje CRUD (backend/app/crud.py)

### Recipes
- `list_recipes`
- `get_recipe_by_id`
- `create_recipe`
- `update_recipe`
- `delete_recipe`

### Ingredients
- `list_ingredients`
- `get_suggestions`
- `get_ingredient_by_id`
- `create_ingredient`
- `update_ingredient`
- `delete_ingredient`

### Categories
- `list_categories`
- `get_category_by_id`
- `create_category`
- `update_category`
- `delete_category`

### Areas
- `list_areas`
- `get_area_by_id`
- `create_area`
- `update_area`
- `delete_area`

## Konwencje kodowania (AI / Cursor)

Reguły dla asystenta: `.cursor/rules/` — przy pracy nad `backend/**/*.py` stosuje się m.in. type hints, docstringi Google, wrapper `APIResponse`, SQLite synchronicznie, granice edycji plików.

## Użycie AI

Użyłem Cursor do generowania `README.md`, GitHub Issues, konsultacji architektury rozwiązania (planning), normalizacji nazw składników (w `scrapper.py`) i debugowania wybranych błędów.
Także do generowania boilerplate'ów CRUD/endpointów, rozbudowanych docstringów, code review i testów automatycznych endpointów.
Cursor wspierał mnie również w pracy
nad frontendem, pomagał w tworzeniu komponentów React, konfiguracji TypeScript i optymalizacji kodu UI.

Użyłem Cursor BugBota do precyzyjnego zidentyfikowania bugów w kodzie.

Użyłem Copilot do utworzenia `.gitignore` i szczegółowego opisu pull requestów. 

## Licencja

MIT

## 👤 Autor

**NightRzz**

---

**Uwaga**: Projekt jest w fazie MVP. Backend i frontend działają w zakresie funkcji opisanych w dokumentacji.
