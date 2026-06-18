from fastapi.testclient import TestClient
from astro_web.main import app

client = TestClient(app)

def test_render_homepage():
    """GET / returns 200 and navigation."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Home" in response.text
    assert "Browse Database" in response.text

def test_render_browse():
    """GET /browse renders source table."""
    response = client.get("/browse")
    assert response.status_code == 200
    assert "Source" in response.text
    assert "2MASS J03552014+1439297" in response.text

def test_render_search_form():
    """GET /search renders search inputs."""
    response = client.get("/search")
    assert response.status_code == 200
    assert "Search" in response.text
    assert "Coordinates" in response.text

def test_render_inventory_page():
    """GET /source/{source_name} renders for existing source."""
    source_name = "2MASS J03552014+1439297"
    response = client.get(f"/source/{source_name}")
    assert response.status_code == 200
    assert source_name in response.text
    assert "Inventory" in response.text

def test_render_inventory_404():
    """GET /source/{invalid_source} returns 404 template."""
    response = client.get("/source/NonExistentSource")
    assert response.status_code == 404
    assert "Source not found" in response.text

def test_render_spectra_page():
    """GET /source/{source_name}/spectra renders Bokeh plot components."""
    source_name = "2MASS J03552014+1439297"
    response = client.get(f"/source/{source_name}/spectra")
    assert response.status_code == 200
    assert "Spectra" in response.text
    assert "bokeh" in response.text.lower()

def test_render_plots_page():
    """GET /plots renders scatter plot components."""
    response = client.get("/plots")
    assert response.status_code == 200
    assert "Plots" in response.text
    assert "bokeh" in response.text.lower()
