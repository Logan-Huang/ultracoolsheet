"""
Configuration settings for the Astro-Web application.

This module contains all configurable settings including database connection
and URL generation parameters.
"""

import os
import pandas as pd
import tomllib
from urllib.parse import quote
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# Database Configuration
# Default to SQLite database in project root
CONNECTION_STRING = os.getenv("ASTRO_WEB_DATABASE_URL", "sqlite:///SIMPLE.sqlite")

# Base URL for source detail pages - can be customized for different deployments
ASTRO_WEB_SOURCE_URL_BASE = os.getenv("ASTRO_WEB_SOURCE_URL_BASE", "/source/")
PRIMARY_TABLE = os.getenv("ASTRO_WEB_PRIMARY_TABLE", "Sources")
SOURCE_COLUMN = os.getenv("ASTRO_WEB_SOURCE_COLUMN", "source")
FOREIGN_KEY = os.getenv("ASTRO_WEB_FOREIGN_KEY", "source")  # typically the same as SOURCE_COLUMN
PRIMARY_DATATYPE = os.getenv("ASTRO_WEB_PRIMARY_DATATYPE", "str")
if PRIMARY_DATATYPE is not None and PRIMARY_DATATYPE == "str":
    PRIMARY_DATATYPE = str
elif PRIMARY_DATATYPE is not None and PRIMARY_DATATYPE == "int":
    PRIMARY_DATATYPE = int
else:
    raise ValueError(f"Invalid PRIMARY_DATATYPE: {PRIMARY_DATATYPE}. Must be str or int")

# RA/Dec column names
RA_COLUMN = os.getenv("ASTRO_WEB_RA_COLUMN", "ra")
DEC_COLUMN = os.getenv("ASTRO_WEB_DEC_COLUMN", "dec")
# Spectra URL column name
SPECTRA_URL_COLUMN = os.getenv("ASTRO_WEB_SPECTRA_URL_COLUMN", "access_url")

# Schema (for postgres and other databases)
SCHEMA = os.getenv("ASTRO_WEB_SCHEMA", None)
if SCHEMA is not None and SCHEMA == "":
    SCHEMA = None

# Lookup tables for proper inventory management
default_lookup_tables = [
    "Publications",
    "Telescopes",
    "Instruments",
    "Modes",
    "Filters",
    "PhotometryFilters",
    "Citations",
    "References",
    "Versions",
    "Parameters",
    "Regimes",
    "RegimeList",
    "ParameterList",
    "AssociationList",
    "CompanionList",
    "SourceTypeList",
]
LOOKUP_TABLES = os.getenv("ASTRO_WEB_LOOKUP_TABLES", None)
# Path to the database configuration file
TOML_PATH = os.getenv("ASTRO_WEB_TOML", "database.toml")
if TOML_PATH == "":
    TOML_PATH = "database.toml"

# If the TOML file exists, use the lookup tables from the file
if os.path.exists(TOML_PATH):
    with open(TOML_PATH, "rb") as f:
        database_config = tomllib.load(f)
    LOOKUP_TABLES = database_config.get("lookup_tables", LOOKUP_TABLES)
elif LOOKUP_TABLES is not None and isinstance(LOOKUP_TABLES, str):
    LOOKUP_TABLES = LOOKUP_TABLES.split(",")
else:
    LOOKUP_TABLES = default_lookup_tables


def get_source_url(results):
    """
    Given a pandas DataFrame or list of dictionaries, convert the SOURCE_COLUMN to a complete URL for the source detail page.

    Args:
        results: Either a pandas DataFrame or list of dictionaries to convert

    Returns:
        Same type as input: DataFrame or list of dictionaries with the SOURCE_COLUMN converted to a complete URL for the source detail page
    """
    if results is None:
        return None

    # Handle list of dictionaries (from database queries)
    if isinstance(results, list):
        new_results = []
        for record in results:
            new_record = record.copy()
            if SOURCE_COLUMN in new_record:
                new_record[SOURCE_COLUMN] = (
                    f"<a href='{ASTRO_WEB_SOURCE_URL_BASE}{quote(str(new_record[SOURCE_COLUMN]))}'>{new_record[SOURCE_COLUMN]}</a>"
                )
            new_results.append(new_record)
        return new_results

    # Handle pandas DataFrame
    elif isinstance(results, pd.DataFrame):
        new_results = results.copy()
        if SOURCE_COLUMN in new_results.columns:
            new_results[SOURCE_COLUMN] = new_results[SOURCE_COLUMN].apply(
                lambda x: f"<a href='{ASTRO_WEB_SOURCE_URL_BASE}{quote(str(x))}'>{x}</a>"
            )
        return new_results

    # Fallback for other types
    else:
        return results
