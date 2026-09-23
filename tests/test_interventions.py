from fastapi.testclient import TestClient


def test_get_interventions(client: TestClient, seed_data):
    response = client.get("/interventions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    names = [item["name"] for item in data]
    assert "tree_planting" in names
    assert "cool_roofing" in names

    tree_planting = next(item for item in data if item["name"] == "tree_planting")
    assert tree_planting["intervention_id"] == 1
    assert tree_planting["unit"] == "per tree"
    assert tree_planting["cost_per_unit"] == 300.0
    assert tree_planting["cooling_coefficient"] == 0.071
    assert tree_planting["data_confidence"] == "strong"
    assert tree_planting["notes"] == "Native shade trees recommended"
    assert tree_planting["coverage_ratio"] == 0.8
    assert tree_planting["max_cooling_ceiling"] == 4.5
