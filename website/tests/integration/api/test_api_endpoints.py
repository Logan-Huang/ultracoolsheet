from fastapi.testclient import TestClient
from astro_web.main import app

client = TestClient(app)

def test_api_search_success():
    """POST /api/search returns 200 and expected JSON structure."""
    response = client.post("/api/search", data={"query": "2MASS J03552014+1439297"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_count" in data
    assert data["total_count"] > 0
    assert any(res["source"] == "2MASS J03552014+1439297" for res in data["results"])

def test_api_search_no_query():
    """POST /api/search with empty query returns 400."""
    response = client.post("/api/search", data={"query": "  "})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_api_cone_search_success():
    """POST /api/search/cone returns 200 and expected JSON."""
    response = client.post("/api/search/cone", data={
        "coordinates": "58.83375 14.658056",
        "radius": "0.1",
        "radius_unit": "degrees"
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["total_count"] > 0
    assert any(res["source"] == "2MASS J03552014+1439297" for res in data["results"])

def test_api_inventory_success():
    """POST /api/inventory returns 200 and source data."""
    # Note: main.py uses 'source' as form field name, but web.py uses 'source_name'
    # The endpoint in main.py is: @app.post("/api/inventory") async def inventory_api_endpoint(source: str = Form(...))
    response = client.post("/api/inventory", data={"source": "2MASS J03552014+1439297"})
    assert response.status_code == 200
    data = response.json()
    assert data["source_name"] == "2MASS J03552014+1439297"
    assert "inventory" in data
    assert "Sources" in data["inventory"]

def test_api_inventory_not_found():
    """POST /api/inventory for non-existent source returns 404."""
    response = client.post("/api/inventory", data={"source": "NonExistentSource"})
    assert response.status_code == 404
    assert "detail" in response.json()
