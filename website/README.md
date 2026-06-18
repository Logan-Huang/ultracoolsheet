# Astro Web

A dynamic web application for exploring astronomical databases, built with FastAPI, Jinja2, and Bokeh.   
This uses the AstroDB Toolkit to explore databases created with it.

## Quickstart

### Prerequisites

- Python 3.13+
- `uv` package manager (or pip)

### Installation

```bash
# Install dependencies
uv sync
```

### Running the Application

Grab a copy of the database at https://github.com/SIMPLE-AstroDB/SIMPLE-binary and place it in the main directory.   
Update configuration settings (CONFIG.md) if needed.

```bash
# Start the development server
uv run serve

# Or run it manually with
uvicorn astro_web.main:app --reload --port 8000
```

Then open your browser to http://localhost:8000

## Project Structure

```
src/
├── main.py                  # FastAPI application entry point
├── config.py               # Configuration settings and environment variables
├── database/                # Database interaction modules
│   ├── sources.py          # Source data database operations
│   └── query.py            # Search and query helper functions
├── routes/                   # API route definitions
│   └── web.py               # Web page routes (homepage, browse, inventory, plot, search, spectra, 404)
├── templates/               # Jinja2 HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Homepage template
│   ├── browse.html         # Browse sources page
│   ├── inventory.html      # Source inventory page
│   ├── plot.html           # Interactive plot page
│   ├── search.html         # Search form page
│   ├── search_results.html # Search results page
│   ├── spectra.html        # Spectra visualization page
│   └── 404.html            # Error page template
├── static/                  # CSS files and static assets
│   ├── style.css           # Clean minimal theme CSS
│   └── schema.yaml         # Schema definitions
└── visualizations/          # Bokeh plot generation functions
    ├── scatter.py          # Scatter plot from source data
    └── spectra.py          # Spectra visualization plots
```

## Features

- **Navigation Bar**: Persistent navigation across all pages
- **Browse Sources**: Explore astronomical sources with DataTables-powered search, filtering, and pagination
- **Source Inventory**: View detailed inventory of astronomical data sources
- **Search Functionality**: Text-based search and cone search for astronomical objects
- **Interactive Visualizations**: Bokeh scatter plots and spectra plots with hover tooltips
- **Spectra Display**: Multi-spectrum visualization with formatted legends and metadata
- **Database Integration**: SQLite database for source data management with astrodbkit
- **API Endpoints**: RESTful API for programmatic access to search functionality
- **Clean Minimal Design**: Astronomy-inspired color palette with light background
- **Fast Development**: Hot-reload enabled for rapid development

## Technology Stack

- **FastAPI** ≥0.120.0 - Web framework
- **Jinja2** - Template engine
- **Bokeh** =3.8.0 - Interactive visualizations
- **astrodbkit** ≥2.4 - Astronomical database operations
- **astropy** - Astronomical coordinate and unit handling
- **DataTables** =1.13.7 - Interactive data tables with jQuery
- **uvicorn** - ASGI server

## API Endpoints

The application provides both web pages and API endpoints:

### Web Pages
- `/` - Homepage
- `/browse` - Browse astronomical sources
- `/search` - Search form
- `/plots` - Interactive visualizations
- `/source/{source_name}` - Source inventory page
- `/source/{source_name}/spectra` - Spectra visualization

### API Endpoints
- `POST /api/search` - Text-based object search
- `POST /api/search/cone` - Cone search by coordinates and radius
- `POST /api/inventory` - Get inventory data for a specific source

#### Example: Text-based Search

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=2MASS J05395200-0059019"
```

#### Example: Cone Search

```bash
curl -X POST "http://localhost:8000/api/search/cone" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "coordinates=85.0 -1.0" \
  -d "radius=1.0" \
  -d "radius_unit=degrees"
```

#### Example: Inventory Lookup

```bash
curl -X POST "http://localhost:8000/api/inventory" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "source=2MASS J05395200-0059019"
```

All endpoints return JSON responses with search results, execution time, and metadata.

## Development

The application runs in development mode with auto-reload enabled:

```bash
uvicorn src.main:app --reload --port 8000
```

Changes to templates, routes, or visualizations will automatically reload.

## License

Copyright © 2025 David Rodriguez
