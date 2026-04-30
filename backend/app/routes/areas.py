import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import APIResponse, AreaCreate, AreaResponse, AreaUpdate

router = APIRouter(prefix="/areas", tags=["areas"])


@router.get("/", response_model=APIResponse)
async def list_areas() -> APIResponse:
    """Zwraca listę wszystkich area/krajów pochodzenia.

    Returns:
        APIResponse: Odpowiedź zawierająca listę area.

    Raises:
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        areas = crud.list_areas()
        models = [AreaResponse.model_validate(item) for item in areas]
        return APIResponse(
            success=True,
            data=[item.model_dump() for item in models],
            message="Pobrano listę area.",
        )
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.get("/{area_id}", response_model=APIResponse)
async def get_area(area_id: int) -> APIResponse:
    """Zwraca pojedynczy area po ID.

    Args:
        area_id: Identyfikator area.

    Returns:
        APIResponse: Odpowiedź z danymi pojedynczego area.

    Raises:
        HTTPException: 400 przy niepoprawnym `area_id`.
        HTTPException: 404 gdy area nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        area = crud.get_area_by_id(area_id)
        if area is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono area.",
            )
        model = AreaResponse.model_validate(area)
        return APIResponse(success=True, data=model.model_dump(), message="Pobrano area.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def create_area(payload: AreaCreate) -> APIResponse:
    """Tworzy nowe area.

    Args:
        payload: Dane nowego area.

    Returns:
        APIResponse: Odpowiedź z utworzonym area.

    Raises:
        HTTPException: 400 przy błędnych danych lub konflikcie unikalności.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        area = crud.create_area(name=payload.name)
        model = AreaResponse.model_validate(area)
        return APIResponse(success=True, data=model.model_dump(), message="Utworzono area.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area o takiej nazwie już istnieje.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.put("/{area_id}", response_model=APIResponse)
async def update_area(area_id: int, payload: AreaUpdate) -> APIResponse:
    """Aktualizuje area po ID.

    Args:
        area_id: Identyfikator area.
        payload: Dane aktualizacji area.

    Returns:
        APIResponse: Odpowiedź ze zaktualizowanym area.

    Raises:
        HTTPException: 400 przy niepoprawnych danych wejściowych.
        HTTPException: 404 gdy area nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        area = crud.update_area(area_id=area_id, name=payload.name)
        if area is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono area.",
            )
        model = AreaResponse.model_validate(area)
        return APIResponse(success=True, data=model.model_dump(), message="Zaktualizowano area.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Area o takiej nazwie już istnieje.",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc


@router.delete("/{area_id}", response_model=APIResponse)
async def delete_area(area_id: int) -> APIResponse:
    """Usuwa area po ID.

    Args:
        area_id: Identyfikator area.

    Returns:
        APIResponse: Odpowiedź potwierdzająca usunięcie rekordu.

    Raises:
        HTTPException: 400 przy niepoprawnym `area_id`.
        HTTPException: 404 gdy area nie istnieje.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        deleted = crud.delete_area(area_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono area.",
            )
        return APIResponse(success=True, data={"deleted": True}, message="Usunięto area.")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Błąd bazy danych.",
        ) from exc
