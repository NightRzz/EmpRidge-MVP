# Frontend - EmpRidge MVP

Frontend aplikacji EmpRidge to SPA w React + TypeScript, pozwalające:
- wyszukiwać przepisy po składnikach z dopasowaniem procentowym,
- filtrować wyniki (kategoria, kraj, minimalny matching ratio, liczba składników),
- przeglądać szczegóły przepisu,
- zarządzać przepisami i składnikami z poziomu panelu admin.

## Stack technologiczny

- React 19
- TypeScript
- Vite
- Material UI (MUI)
- TanStack Query (React Query)
- React Router
- React Hook Form + Zod

## Wymagania

- Node.js 20+ (zalecane LTS)
- npm 10+
- działający backend EmpRidge (`http://localhost:8000` lub inny URL)

## Konfiguracja środowiska

Aplikacja korzysta z `VITE_API_URL` do komunikacji z backendem.

1. Utwórz plik `.env` w katalogu `frontend/`:

```bash
VITE_API_URL=http://localhost:8000
```

2. Jeśli zmienisz URL backendu, zaktualizuj wartość zmiennej.

Domyślnie (gdy brak `.env`) frontend użyje `http://localhost:8000`.

## Uruchomienie lokalne

```bash
cd frontend
npm install
npm run dev
```

Domyślny adres development servera:
- `http://localhost:5173`

## Dostępne skrypty

- `npm run dev` - uruchamia frontend w trybie developerskim (HMR)
- `npm run build` - buduje aplikację produkcyjną (`dist/`)
- `npm run preview` - podgląd buildu produkcyjnego lokalnie
- `npm run lint` - uruchamia ESLint dla całego frontendu

## Routing

Zdefiniowany w `src/app/router.tsx`:
- `/` - strona główna (wyszukiwarka + lista przepisów)
- `/recipe/:id` - szczegóły przepisu
- `/admin/recipes` - panel zarządzania przepisami
- `/admin/ingredients` - panel zarządzania składnikami

## Struktura frontendu

```text
frontend/
├── src/
│   ├── app/                 # bootstrap appki: router, theme, QueryClient
│   ├── components/          # reużywalne komponenty UI
│   ├── hooks/               # custom hooki
│   ├── pages/               # strony routingu
│   │   └── admin/           # widoki panelu administracyjnego
│   ├── services/            # warstwa API (fetch + mapowanie danych)
│   ├── types/               # typy TS i modele API
│   ├── utils/               # helpery (np. YouTube embed)
│   └── main.tsx             # entrypoint React
├── index.html
├── package.json
└── README.md
```

## Architektura i przeplyw danych

- `apiClient.ts` centralizuje wywolania HTTP i obsluge formatu odpowiedzi backendu.
- `services/*Api.ts` udostepniaja funkcje domenowe (recipes, ingredients, categories, areas, search).
- TanStack Query zarzadza cache, loading/error i odswiezaniem danych.
- Strony (`pages/*`) skladaja UI z komponentow i spinaja logike zapytan.
- Formularze admina sa oparte o `react-hook-form` + walidacje przez Zod.

## Glowne komponenty

- `IngredientAutocomplete` - wielokrotny wybor skladnikow z podpowiedziami.
- `SearchFilters` - filtry wyszukiwania przepisow.
- `RecipeCard` - karta przepisu dla list i wynikow.
- `ListPagination` - wspolna paginacja list.
- `ConfirmDialog` - potwierdzanie operacji destrukcyjnych.
- `AppLayout` - layout, nawigacja i kontener widokow.

## Jak rozwijac frontend

1. Uruchom backend.
2. Uruchom frontend (`npm run dev`).
3. Sprawdz lint:

```bash
npm run lint
```

4. Zbuduj aplikacje przed release:

```bash
npm run build
```

## Typowe problemy

- **Brak polaczenia z API**: sprawdz `VITE_API_URL` i CORS po stronie backendu.
- **Puste listy danych**: upewnij sie, ze baza backendu zawiera dane testowe.
- **Bledy linta React hooks**: unikaj synchronicznego `setState` wewnatrz `useEffect`.

## Status

Frontend MVP jest gotowy i obejmuje:
- wyszukiwarke przepisow + filtry,
- szczegoly przepisu,
- panel admin dla przepisow i skladnikow,
- obsluge loading/error/empty states,
- podstawowa walidacje formularzy i UX potwierdzen.
