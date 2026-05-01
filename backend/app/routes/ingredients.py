import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import APIResponse, IngredientCreate, IngredientResponse, IngredientUpdate

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/", response_model=APIResponse)
async def list_ingredients(skip: int = 0, limit: int = 100):
    """Zwraca listę składników z paginacją.

    Endpoint pobiera składniki posortowane alfabetycznie po nazwie
    z możliwością ustawienia przesunięcia i limitu wyników.

    Args:
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów do zwrócenia.

    Returns:
        APIResponse: Odpowiedź zawierająca listę składników.

    Raises:
        HTTPException: 400 przy niepoprawnych parametrach paginacji.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        ingredients_result = crud.list_ingredients(skip, limit)
        ingredients = ingredients_result[0] if isinstance(ingredients_result, tuple) else ingredients_result
        ingredient_models = [IngredientResponse.model_validate(item) for item in ingredients]
        return APIResponse(
            success=True,
            data=[item.model_dump() for item in ingredient_models],
            message="Pobrano listę składników.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.get("/suggestions", response_model=APIResponse)
async def get_suggestions(query:str, limit:int = 15) -> APIResponse:
    """Zwraca sugestie składników na podstawie zapytania.

    Endpoint zwraca listę składników, których nazwa zawiera podany ciąg znaków.
    Wyniki są posortowane alfabetycznie i ograniczone do określonej liczby.

    Args:
        query: Ciąg znaków do wyszukania w nazwach składników.
        limit: Maksymalna liczba sugestii do zwrócenia.
    Returns:
        APIResponse: Odpowiedź zawierająca listę sugestii.

    Raises:
        HTTPException: 400 przy niepoprawnych parametrach.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:

        suggestions = crud.suggest_ingredients(query, limit)

        suggestion_models = [IngredientResponse.model_validate(item) for item in suggestions]

        message = "Pobrano listę składników." if suggestions else "Nie znaleziono składników."
        return APIResponse(
            success=True,
            data=[item.model_dump() for item in suggestion_models],
            message=message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.get("/{ingredient_id}", response_model=APIResponse)
async def get_ingredient(ingredient_id: int):
    """Zwraca szczegóły składnika po ID.

    Args:
        ingredient_id: Identyfikator składnika.

    Returns:
        APIResponse: Odpowiedź z danymi pojedynczego składnika.

    Raises:
        HTTPException: 400 przy niepoprawnym `ingredient_id`.
        HTTPException: 404 gdy składnik nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        ingredient = crud.get_ingredient_by_id(ingredient_id)
        if ingredient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono składnika.",
            )
        ingredient_model = IngredientResponse.model_validate(ingredient)
        return APIResponse(
            success=True,
            data=ingredient_model.model_dump(),
            message="Pobrano składnik.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def create_ingredient(payload: IngredientCreate):
    """Tworzy nowy składnik.

    Args:
        payload: Dane nowego składnika (nazwa oraz URL obrazka).

    Returns:
        APIResponse: Odpowiedź z utworzonym składnikiem.

    Raises:
        HTTPException: 400 przy błędnych danych lub konflikcie unikalności.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        ingredient = crud.create_ingredient(name=payload.name, image_url=payload.image_url)
        ingredient_model = IngredientResponse.model_validate(ingredient)
        return APIResponse(
            success=True,
            data=ingredient_model.model_dump(),
            message="Utworzono składnik.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Składnik o takiej nazwie lub image_url już istnieje.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.put("/{ingredient_id}", response_model=APIResponse)
async def update_ingredient(ingredient_id: int, payload: IngredientUpdate):
    """Aktualizuje składnik po ID.

    Args:
        ingredient_id: Identyfikator składnika.
        payload: Pola składnika do aktualizacji.

    Returns:
        APIResponse: Odpowiedź ze zaktualizowanym składnikiem.

    Raises:
        HTTPException: 400 przy niepoprawnych danych wejściowych.
        HTTPException: 404 gdy składnik nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        ingredient = crud.update_ingredient(
            ingredient_id=ingredient_id,
            name=payload.name,
            image_url=payload.image_url,
        )
        if ingredient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono składnika.",
            )
        ingredient_model = IngredientResponse.model_validate(ingredient)
        return APIResponse(
            success=True,
            data=ingredient_model.model_dump(),
            message="Zaktualizowano składnik.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.delete("/{ingredient_id}", response_model=APIResponse)
async def delete_ingredient(ingredient_id: int):
    """Usuwa składnik po ID.

    Args:
        ingredient_id: Identyfikator składnika.

    Returns:
        APIResponse: Odpowiedź potwierdzająca usunięcie rekordu.

    Raises:
        HTTPException: 400 przy niepoprawnym `ingredient_id`.
        HTTPException: 404 gdy składnik nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        deleted = crud.delete_ingredient(ingredient_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono składnika.",
            )
        return APIResponse(
            success=True,
            data={"deleted": True},
            message="Usunięto składnik.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


