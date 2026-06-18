"""
Main FastAPI application entry point for Hello World website.

This module initializes the FastAPI app with basic configuration.
"""

from urllib.parse import quote

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from astro_web.routes import web

app = FastAPI(
    title="Astro Web",
    description="Multi-page astronomy database web application with navigation bar",
    version="0.1.0",
)

# Configure Jinja2 templates
templates = Jinja2Templates(directory="astro_web/templates")
# Add urlencode filter for URL encoding source names
templates.env.filters["urlencode"] = lambda u: quote(str(u), safe="")
web.set_templates(templates)

# Configure static file serving
app.mount("/static", StaticFiles(directory="astro_web/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Homepage route rendering 'Hello World' content."""
    return await web.homepage(request)


@app.get("/browse", response_class=HTMLResponse)
async def browse(request: Request):
    """Browse database page rendering Sources table."""
    return await web.browse(request)


@app.get("/plots", response_class=HTMLResponse)
async def plot(request: Request):
    """Plots page rendering scatter visualization."""
    return await web.plot(request)


@app.get("/source/{source_name}", response_class=HTMLResponse)
async def inventory_page(request: Request, source_name: str):
    """Source inventory page rendering all data for a specific source."""
    return await web.inventory(request, source_name)


@app.get("/source/{source_name}/spectra", response_class=HTMLResponse)
async def spectra_page(request: Request, source_name: str):
    """Spectra visualization page for a specific source."""
    return await web.spectra_display(request, source_name)


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Search form page."""
    return await web.search_form(request)


@app.post("/search/results", response_class=HTMLResponse)
async def search_results_page(request: Request, query: str = Form(...)):
    """Search results page."""
    return await web.search_results(request, query)


@app.post("/api/search")
async def search_api_endpoint(query: str = Form(...)):
    """API endpoint for programmatic search access."""
    return await web.search_api(query)


@app.post("/search/cone-results", response_class=HTMLResponse)
async def cone_search_results_page(
    request: Request, coordinates: str = Form(...), radius: str = Form(...), radius_unit: str = Form(...)
):
    """Cone search results page."""
    return await web.cone_search_results(request, coordinates, radius, radius_unit)


@app.post("/api/search/cone")
async def cone_search_api_endpoint(coordinates: str = Form(...), radius: str = Form(...), radius_unit: str = Form(...)):
    """API endpoint for programmatic cone search access."""
    return await web.cone_search_api(coordinates, radius, radius_unit)


@app.post("/api/inventory")
async def inventory_api_endpoint(source: str = Form(...)):
    """API endpoint for programmatic inventory access."""
    return await web.inventory_api(source)


@app.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, path: str):
    """404 handler for non-existent pages."""
    return await web.not_found(request, path)


def serve():
    """Entry point for the 'serve' command."""
    # ruff: noqa: PLC0415
    import uvicorn

    uvicorn.run("astro_web.main:app", host="0.0.0.0", port=8000, reload=True)
