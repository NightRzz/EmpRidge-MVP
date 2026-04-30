import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app import crud
from backend.app.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Tworzy klienta testowego z izolowaną bazą SQLite."""
    db_path = tmp_path / "test_search.db"
    schema_path = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()

    monkeypatch.setattr(crud, "DB_PATH", db_path)
    return TestClient(app)


def test_search_recipes_smoke(client: TestClient) -> None:
    """Smoke test endpointu /search-recipes: sortowanie + ratio + filtry."""
    # 1) Seed: kategorie i area
    cat_breakfast = client.post("/categories/", json={"name": "Breakfast"}).json()["data"]["id"]
    cat_dinner = client.post("/categories/", json={"name": "Dinner"}).json()["data"]["id"]
    area_pl = client.post("/areas/", json={"name": "Polish"}).json()["data"]["id"]

    # 2) Seed: składniki
    egg_id = client.post(
        "/ingredients/",
        json={"name": "egg", "image_url": "https://img/egg.png"},
    ).json()["data"]["id"]
    bread_id = client.post(
        "/ingredients/",
        json={"name": "bread", "image_url": "https://img/bread.png"},
    ).json()["data"]["id"]
    cheese_id = client.post(
        "/ingredients/",
        json={"name": "cheese", "image_url": "https://img/cheese.png"},
    ).json()["data"]["id"]

    # 3) Seed: przepisy
    # Założenie: masz endpoint tworzenia recipe_ingredients
    # Jeśli nie masz osobnego endpointu, wstaw dane relacji SQL-em bezpośrednio (poniżej wariant A/B)
    r1_id = client.post(
        "/recipes/",
        json={
            "title": "Egg Bread",
            "instructions": "Mix and fry",
            "image_url": "https://img/r1.png",
            "youtube_url": None,
            "category_id": cat_breakfast,
            "area_id": area_pl,
        },
    ).json()["data"]["id"]

    r2_id = client.post(
        "/recipes/",
        json={
            "title": "Cheese Toast",
            "instructions": "Toast and melt",
            "image_url": "https://img/r2.png",
            "youtube_url": None,
            "category_id": cat_dinner,
            "area_id": area_pl,
        },
    ).json()["data"]["id"]

    # --- Wariant A: masz endpoint relacji (podmień na właściwy) ---
    # client.post("/recipes/{r1_id}/ingredients", ...)
    # client.post("/recipes/{r2_id}/ingredients", ...)

    # --- Wariant B: brak endpointu relacji -> seed bezpośrednio SQL ---
    conn = sqlite3.connect(str(crud.DB_PATH))
    try:
        cur = conn.cursor()
        # r1: egg + bread (2/2 match dla [egg,bread])
        cur.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, measure) VALUES (?, ?, ?)",
            (r1_id, egg_id, "2 szt"),
        )
        cur.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, measure) VALUES (?, ?, ?)",
            (r1_id, bread_id, "2 kromki"),
        )

        # r2: egg + cheese (1/2 match dla [egg,bread])
        cur.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, measure) VALUES (?, ?, ?)",
            (r2_id, egg_id, "1 szt"),
        )
        cur.execute(
            "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, measure) VALUES (?, ?, ?)",
            (r2_id, cheese_id, "50 g"),
        )
        conn.commit()
    finally:
        conn.close()

    # 4) Search bez filtrów
    resp = client.post(
        "/search-recipes",
        json={
            "ingredient_ids": [egg_id, bread_id],
            "min_matching_ratio": 0.0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 2

    # Każdy wynik ma pola z issue #14
    for item in data:
        assert "matched_count" in item
        assert "total_count" in item
        assert "matching_ratio" in item

    # Sortowanie DESC po matching_ratio
    assert data[0]["matching_ratio"] >= data[1]["matching_ratio"]

    # r1 powinien mieć lepszy wynik niż r2
    top_ids = [x["id"] for x in data[:2]]
    assert r1_id in top_ids
    assert data[0]["id"] == r1_id
    assert data[0]["matched_count"] == 2
    assert data[0]["total_count"] == 2
    assert data[0]["matching_ratio"] == 100.0

    # 5) Filtr min_matching_ratio
    filtered = client.post(
        "/search-recipes",
        json={
            "ingredient_ids": [egg_id, bread_id],
            "min_matching_ratio": 75,
        },
    )
    assert filtered.status_code == 200
    fdata = filtered.json()["data"]
    assert all(item["matching_ratio"] >= 75 for item in fdata)
    assert any(item["id"] == r1_id for item in fdata)
    assert all(item["id"] != r2_id for item in fdata)

    # 6) Filtr category_id
    by_category = client.post(
        "/search-recipes",
        json={
            "ingredient_ids": [egg_id, bread_id],
            "category_id": cat_breakfast,
        },
    )
    assert by_category.status_code == 200
    cdata = by_category.json()["data"]
    assert all(item["category_id"] == cat_breakfast for item in cdata)