"""
Database query helper functions.

This module contains helper functions for executing database queries
with timing and error handling.
"""

import time

from astropy.coordinates import SkyCoord
from astropy.units import Quantity

from astro_web.config import (
    DEC_COLUMN,
    RA_COLUMN,
)
from astro_web.database import get_db


def search_objects(query: str):
    """
    Search for objects in the database using astrodbkit.

    Args:
        query (str): The search query string
        db_path (str): Path to the database file

    Returns:
        tuple: (results, execution_time) where results is a list of search results
               and execution_time is the time taken in seconds
    """
    start_time = time.time()
    with get_db() as db:
        results = db.search_object(query.strip(), resolve_simbad=True, fmt="pandas")
    execution_time = time.time() - start_time

    return results, execution_time


def parse_coordinates_string(coords_str):
    """
    Parse a combined coordinate string (RA and Dec) to decimal degrees.

    The coordinate string can contain both RA and Dec in various formats.
    Uses SkyCoord to handle all parsing.

    Args:
        coords_str (str): Combined coordinate string (e.g., "13h57m12s +14d28m39s" or "209.30 14.48")

    Returns:
        tuple: (ra_decimal, dec_decimal) in degrees

    Raises:
        ValueError: If coordinates cannot be parsed
    """
    coords_str = coords_str.strip()

    # Check if the string contains sexagesimal indicators or has multiple parts
    parts = coords_str.split()
    has_sexagesimal = (
        any(char in coords_str.lower() for char in ["h", "m", "s", "d", "°", "'", '"', ":"]) or len(parts) > 2
    )

    try:
        if has_sexagesimal:
            # For sexagesimal format, assume hourangle for RA if not explicit
            skycoord = SkyCoord(coords_str, frame="icrs", unit=("hour", "deg"))
            ra_decimal = skycoord.ra.deg
            dec_decimal = skycoord.dec.deg
        else:
            # For decimal format, split and parse manually
            if len(parts) != 2:
                raise ValueError("Expected two space-separated values for decimal coordinates (e.g., '209.30 14.48')")

            ra_decimal = float(parts[0])
            dec_decimal = float(parts[1])

        # Validate coordinate ranges
        if not (0 <= ra_decimal <= 360):
            raise ValueError(f"RA must be between 0 and 360 degrees, got {ra_decimal}")
        if not (-90 <= dec_decimal <= 90):
            raise ValueError(f"Dec must be between -90 and +90 degrees, got {dec_decimal}")

        return ra_decimal, dec_decimal

    except ValueError as e:
        # Re-raise ValueError to preserve the error message
        raise e from None
    except (TypeError, KeyError) as e:
        raise ValueError(f"Invalid coordinate format: {coords_str}") from e


def convert_radius_to_degrees(radius_value, radius_unit):
    """
    Convert radius from user-selected unit to degrees.

    Args:
        radius_value (str or float): Radius value as number
        radius_unit (str): Unit of radius ("degrees", "arcminutes", "arcseconds")

    Returns:
        float: Radius in degrees

    Raises:
        ValueError: If radius_unit is invalid or radius exceeds 10 degrees
    """
    # Convert to float
    radius_val = float(radius_value)

    # Validate radius is positive
    if radius_val <= 0:
        raise ValueError("Radius must be a positive number")

    # Convert based on unit
    if radius_unit == "degrees":
        radius_deg = radius_val
    elif radius_unit == "arcminutes":
        radius_deg = radius_val / 60.0
    elif radius_unit == "arcseconds":
        radius_deg = radius_val / 3600.0
    else:
        raise ValueError(f"Invalid radius unit: {radius_unit}. Must be degrees, arcminutes, or arcseconds")

    # Validate radius does not exceed 10 degrees
    if radius_deg > 10.0:
        raise ValueError("Radius must not exceed 10 degrees after unit conversion")

    return radius_deg


def cone_search(ra, dec, radius_deg):
    """
    Perform a cone search for objects within a specified region of the sky.

    Args:
        ra (float): Right Ascension in decimal degrees (0-360)
        dec (float): Declination in decimal degrees (-90 to +90)
        radius_deg (float): Search radius in degrees

    Returns:
        tuple: (results, execution_time) where results is a DataFrame
               and execution_time is the time taken in seconds
    """
    start_time = time.time()
    coords = SkyCoord(ra, dec, unit="deg")
    radius = Quantity(radius_deg, "deg")

    with get_db() as db:
        results = db.query_region(coords, radius=radius, fmt="pandas", ra_col=RA_COLUMN, dec_col=DEC_COLUMN)

    execution_time = time.time() - start_time

    # Apply 10,000 result cap if needed
    if len(results) > 10000:
        results = results.head(10000)

    return results, execution_time
