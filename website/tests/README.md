# Astro-Web Tests

This directory contains the test suite for the Astro-Web application. The tests are designed to ensure the reliability of astronomical database queries, API endpoints, and web page rendering.

## Test Organization

The tests are split into two main categories:

- **`unit/`**: Isolated tests for utility functions and visualization logic that do not require a database connection.
  - `database/`: Tests for coordinate parsing and unit conversions.
  - `visualizations/`: Tests for Bokeh plot generation logic.
- **`integration/`**: Tests that verify the interaction between different components, including the database and the web framework.
  - `api/`: Verifies RESTful API endpoints and JSON responses.
  - `database/`: Verifies data retrieval using `astrodbkit` from the SQLite database.
  - `web/`: Verifies that Jinja2 templates render correctly with live data.

## Requirements

### Database
Integration tests require a copy of the **SIMPLE** database in the project root.
- **File name**: `SIMPLE.sqlite`
- **Download**: You can download the latest version from [SIMPLE-AstroDB/SIMPLE-binary](https://github.com/SIMPLE-AstroDB/SIMPLE-binary/raw/main/SIMPLE.sqlite).

The tests expect this file to be present at the path specified by `ASTRO_WEB_DATABASE_URL` (defaults to `sqlite:///SIMPLE.sqlite`).

### Dependencies
All testing dependencies are included in the `dev` optional dependency group in `pyproject.toml`.

## Running Tests

### Using `uv` (Recommended)
To run the full test suite:
```bash
uv run pytest
```

To run with coverage report:
```bash
uv run pytest --cov
```

### Running Specific Tests
You can target specific directories or files:
```bash
# Run only unit tests
uv run pytest test/unit

# Run only database integration tests
uv run pytest test/integration/database
```

## Continuous Integration
Tests are automatically run on GitHub Actions for every push and pull request to the `main` branch. The CI environment automatically downloads the required database to perform integration testing.
