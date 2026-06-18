# Astro-Web Configuration

## Environment Variables

You can customize the application behavior by setting these environment variables:

### Database Configuration

- `ASTRO_WEB_DATABASE_URL`: Database connection string
  - Default: `sqlite:///SIMPLE.sqlite`
  - Examples:
    - SQLite: `sqlite:///path/to/database.db`
    - PostgreSQL: `postgresql://username:password@localhost:5432/astrodb`
    - MySQL: `mysql://username:password@localhost:3306/astrodb`

### Additional Configuration

- `ASTRO_WEB_TOML`: Full path to the `database.toml` file
  - Default: `database.toml` (expected in the current directory)
  - If present, it dictates what path (and name) the server should use for the configuration file.
- `ASTRO_WEB_SOURCE_URL_BASE`: Base URL for source detail pages
  - Default: `/source/`
  - Example: `/astro/sources/` (for custom deployment)
- `ASTRO_WEB_SCHEMA`: Schema name for the database
  - Default: None (for SQLite databases)
  - Example: `public`
- `ASTRO_WEB_PRIMARY_TABLE`: Primary table name for the database (usually Sources)
  - Default: `Sources`
  - Example: `galaxies`
- `ASTRO_WEB_SOURCE_COLUMN`: Column name for the source identifier
  - Default: `source`
- `ASTRO_WEB_FOREIGN_KEY`: Foreign key column name for the primary table
  - Default: `source`
- `ASTRO_WEB_RA_COLUMN`: Column name for the right ascension
  - Default: `ra`
- `ASTRO_WEB_DEC_COLUMN`: Column name for the declination
  - Default: `dec`
- `ASTRO_WEB_SPECTRA_URL_COLUMN`: Column name for the spectrum data URL/path
  - Default: `access_url`
  - Used when retrieving spectra for visualization

### Lookup Tables

- `ASTRO_WEB_LOOKUP_TABLES`: Lookup tables to use for the database (as comma-separated string)
  - Default: `Publications,Telescopes,Instruments,PhotometryFilters,Versions,RegimeList,SourceTypeList,ParameterList,AssociationList,CompanionList`
  - If `database.toml` exists, use the lookup tables from the file, otherwise use the default lookup tables

## Usage

Set environment variables before running the application:

```bash
export ASTRO_WEB_DATABASE_URL="postgresql://user:pass@localhost:5432/astrodb"
export ASTRO_WEB_SOURCE_URL_BASE="/astro/sources/"
export ASTRO_WEB_PRIMARY_TABLE="galaxies"
export ASTRO_WEB_SOURCE_COLUMN="source_id"
export ASTRO_WEB_RA_COLUMN="ra"
export ASTRO_WEB_DEC_COLUMN="dec"
export ASTRO_WEB_SPECTRA_URL_COLUMN="access_url"
export ASTRO_WEB_LOOKUP_TABLES="Publications,Telescopes,Instruments,PhotometryFilters,Versions,RegimeList,SourceTypeList,ParameterList,AssociationList,CompanionList"
uvicorn src.main:app --reload --port 8000
```

It is recommended to create a `.env` file in the root directory and add the environment variables to it. See `.env.example` for an example.
