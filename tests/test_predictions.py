from fastapi.testclient import TestClient


def test_get_predictions_hot_cell(client: TestClient, seed_data):
    response = client.get("/predict/101")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    seasons = [p["season"] for p in data]
    assert "summer" in seasons
    assert "monsoon" in seasons

    summer_pred = next(p for p in data if p["season"] == "summer")
    assert summer_pred["predicted_lst"] == 45.8
    assert summer_pred["actual_lst"] == 46.2
    assert summer_pred["prediction_date"] == "2026-08-18"

    monsoon_pred = next(p for p in data if p["season"] == "monsoon")
    assert monsoon_pred["predicted_lst"] == 33.2
    assert monsoon_pred["actual_lst"] is None


def test_get_predictions_bulk(client: TestClient, seed_data):
    response = client.get("/predict/bulk?cell_ids=101,102")
    assert response.status_code == 200
    data = response.json()
    assert "101" in data
    assert "102" in data
    assert len(data["101"]) == 2
    assert len(data["102"]) == 0

    # Test POST
    post_res = client.post("/predict/bulk", json={"cell_ids": [101, 102], "season": "summer"})
    assert post_res.status_code == 200
    post_data = post_res.json()
    assert len(post_data["101"]) == 1
    assert post_data["101"][0]["season"] == "summer"


def test_get_predictions_non_hot_cell_returns_empty_list_200(client: TestClient, seed_data):
    """
    If a cell exists in grid_cells but has no prediction rows (not in top 25th percentile hot cells),
    it MUST return an empty list [] with status 200, NOT a 404.
    """
    response = client.get("/predict/102")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []


def test_get_predictions_invalid_cell_returns_404(client: TestClient, seed_data):
    """
    If a cell does not exist in grid_cells, return 404 with a clear error message.
    """
    response = client.get("/predict/99999")
    assert response.status_code == 404
    assert "Grid cell with ID 99999 not found" in response.json()["detail"]
