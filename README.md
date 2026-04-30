# EmpRidge MVP

**Aplikacja do wyszukiwania przepisów na podstawie składników, które masz w domu.**

Aplikacja do wyszukiwania przepisów kulinarnych na podstawie posiadanych składników. Technologia dopasowuje przepisy i pokazuje, ile procent składników do nich pasuje.

## Funkcje

-  **Wyszukiwanie przepisów** — na podstawie wybranych składników
-  **Współczynnik dopasowania** — procent dopasowania składników do każdego przepisu
-  **Filtry** — kategoria, kraj pochodzenia, liczba składników
-  **Autouzupełnianie** — podpowiedzi składników podczas wpisywania
-  **Szczegóły przepisu** — instrukcje, zdjęcia, linki YouTube
-  **Frontend** — React + Vite + MUI (w trakcie)

##  Stack technologiczny

### Backend
- **Python 3.11+**
- **FastAPI** — framework REST API
- **SQLite** — baza danych
- **Pydantic** — walidacja i serializacja danych
- **uvicorn** — serwer ASGI

### Frontend (TODO)
- **React 18+**
- **Vite** — narzędzie budowania
- **Material-UI (MUI)** — komponenty UI

### Zewnętrzne API
- **TheMealDB** — źródło przepisów (scrapper)

##  Struktura projektu

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
│   │       └── recipes.py            # CRUD endpoints
│   ├── data/
│   │   ├── database.py               # DB helpers (legacy)
│   │   ├── scrapper.py               # Import danych z TheMealDB
│   │   ├── empridge.db               # SQLite plik
│   │   └── empridge - Copy.db        # Backup
│   └── sql/
│       └── schema.sql                # Schemat bazy danych
├── frontend/                          # (TODO) React app
├── requirements.txt                  # Python dependencies
├── README.md                         # Dokumentacja (ten plik)
└── .cursor/rules/                    # Reguły Cursor (konwencje backendu)
```

## ️ Baza danych

### Tabele
- `recipes` — przepisy kulinarnych
- `ingredients` — składniki
- `categories` — kategorie (np. Breakfast, Lunch)
- `areas` — kraje pochodzenia (np. Italian, Polish)
- `recipe_ingredients` — relacja Many-to-Many z miarą

### Schema
Zdefiniowany w `backend/sql/schema.sql` — ustalony z uwzględnieniem relacji i constraints.

##  Uruchomienie

### Backend

1. **Zainstaluj zależności**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uruchom serwer**
   ```bash
   cd C:\Users\Nightrzz\PycharmProjects\EmpRidge-MVP
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

### Frontend (TODO)
```bash
cd frontend
npm install
npm run dev
```

##  Endpointy API

### Przepisy
- `GET /recipes` — lista przepisów (paginacja)
- `GET /recipes/{id}` — szczegóły przepisu
- `POST /recipes` — tworzenie przepisu (admin)
- `PUT /recipes/{id}` — edycja przepisu (admin)
- `DELETE /recipes/{id}` — usuwanie przepisu (admin)

### Dane pomocnicze
- `GET /recipes/lists/categories` — lista kategorii
- `GET /recipes/lists/areas` — lista area

### Wyszukiwanie (TODO)
- `POST /search-recipes` — wyszukiwanie po składnikach

##  Status

###  Zrobione
- [x] Schemat bazy danych
- [x] Import danych z TheMealDB (scrapper)
- [x] Modele Pydantic
- [x] CRUD funkcje w bazie
- [x] Konfiguracja FastAPI

###  W trakcie (Issues #1-3)
- [ ] CRUD endpointy (recipes, ingredients, categories, areas)
- [ ] Endpoint wyszukiwania
- [ ] Współczynnik dopasowania
- [ ] Filtry

###  TODO
- [ ] Testy backendu
- [ ] Frontend (React + Vite + MUI)
- [ ] Silnik wyszukiwania
- [ ] Dokumentacja API

##  Konwencje kodowania (AI / Cursor)

Reguły dla asystenta: `.cursor/rules/` — przy pracy nad `backend/**/*.py` stosuje się m.in. type hints, docstringi Google, wrapper `APIResponse`, SQLite synchronicznie, granice edycji plików.

##  Użycie AI

Użyłem Cursor do generowania `README.md`, GitHub Issues, konsultacji architektury rozwiązania (planning), normalizacji nazw składników (w `scrapper.py`) i debugowania wybranych błędów.
Generowania boilerplate'ów do CRUDa, code review

Użyłem Copilot do utworzenia `.gitignore` i szczegółowego opisu pull requestu.
 
##  Licencja

MIT

## 👤 Autor

**NightRzz**

---

**Uwaga**: Projekt jest w fazie MVP. Backend jest w trakcie rozwoju, frontend planowany na później.
