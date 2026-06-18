# AGENTS.md - Astro Web

## Project Overview
Astro Web is a FastAPI-based web application for exploring astronomical databases created with the AstroDB Toolkit. It features interactive Bokeh visualizations (scatter plots, spectra), source browsing with DataTables, and both text and cone search capabilities.

## Directory Structure
- `astro_web/`: Main application package.
    - `main.py`: FastAPI entry point.
    - `config.py`: Configuration and environment variables.
    - `database/`: Database interaction (astrodbkit, SQLite).
    - `routes/`: Web page route definitions (web.py).
    - `visualizations/`: Bokeh plot generation (scatter, spectra).
    - `templates/`: Jinja2 HTML templates.
    - `static/`: CSS and schema definitions.
- `CONFIG.md`: Configuration settings guide.
- `pyproject.toml`: Project metadata and dependencies (managed by uv).
- `.env.example`: Template for environment variables.
- `constitution.md`: Project constitution and development guidelines.

## Guidance
Prior to making any code changes, read the `constitution.md` file to understand the project's development guidelines and coding standards.
