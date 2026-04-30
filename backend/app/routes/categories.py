import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import APIResponse, CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=APIResponse)
async def list_categories() -> APIResponse:
    """Zwraca listę wszystkich kategorii.

    Returns:
        APIResponse: Odpowiedź zawierająca listę kategorii.

    Raises:
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        categories = crud.list_categories()
        models = [CategoryResponse.model_validate(item) for item in categories]
        return APIResponse(
            success=True,
            data=[item.model_dump() for item in models],
            message="Pobrano listę kategorii.",
        )
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.get("/{category_id}", response_model=APIResponse)
async def get_category(category_id: int) -> APIResponse:
    """Zwraca pojedynczą kategorię po ID.

    Args:
        category_id: Identyfikator kategorii.

    Returns:
        APIResponse: Odpowiedź z danymi pojedynczej kategorii.

    Raises:
        HTTPException: 400 przy niepoprawnym `category_id`.
        HTTPException: 404 gdy kategoria nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        category = crud.get_category_by_id(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono kategorii.",
            )
        model = CategoryResponse.model_validate(category)
        return APIResponse(success=True, data=model.model_dump(), message="Pobrano kategorię.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def create_category(payload: CategoryCreate) -> APIResponse:
    """Tworzy nową kategorię.

    Args:
        payload: Dane nowej kategorii.

    Returns:
        APIResponse: Odpowiedź z utworzoną kategorią.

    Raises:
        HTTPException: 400 przy błędnych danych lub konflikcie unikalności.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        category = crud.create_category(name=payload.name)
        model = CategoryResponse.model_validate(category)
        return APIResponse(success=True, data=model.model_dump(), message="Utworzono kategorię.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kategoria o takiej nazwie już istnieje.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.put("/{category_id}", response_model=APIResponse)
async def update_category(category_id: int, payload: CategoryUpdate) -> APIResponse:
    """Aktualizuje kategorię po ID.

    Args:
        category_id: Identyfikator kategorii.
        payload: Dane aktualizacji kategorii.

    Returns:
        APIResponse: Odpowiedź ze zaktualizowaną kategorią.

    Raises:
        HTTPException: 400 przy niepoprawnych danych wejściowych.
        HTTPException: 404 gdy kategoria nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        category = crud.update_category(category_id=category_id, name=payload.name)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono kategorii.",
            )
        model = CategoryResponse.model_validate(category)
        return APIResponse(
            success=True,
            data=model.model_dump(),
            message="Zaktualizowano kategorię.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kategoria o takiej nazwie już istnieje.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.delete("/{category_id}", response_model=APIResponse)
async def delete_category(category_id: int) -> APIResponse:
    """Usuwa kategorię po ID.

    Args:
        category_id: Identyfikator kategorii.

    Returns:
        APIResponse: Odpowiedź potwierdzająca usunięcie rekordu.

    Raises:
        HTTPException: 400 przy niepoprawnym `category_id`.
        HTTPException: 404 gdy kategoria nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        deleted = crud.delete_category(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono kategorii.",
            )
        return APIResponse(success=True, data={"deleted": True}, message="Usunięto kategorię.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc
