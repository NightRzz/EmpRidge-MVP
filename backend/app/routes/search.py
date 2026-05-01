import sqlite3

from fastapi import APIRouter, HTTPException, status

from backend.app import crud
from backend.app.schemas import APIResponse, SearchRecipesRequest, SearchRecipeItem

router = APIRouter(tags=["search"])

@router.post("/search-recipes", response_model=APIResponse)
async def search_recipes(payload: SearchRecipesRequest) -> APIResponse:
    """Wyszukuje przepisy na podstawie listy składników.

    Endpoint dopasowuje przepisy do przekazanych `ingredient_ids` i zwraca wyniki sortowane
    według `matching_ratio` (oraz dodatkowych kryteriów z poziomu zapytania SQL).

    Args:
        payload: Model wejściowy zawierający filtry wyszukiwania:
            - `ingredient_ids`: lista składników, które mają wpływać na dopasowanie
            - `category_id`: opcjonalny filtr kategorii
            - `area_id`: opcjonalny filtr obszaru
            - `min_matching_ratio`: minimalna granica dopasowania (w %)
            - `max_total_ingredients`: opcjonalna granica liczby składników w przepisie

    Returns:
        APIResponse: Sukces lub błąd.
            Przy sukcesie `data` zawiera listę obiektów `SearchRecipeItem`.

    Raises:
        HTTPException: 400 w przypadku błędnej walidacji danych wejściowych.
        HTTPException: 500 przy nieoczekiwanych błędach bazy danych.
    """
    try:
        rows_result = crud.search_recipes(
            ingredient_ids=payload.ingredient_ids,
            category_id=payload.category_id,
            area_id=payload.area_id,
            min_matching_ratio=payload.min_matching_ratio,
            max_total_ingredients=payload.max_total_ingredients
        )
        rows = rows_result[0] if isinstance(rows_result, tuple) else rows_result
        items = [SearchRecipeItem.model_validate(row) for row in rows]
        message = "Znaleziono przepisy." if items else "Nie znaleziono przepisów."
        return APIResponse(success=True, data=items, message=message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Błąd bazy danych.") from exc
