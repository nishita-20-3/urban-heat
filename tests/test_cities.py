from fastapi.testclient import TestClient


def test_get_cities(client: TestClient, seed_data):
    response = client.get("/cities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    surat = next((c for c in data if c["name"] == "Surat"), None)
    assert surat is not None
    assert surat["city_id"] == 1
    assert surat["state"] == "Gujarat"
    assert surat["is_prototype"] is True
