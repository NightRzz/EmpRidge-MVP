import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import (
    APIResponse,
    RecipeCreate,
    RecipeIngredientsReplace,
    RecipeResponse,
    RecipeUpdate,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=APIResponse)
async def list_recipes(skip: int = 0, limit: int = 50) -> APIResponse:
    """Zwraca listę przepisów z obsługą paginacji.

    Endpoint zwraca jedynie podstawowe dane przepisu (bez szczegółowej listy składników),
    a stronowanie jest realizowane na poziomie zapytania do bazy.

    Args:
        skip: Liczba rekordów, które należy pominąć na początku (offset).
        limit: Maksymalna liczba przepisów do zwrócenia (page size).

    Returns:
        APIResponse: Odpowiedź z listą przepisów w polu `data`.
            Struktura `data` jest zgodna z modelem `RecipeResponse`.

    Raises:
        HTTPException: Gdy parametry `skip`/`limit` są niepoprawne (np. poza zakresem).
        HTTPException: Gdy wystąpi błąd bazy danych (np. problemy z połączeniem).
    """
    try:
        recipes_result = crud.list_recipes(skip=skip, limit=limit)
        recipes = recipes_result[0] if isinstance(recipes_result, tuple) else recipes_result
        models = [RecipeResponse.model_validate(item) for item in recipes]
        return APIResponse(
            success=True,
            data=[item.model_dump() for item in models],
            message="Pobrano listę przepisów.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.put("/{recipe_id}/ingredients", response_model=APIResponse)
async def replace_recipe_ingredients(recipe_id: int, payload: RecipeIngredientsReplace) -> APIResponse:
    """Całkowicie zastępuje listę składników przypisanych do przepisu.

    Endpoint jest przeznaczony dla panelu admina. Oczekuje pełnej listy składników
    jako pary `(ingredient_id, measure)` i usuwa wcześniej przypisane składniki przepisu,
    po czym wstawia nowe rekordy relacji.

    Wymagania:
    - `ingredient_id` musi wskazywać istniejący składnik z tabeli `ingredients`.
    - Duplikaty `ingredient_id` w payloadzie są traktowane jako błąd.

    Args:
        recipe_id: Identyfikator przepisu, dla którego ma zostać zaktualizowana lista składników.
        payload: Lista składników w formacie `RecipeIngredientsReplace`.

    Returns:
        APIResponse: Odpowiedź zawierająca zaktualizowany przepis w polu `data`.

    Raises:
        HTTPException: 400 dla niepoprawnych danych wejściowych (walidacja Pythona/Pydantic).
        HTTPException: 404 gdy przepis o podanym `recipe_id` nie istnieje.
        HTTPException: 500 dla błędów nieoczekiwanych (np. ogólne błędy bazy).
    """
    try:
        lines = [(item.ingredient_id, item.measure) for item in payload.ingredients]
        recipe = crud.replace_recipe_ingredients(recipe_id, lines)
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono przepisu.",
            )
        model = RecipeResponse.model_validate(recipe)
        return APIResponse(success=True, data=model.model_dump(), message="Zaktualizowano składniki przepisu.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowe ID składnika lub dane powiązania.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.get("/{recipe_id}", response_model=APIResponse)
async def get_recipe(recipe_id: int) -> APIResponse:
    """Zwraca pojedynczy przepis wraz ze szczegółami składników.

    Endpoint zwraca dane przepisów wraz z listą składników (`ingredients`),
    co pozwala na odtworzenie widoku szczegółów po stronie frontendowej.

    Args:
        recipe_id: Identyfikator przepisu do pobrania.

    Returns:
        APIResponse: Odpowiedź z przepisem w polu `data`, zgodna z modelem `RecipeResponse`.

    Raises:
        HTTPException: 400 gdy `recipe_id` jest niepoprawne (np. <= 0).
        HTTPException: 404 gdy przepis nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        recipe = crud.get_recipe_by_id(recipe_id)
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono przepisu.",
            )
        model = RecipeResponse.model_validate(recipe)
        return APIResponse(success=True, data=model.model_dump(), message="Pobrano przepis.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def create_recipe(payload: RecipeCreate) -> APIResponse:
    """Tworzy nowy przepis.

    Args:
        payload: Dane nowego przepisu (bez relacji składników; relacje dodawane są osobnym endpointem admina).

    Returns:
        APIResponse: Odpowiedź z utworzonym przepisem w polu `data`.

    Raises:
        HTTPException: 400 przy błędnej walidacji danych wejściowych.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        recipe = crud.create_recipe(
            title=payload.title,
            instructions=payload.instructions,
            image_url=payload.image_url,
            youtube_url=payload.youtube_url,
            category_id=payload.category_id,
            area_id=payload.area_id,
        )
        model = RecipeResponse.model_validate(recipe)
        return APIResponse(success=True, data=model.model_dump(), message="Utworzono przepis.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niepoprawne dane relacji lub konflikt unikalności.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.put("/{recipe_id}", response_model=APIResponse)
async def update_recipe(recipe_id: int, payload: RecipeUpdate) -> APIResponse:
    """Aktualizuje wybrane pola przepisu po `recipe_id`.

    Endpoint pozwala na częściową aktualizację (PATCH-like zachowanie) dzięki temu,
    że pola w `RecipeUpdate` są opcjonalne.

    Args:
        recipe_id: Identyfikator przepisu.
        payload: Pól przepisu do aktualizacji.

    Returns:
        APIResponse: Odpowiedź ze zaktualizowanym przepisem w polu `data`.

    Raises:
        HTTPException: 400 przy niepoprawnych danych wejściowych.
        HTTPException: 404 gdy przepis nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        recipe = crud.update_recipe(
            recipe_id=recipe_id,
            title=payload.title,
            instructions=payload.instructions,
            image_url=payload.image_url,
            youtube_url=payload.youtube_url,
            category_id=payload.category_id,
            area_id=payload.area_id,
        )
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono przepisu.",
            )
        model = RecipeResponse.model_validate(recipe)
        return APIResponse(success=True, data=model.model_dump(), message="Zaktualizowano przepis.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niepoprawne dane relacji lub konflikt unikalności.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.delete("/{recipe_id}", response_model=APIResponse)
async def delete_recipe(recipe_id: int) -> APIResponse:
    """Usuwa przepis po identyfikatorze.

    Args:
        recipe_id: Identyfikator przepisu.

    Returns:
        APIResponse: Odpowiedź potwierdzająca usunięcie rekordu w polu `data`.

    Raises:
        HTTPException: 400 przy niepoprawnym `recipe_id`.
        HTTPException: 404 gdy przepis nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        deleted = crud.delete_recipe(recipe_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono przepisu.",
            )
        return APIResponse(success=True, data={"deleted": True}, message="Usunięto przepis.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc
