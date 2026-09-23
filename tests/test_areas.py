from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_areas_surat():
    response = client.get("/areas/1?season=summer")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 34
    
    first_area = data["features"][0]
    assert "geometry" in first_area
    assert first_area["geometry"]["type"] in ["Polygon", "MultiPolygon"]
    props = first_area["properties"]
    assert props["city_id"] == 1
    assert "building_rooftop_sqm" in props
    assert "road_paved_sqm" in props
    assert "open_ground_sqm" in props
    assert "avg_lst" in props
    assert "total_budget_inr" in props
    assert props["total_budget_inr"] > 0
    assert "is_hotspot" in props


def test_get_areas_ahmedabad():
    response = client.get("/areas/2?season=summer")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 21


def test_get_areas_invalid_city():
    response = client.get("/areas/9999")
    assert response.status_code == 404


def test_get_area_detail_feasibility():
    response = client.get("/areas/detail/1?season=summer")
    assert response.status_code == 200
    data = response.json()
    assert data["area_id"] == 1
    assert "City North" in data["name"]
    assert "land_distribution" in data
    land = data["land_distribution"]
    assert land["building_rooftop_sqm"] > 0
    assert land["road_paved_sqm"] > 0
    assert land["open_ground_sqm"] > 0

    # Categorized physical land feasibility interventions
    assert len(data["rooftop_interventions"]) > 0
    roof = data["rooftop_interventions"][0]
    assert roof["category"] == "rooftop"
    assert "High-SRI" in roof["targeted_measure"]
    assert "Feasibility Verified" in roof["feasibility_check"]
    assert roof["total_cost_inr"] > 0

    assert len(data["road_interventions"]) > 0
    road = data["road_interventions"][0]
    assert road["category"] == "road"
    assert "Feasibility Verified" in road["feasibility_check"]

    assert data["total_cooling_potential_c"] > 0
    assert data["total_budget_inr"] > 0
    assert "Phase 1" in data["implementation_timeline"]


def test_get_area_detail_invalid():
    response = client.get("/areas/detail/99999")
    assert response.status_code == 404

