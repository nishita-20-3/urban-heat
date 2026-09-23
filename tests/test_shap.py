from fastapi.testclient import TestClient


def test_get_shap_with_season_param(client: TestClient, seed_data):
    response = client.get("/shap/101?season=summer")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["cell_id"] == 101
    assert data["season"] == "summer"
    assert data["predicted_lst"] == 45.8
    assert data["shap_base_value"] == 37.35
    assert "shap_contributions" in data

    contributions = data["shap_contributions"]
    assert contributions["ndvi"] == 0.496
    assert contributions["ndbi"] == 3.071
    assert contributions["air_temp"] == 5.144
    assert contributions["humidity"] == -0.091
    assert contributions["wind_speed"] == -1.093
    assert contributions["Built-up_pct"] == -0.041
    assert contributions["Tree cover_pct"] == 0.422


def test_get_shap_without_season_param_returns_all_seasons(client: TestClient, seed_data):
    response = client.get("/shap/101")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    summer_item = next((item for item in data if item["season"] == "summer"), None)
    assert summer_item is not None
    assert summer_item["cell_id"] == 101
    assert summer_item["shap_base_value"] == 37.35

    monsoon_item = next((item for item in data if item["season"] == "monsoon"), None)
    assert monsoon_item is not None
    assert monsoon_item["cell_id"] == 101
    # monsoon base_value computed: 33.2 - (-0.2 + 1.1 + 2.3) = 33.2 - 3.2 = 30.0
    assert round(monsoon_item["shap_base_value"], 1) == 30.0


def test_get_shap_season_not_found(client: TestClient, seed_data):
    response = client.get("/shap/101?season=winter")
    assert response.status_code == 404
    assert "No heat prediction found for cell 101 for season 'winter'" in response.json()["detail"]


def test_get_shap_non_hot_cell_empty_list(client: TestClient, seed_data):
    response = client.get("/shap/102")
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_shap_invalid_cell_404(client: TestClient, seed_data):
    response = client.get("/shap/99999")
    assert response.status_code == 404
    assert "Grid cell with ID 99999 not found" in response.json()["detail"]
