import uvicorn
from fastapi import FastAPI

from backend.app.routes.areas import router as areas_router
from backend.app.routes.categories import router as categories_router
from backend.app.routes.ingredients import router as ingredients_router
from backend.app.routes.recipes import router as recipes_router

app = FastAPI(title="EmpRidge MVP API", version="0.1.0")

app.include_router(recipes_router)
app.include_router(ingredients_router)
app.include_router(categories_router)
app.include_router(areas_router)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Prosty endpoint healthcheck."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
