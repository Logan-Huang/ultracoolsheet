"""
Spectra visualization for astronomical sources.

This module generates interactive Bokeh plots displaying multiple spectra for a source
with formatted legends and metadata.
"""

import astropy.units as u
from bokeh.embed import components
from bokeh.plotting import figure

from astro_web.config import SPECTRA_URL_COLUMN


def generate_spectra_plot(spectra_df):
    """
    Generate an interactive Bokeh plot displaying all spectra for a source.

    Args:
        spectra_df (pandas.DataFrame): DataFrame with spectrum data including wavelength,
                                      flux, observation_date, regime, telescope, instrument

    Returns:
        dict: Dictionary with 'script', 'div', 'spectra_count', 'has_spectra', and
              'spectra_metadata' keys for embedding in HTML template
    """
    # Initialize return values
    plot_script = ""
    plot_div = ""
    spectra_count = 0
    has_spectra = False
    spectra_metadata = []

    # Check if spectra data exists and is valid
    if spectra_df is None or spectra_df.empty:
        return {
            "script": plot_script,
            "div": plot_div,
            "spectra_count": spectra_count,
            "has_spectra": has_spectra,
            "spectra_metadata": spectra_metadata,
        }

    # Create the figure
    p = figure(
        width=900,
        height=500,
        title="Spectra",
        x_axis_label="Wavelength (μm)",
        y_axis_label="Flux",
        tools="pan,box_zoom,wheel_zoom,reset,save",
    )

    # Plot each spectrum
    colors = [
        "#6366f1",  # indigo
        "#8b5cf6",  # purple
        "#ec4899",  # pink
        "#f59e0b",  # amber
        "#10b981",  # emerald
        "#3b82f6",  # blue
        "#ef4444",  # red
        "#06b6d4",  # cyan
        "#84cc16",  # lime
        "#f97316",  # orange
    ]

    # First pass: Extract metadata for ALL spectra
    for idx, (_, row) in enumerate(spectra_df.iterrows()):
        # Format basic metadata for all spectra
        obs_date = str(row.get("observation_date", "-"))
        regime = str(row.get("regime", "-"))
        telescope = str(row.get("telescope", "-"))
        instrument = str(row.get("instrument", "-"))
        reference = str(row.get("reference", "-"))
        legend_label = f"{obs_date} | {regime} | {telescope}/{instrument}"

        # Store metadata for all spectra (will update display_status later)
        metadata = {
            "observation_date": obs_date,
            "regime": regime,
            "telescope": telescope,
            "instrument": instrument,
            "reference": reference,
            "access_url": row.get(SPECTRA_URL_COLUMN, ""),
            "legend_label": legend_label,
            "display_status": "failed",  # Default to failed, will update if successful
        }
        spectra_metadata.append(metadata)

    # Second pass: Attempt to plot each spectrum and update status
    spectra_count = 0
    for idx, (_, row) in enumerate(spectra_df.iterrows()):
        try:
            spec = row.get("processed_spectrum")
            # Get wavelength and flux data
            wavelength = spec.spectral_axis.to(u.micron).value
            flux = spec.flux.value

            # Skip if data is missing or invalid
            if wavelength is None or flux is None:
                continue

            # Convert to numpy arrays if needed
            if hasattr(wavelength, "values"):
                wavelength = wavelength.values
            if hasattr(flux, "values"):
                flux = flux.values

            # Plot the spectrum with color cycling
            color = colors[idx % len(colors)]
            p.line(
                wavelength,
                flux,
                legend_label=spectra_metadata[idx]["legend_label"],
                line_width=2,
                color=color,
                alpha=0.8,
            )

            # Update metadata status to displayed
            spectra_metadata[idx]["display_status"] = "displayed"
            spectra_count += 1

        except Exception:
            # Keep display_status as "failed" for this spectrum
            continue

    # Configure plot styling
    p.background_fill_color = "#f5f5f7"
    p.border_fill_color = "white"

    # Only configure legend if we have spectra plotted
    if spectra_count > 0:
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"

    # Export as embeddable components
    if spectra_count > 0:
        has_spectra = True
        script, div = components(p)
        plot_script = script
        plot_div = div
    elif len(spectra_metadata) > 0:
        # Even if no spectra could be plotted, we have metadata to show
        has_spectra = True

    return {
        "script": plot_script,
        "div": plot_div,
        "spectra_count": spectra_count,
        "has_spectra": has_spectra,
        "spectra_metadata": spectra_metadata,
    }
