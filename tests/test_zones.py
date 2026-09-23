from fastapi.testclient import TestClient


def test_get_city_zones_success(client: TestClient, seed_data):
    response = client.get("/zones/1?season=summer")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert isinstance(data["features"], list)
    assert len(data["features"]) >= 1

    zone = data["features"][0]
    assert zone["type"] == "Feature"
    assert "properties" in zone
    assert "name" in zone["properties"]
    assert "code" in zone["properties"]
    assert "avg_lst" in zone["properties"]
    assert "priority_level" in zone["properties"]
    assert "total_budget_inr" in zone["properties"]


def test_get_zone_summary(client: TestClient, seed_data):
    response = client.get("/zones/summary/1?season=summer")
    assert response.status_code == 200
    data = response.json()
    assert data["zone_id"] == 1
    assert "Central Zone" in data["name"]
    assert "priority_level" in data
    assert "built_up_sqm" in data
    assert "open_soil_sqm" in data
    assert "top_interventions" in data
    assert isinstance(data["top_interventions"], list)


def test_get_zones_invalid_city(client: TestClient, seed_data):
    response = client.get("/zones/99999")
    assert response.status_code == 404
