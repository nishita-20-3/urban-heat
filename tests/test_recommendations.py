from fastapi.testclient import TestClient


def test_get_recommendations_existing_data(client: TestClient, seed_data):
    response = client.get("/recommendations/101")
    assert response.status_code == 200
    data = response.json()
    assert data["cell_id"] == 101
    assert "scenarios" in data

    scenarios = data["scenarios"]
    assert "max_cooling" in scenarios
    assert "balanced" in scenarios

    max_cooling = scenarios["max_cooling"]
    # Total cooling: 3.0 + 5.9 = 8.9
    assert max_cooling["total_cooling_c"] == 8.9
    # Total cost: 12600 + 4520000 = 4532600
    assert max_cooling["total_cost_inr"] == 4532600.0
    assert len(max_cooling["interventions"]) == 2

    # Check intervention item details
    tree_interv = next(i for i in max_cooling["interventions"] if i["name"] == "tree_planting")
    assert tree_interv["quantity"] == 42.0
    assert tree_interv["unit"] == "per tree"
    assert tree_interv["cooling_contribution_c"] == 3.0
    assert tree_interv["cost_inr"] == 12600.0


def test_get_recommendations_no_recommendations_cell_returns_empty_scenarios_200(
    client: TestClient, seed_data
):
    """
    If a cell has no recommendations or recommendations table is not populated yet,
    it must return 200 OK with empty scenarios dictionary.
    """
    response = client.get("/recommendations/102")
    assert response.status_code == 200
    data = response.json()
    assert data["cell_id"] == 102
    assert data["scenarios"] == {}


def test_get_recommendations_invalid_cell_returns_404(client: TestClient, seed_data):
    """
    If cell does not exist in grid_cells, return 404 with clear error.
    """
    response = client.get("/recommendations/99999")
    assert response.status_code == 404
    assert "Grid cell with ID 99999 not found" in response.json()["detail"]
