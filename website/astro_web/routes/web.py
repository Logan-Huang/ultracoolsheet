"""
Web page routes for Hello World website.

This module contains all HTML page routes including homepage and error pages.
"""

from datetime import datetime
from urllib.parse import unquote

from fastapi import Form, HTTPException, Request
from fastapi.templating import Jinja2Templates

from astro_web.config import get_source_url
from astro_web.database.query import cone_search, convert_radius_to_degrees, parse_coordinates_string, search_objects
from astro_web.database.sources import get_all_sources, get_source_inventory, get_source_spectra
from astro_web.visualizations.scatter import create_scatter_plot
from astro_web.visualizations.spectra import generate_spectra_plot

# Templates instance - will be imported from main
templates = None


def set_templates(templates_instance: Jinja2Templates):
    """Set the templates instance from main module."""
    global templates  # noqa: PLW0603
    templates = templates_instance


def create_navigation_context(current_page="/"):
    """
    Generate navigation items with active state for the navigation bar.

    Args:
        current_page (str): Route of the current page (e.g., "/", "/browse", "/plots")

    Returns:
        dict: Navigation context with list of navigation items
    """
    nav_items = [
        {"label": "Home", "route": "/", "is_active": current_page == "/"},
        {
            "label": "Browse Database",
            "route": "/browse",
            "is_active": current_page == "/browse",
        },
        {"label": "Search", "route": "/search", "is_active": current_page == "/search"},
        {"label": "Plots", "route": "/plots", "is_active": current_page == "/plots"},
    ]
    return {"nav_items": nav_items}


async def homepage(request: Request):
    """Render the homepage"""

    # Create navigation context with active page
    nav_context = create_navigation_context(current_page="/")

    return templates.TemplateResponse(request, "index.html", {"request": request, **nav_context})


async def browse(request: Request):
    """Render the browse database page with Sources table."""

    # Get all Sources from database
    sources_data = get_all_sources()

    # Apply source URL conversion
    sources_data = get_source_url(sources_data)

    # Handle errors
    has_error = sources_data is None
    error_message = "Sources data could not be loaded at this time." if has_error else None

    # Create navigation context with active page
    nav_context = create_navigation_context(current_page="/browse")

    return templates.TemplateResponse(
        request,
        "browse.html",
        {
            "request": request,
            "sources_data": sources_data if not has_error else [],
            "has_error": has_error,
            "error_message": error_message,
            **nav_context,
        },
    )


async def plot(request: Request):
    """Render the plots page with scatter visualization."""
    # Generate scatter plot
    plot = create_scatter_plot()

    # Create navigation context with active page
    nav_context = create_navigation_context(current_page="/plots")

    return templates.TemplateResponse(
        request,
        "plot.html",
        {
            "request": request,
            "plot_script": plot["script"],
            "plot_div": plot["div"],
            **nav_context,
        },
    )


async def inventory(request: Request, source_name: str):
    """Render the source inventory page."""

    # Get decoded source name for display
    decoded_source_name = unquote(source_name)

    # Get inventory data
    inventory_data = get_source_inventory(source_name)

    # Check if spectra exist for this source
    spectra_df = get_source_spectra(source_name, convert_to_spectrum=False)
    if spectra_df is None:
        has_spectra = False
    else:
        has_spectra = spectra_df is not None and not spectra_df.empty

    # Handle errors
    if inventory_data is None:
        # Source not found
        has_error = True
        error_message = f"Source not found: {decoded_source_name}"
    else:
        has_error = False
        error_message = None

    # Create navigation context with active page
    nav_context = create_navigation_context(current_page=f"/source/{source_name}")

    return templates.TemplateResponse(
        request,
        "inventory.html",
        {
            "request": request,
            "source_name": decoded_source_name,
            "inventory_data": inventory_data if not has_error else {},
            "has_error": has_error,
            "error_message": error_message,
            "has_spectra": has_spectra,
            **nav_context,
        },
        status_code=404 if has_error else 200,
    )


async def spectra_display(request: Request, source_name: str):
    """Render the spectra visualization page for a specific source."""

    # Get decoded source name for display
    decoded_source_name = unquote(source_name)

    # Get spectra data from database
    spectra_df = get_source_spectra(source_name, convert_to_spectrum=True)

    # Generate the plot
    plot_data = generate_spectra_plot(spectra_df)

    # Handle errors
    has_error = spectra_df is None
    if has_error:
        error_message = f"Could not load spectra for: {decoded_source_name}"
    else:
        error_message = None

    # Create navigation context with active page
    nav_context = create_navigation_context(current_page=f"/source/{source_name}/spectra")

    return templates.TemplateResponse(
        request,
        "spectra.html",
        {
            "request": request,
            "source_name": decoded_source_name,
            "plot_script": plot_data.get("script", ""),
            "plot_div": plot_data.get("div", ""),
            "spectra_count": plot_data.get("spectra_count", 0),
            "has_spectra": plot_data.get("has_spectra", False),
            "spectra_metadata": plot_data.get("spectra_metadata", []),
            "has_error": has_error,
            "error_message": error_message,
            **nav_context,
        },
        status_code=404 if has_error else 200,
    )


async def search_form(request: Request):
    """Display search form page"""
    # Create navigation context with active page
    nav_context = create_navigation_context(current_page="/search")

    return templates.TemplateResponse(request, "search.html", {"request": request, **nav_context})


async def search_results(request: Request, query: str = Form(...)):
    """Process search query and display results"""
    try:
        # Validate query
        if not query.strip():
            nav_context = create_navigation_context(current_page="/search")
            return templates.TemplateResponse(
                request, "search.html", {"request": request, "error": "Please enter a search term", **nav_context}
            )

        # Execute search using astrodbkit
        results, execution_time = search_objects(query.strip())

        # Format results for display - convert pandas DataFrame to list of dicts
        formatted_results = results.to_dict("records")

        # Apply source URL conversion
        formatted_results = get_source_url(formatted_results)

        # Create navigation context with active page
        nav_context = create_navigation_context(current_page="/search")

        return templates.TemplateResponse(
            request,
            "search_results.html",
            {
                "request": request,
                "query_text": query.strip(),
                "results": formatted_results,
                "total_count": len(formatted_results),
                "execution_time": f"{execution_time:.3f}",
                **nav_context,
            },
        )

    except Exception as e:
        # Handle astrodbkit errors
        nav_context = create_navigation_context(current_page="/search")
        return templates.TemplateResponse(
            request,
            "search_results.html",
            {
                "request": request,
                "query_text": query.strip() if query else "",
                "error": f"An error occurred during search: {e}",
                "results": [],
                "total_count": 0,
                "execution_time": "0.000",
                **nav_context,
            },
        )


async def search_api(query: str = Form(...)):
    """API endpoint for programmatic search access"""
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query parameter is required")

        results, execution_time = search_objects(query.strip())

        # Convert pandas DataFrame to list of dicts
        formatted_results = results.to_dict("records")

        return {
            "results": formatted_results,
            "total_count": len(formatted_results),
            "query_text": query.strip(),
            "search_time": datetime.now().isoformat(),
            "execution_time": execution_time,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during search: {e}")


async def cone_search_results(
    request: Request, coordinates: str = Form(...), radius: str = Form(...), radius_unit: str = Form(...)
):
    """Process cone search query and display results"""

    # Create navigation context
    nav_context = create_navigation_context(current_page="/search")

    try:
        # Parse coordinates from single string
        ra_decimal, dec_decimal = parse_coordinates_string(coordinates)

        # Convert and validate radius
        radius_degrees = convert_radius_to_degrees(radius, radius_unit)

        # Execute cone search
        results, execution_time = cone_search(ra_decimal, dec_decimal, radius_degrees)

        # Check if results were truncated
        warning = None
        if len(results) >= 10000:
            warning = "Results limited to 10,000 objects. Refine search to see all results."

        # Format results for display
        formatted_results = results.to_dict("records")

        # Apply source URL conversion
        formatted_results = get_source_url(formatted_results)

        return templates.TemplateResponse(
            request,
            "search_results.html",
            {
                "request": request,
                "query_text": f"Coords={coordinates}, Radius={radius} {radius_unit}",
                "results": formatted_results,
                "total_count": len(formatted_results),
                "execution_time": f"{execution_time:.3f}",
                "warning": warning,
                "coordinates_input": coordinates,
                "radius_value": radius,
                "radius_unit": radius_unit,
                **nav_context,
            },
        )

    except ValueError as e:
        # Validation errors - return to search page with error
        return templates.TemplateResponse(request, "search.html", {"request": request, "error": str(e), **nav_context})
    except Exception as e:
        # Database errors - return results page with error
        return templates.TemplateResponse(
            request,
            "search_results.html",
            {
                "request": request,
                "query_text": f"Coords={coordinates}",
                "error": f"An error occurred during search: {e}",
                "results": [],
                "total_count": 0,
                "execution_time": "0.000",
                **nav_context,
            },
        )


async def cone_search_api(coordinates: str = Form(...), radius: str = Form(...), radius_unit: str = Form(...)):
    """API endpoint for programmatic cone search access"""
    try:
        # Parse and validate inputs
        ra_decimal, dec_decimal = parse_coordinates_string(coordinates)
        radius_degrees = convert_radius_to_degrees(radius, radius_unit)

        # Execute search
        results, execution_time = cone_search(ra_decimal, dec_decimal, radius_degrees)

        # Check for truncation
        warning = None
        if len(results) >= 10000:
            warning = "Results limited to 10,000 objects. Refine search to see all results."

        # Format results
        formatted_results = results.to_dict("records")

        return {
            "results": formatted_results,
            "total_count": len(formatted_results),
            "coordinates_input": coordinates,
            "radius_value": radius,
            "radius_unit": radius_unit,
            "search_time": datetime.now().isoformat(),
            "execution_time": execution_time,
            "warning": warning,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during search: {e}")


async def inventory_api(source_name: str = Form(...)):
    """API endpoint for programmatic inventory access"""
    try:
        if not source_name.strip():
            raise HTTPException(status_code=400, detail="source_name parameter is required")

        inventory_data = get_source_inventory(source_name.strip())

        if inventory_data is None:
            raise HTTPException(status_code=404, detail=f"Source not found: {source_name.strip()}")

        return {
            "source_name": source_name.strip(),
            "inventory": inventory_data,
            "retrieval_time": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


async def not_found(request: Request, path: str):
    """Render 404 error page for non-existent routes."""
    return templates.TemplateResponse(request, "404.html", {"request": request, "path": path}, status_code=404)
