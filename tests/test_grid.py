from fastapi.testclient import TestClient


def test_get_grid_cells_success(client: TestClient, seed_data):
    response = client.get("/grid/1")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert isinstance(data["features"], list)
    assert len(data["features"]) == 2

    feature = data["features"][0]
    assert feature["type"] == "Feature"
    assert "geometry" in feature
    assert feature["geometry"]["type"] == "Polygon"
    assert "properties" in feature
    assert "cell_id" in feature["properties"]
    assert feature["properties"]["cell_id"] in [101, 102]


def test_get_grid_cells_limit(client: TestClient, seed_data):
    response = client.get("/grid/1?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["features"]) == 1


def test_get_grid_cells_bbox_filter(client: TestClient, seed_data):
    response = client.get("/grid/1?bbox=72.7,21.1,72.9,21.3")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2


def test_get_grid_cells_invalid_bbox(client: TestClient, seed_data):
    response = client.get("/grid/1?bbox=invalid_bbox_string")
    assert response.status_code == 400
    assert "Invalid bbox parameter" in response.json()["detail"]


def test_get_grid_cells_nonexistent_city(client: TestClient, seed_data):
    response = client.get("/grid/99999")
    assert response.status_code == 404
    assert "City with id 99999 not found" in response.json()["detail"]
