from pydantic import BaseModel, ConfigDict
from typing import Optional


class RecipeBase(BaseModel):
    """Wspólne pola dla Recipe."""
    title: str
    instructions: Optional[str] = None
    image_url: Optional[str] = None
    youtube_url: Optional[str] = None
    category_id: Optional[int] = None
    area_id: Optional[int] = None


class RecipeCreate(RecipeBase):
    """Schemat do tworzenia przepisu."""
    pass


class RecipeUpdate(RecipeBase):
    """Schemat do aktualizacji przepisu."""
    title: Optional[str] = None


class RecipeResponse(RecipeBase):
    """Schemat odpowiedzi — to dostaje frontend."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============ INGREDIENT ============

class IngredientBase(BaseModel):
    """Wspólne pola dla Ingredient."""
    name: str
    image_url: Optional[str] = None


class IngredientCreate(IngredientBase):
    """Schemat do tworzenia składnika."""
    image_url: str


class IngredientUpdate(BaseModel):
    """Schemat do aktualizacji składnika."""

    name: str | None = None
    image_url: str | None = None


class IngredientResponse(IngredientBase):
    """Schemat odpowiedzi."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============ CATEGORY ============

class CategoryBase(BaseModel):
    """Wspólne pola dla Category."""
    name: str


class CategoryCreate(CategoryBase):
    """Schemat do tworzenia kategorii."""
    pass


class CategoryUpdate(BaseModel):
    """Schemat do aktualizacji kategorii."""

    name: str | None = None


class CategoryResponse(CategoryBase):
    """Schemat odpowiedzi."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============ AREA ============

class AreaBase(BaseModel):
    """Wspólne pola dla Area."""
    name: str


class AreaCreate(AreaBase):
    """Schemat do tworzenia area."""
    pass


class AreaUpdate(BaseModel):
    """Schemat do aktualizacji area."""

    name: str | None = None


class AreaResponse(AreaBase):
    """Schemat odpowiedzi."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ============ API RESPONSE WRAPPER ============

class APIResponse(BaseModel):
    """Wrapper dla spójnych odpowiedzi API."""
    success: bool
    data: Optional[dict | list] = None
    error: Optional[str] = None
    message: Optional[str] = None