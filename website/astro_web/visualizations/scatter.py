"""
Scatter plot visualization for astronomical Sources data.

This module generates interactive Bokeh scatter plots with ra vs dec
coordinates from the Sources table.
"""

from bokeh.embed import components
from bokeh.plotting import figure

from astro_web.config import DEC_COLUMN, RA_COLUMN
from astro_web.database.sources import get_all_sources


def create_scatter_plot():
    """
    Create an interactive Bokeh scatter plot of ra vs dec coordinates.

    Returns:
        dict: Dictionary with 'script' and 'div' components for embedding in HTML.
    """
    # Get Sources data from database
    sources_data = get_all_sources()

    # Filter sources with valid ra and dec coordinates
    valid_sources = [
        s
        for s in sources_data
        if sources_data is not None and s.get(RA_COLUMN) is not None and s.get(DEC_COLUMN) is not None
    ]

    if not valid_sources:
        # Return empty plot if no valid data
        p = figure(
            width=800,
            height=400,
            title="Sources Coordinates",
            x_axis_label="Right Ascension (deg)",
            y_axis_label="Declination (deg)",
            tools="pan,box_zoom,wheel_zoom,reset,save",
        )
    else:
        # Extract ra and dec values
        ras = [s[RA_COLUMN] for s in valid_sources]
        decs = [s[DEC_COLUMN] for s in valid_sources]
        source_ids = [s.get("source", "") for s in valid_sources]

        # Create figure
        p = figure(
            width=800,
            height=400,
            title="Coordinates",
            x_axis_label="Right Ascension (deg)",
            y_axis_label="Declination (deg)",
            tools="hover,pan,box_zoom,wheel_zoom,reset,save",
        )

        # Add scatter points with data source for hover tooltips
        _ = p.scatter(
            "ra",
            "dec",
            size=8,
            alpha=0.6,
            color="#6366f1",
            marker="circle",
            source={"ra": ras, "dec": decs, "source": source_ids},
        )

        # Configure hover tooltips
        p.hover.tooltips = [("Source", "@source"), ("RA", "@ra"), ("Dec", "@dec")]

    # Style the plot
    p.background_fill_color = "#f5f5f7"
    p.border_fill_color = "white"

    # Export as embeddable components
    script, div = components(p)

    return {"script": script, "div": div}
