import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import APIResponse, SearchRecipesRequest, SearchRecipeItem

router = APIRouter(tags=["search"])

@router.post("/search-recipes", response_model=APIResponse)
async def search_recipes(payload: SearchRecipesRequest) -> APIResponse:
    """Wyszukiwanie przepisów po składnikach.

    Args:
        payload: Dane wyszukiwania.

    Returns:
        APIResponse: Odpowiedź z listą znalezionych przepisów.

    Raises:
        HTTPException: 400 przy błędnych danych wejściowych.
        HTTPException: 500 przy błędzie bazy danych.
    """
    try:
        rows = crud.search_recipes(
            ingredient_ids=payload.ingredient_ids,
            category_id=payload.category_id,
            area_id=payload.area_id,
            min_matching_ratio=payload.min_matching_ratio,
            max_total_ingredients=payload.max_total_ingredients
        )
        items = [SearchRecipeItem.model_validate(row) for row in rows]
        message = "Znaleziono przepisy." if items else "Nie znaleziono przepisów."
        return APIResponse(success=True, data=items, message=message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Błąd bazy danych.") from exc
