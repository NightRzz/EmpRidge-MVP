import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import APIResponse, RecipeCreate, RecipeResponse, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=APIResponse)
async def list_recipes(skip: int = 0, limit: int = 50) -> APIResponse:
    """Zwraca listę przepisów z paginacją.

    Args:
        skip: Liczba rekordów do pominięcia.
        limit: Maksymalna liczba rekordów do zwrócenia.

    Returns:
        APIResponse: Odpowiedź zawierająca listę przepisów.

    Raises:
        HTTPException: 400 przy niepoprawnych parametrach paginacji.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        recipes = crud.list_recipes(skip=skip, limit=limit)
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


@router.get("/{recipe_id}", response_model=APIResponse)
async def get_recipe(recipe_id: int) -> APIResponse:
    """Zwraca pojedynczy przepis po ID.

    Args:
        recipe_id: Identyfikator przepisu.

    Returns:
        APIResponse: Odpowiedź z danymi pojedynczego przepisu.

    Raises:
        HTTPException: 400 przy niepoprawnym `recipe_id`.
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
        payload: Dane nowego przepisu.

    Returns:
        APIResponse: Odpowiedź z utworzonym przepisem.

    Raises:
        HTTPException: 400 przy błędnych danych wejściowych.
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
    """Aktualizuje przepis po ID.

    Args:
        recipe_id: Identyfikator przepisu.
        payload: Pola przepisu do aktualizacji.

    Returns:
        APIResponse: Odpowiedź ze zaktualizowanym przepisem.

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
    """Usuwa przepis po ID.

    Args:
        recipe_id: Identyfikator przepisu.

    Returns:
        APIResponse: Odpowiedź potwierdzająca usunięcie rekordu.

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
