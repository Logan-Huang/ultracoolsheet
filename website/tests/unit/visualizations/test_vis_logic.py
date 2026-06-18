import pandas as pd
from astro_web.visualizations.scatter import create_scatter_plot
from astro_web.visualizations.spectra import generate_spectra_plot

def test_create_scatter_plot_logic():
    """Verify create_scatter_plot returns dict with 'script' and 'div'."""
    plot_data = create_scatter_plot()
    assert isinstance(plot_data, dict)
    assert "script" in plot_data
    assert "div" in plot_data
    assert plot_data["script"].startswith("<script")
    assert plot_data["div"].startswith("<div")

def test_generate_spectra_plot_logic_empty():
    """Verify handling of empty spectra lists."""
    # Empty DataFrame
    df_empty = pd.DataFrame()
    plot_data = generate_spectra_plot(df_empty)
    assert plot_data["has_spectra"] is False
    assert plot_data["spectra_count"] == 0
    assert plot_data["script"] == ""
    
    # None input
    plot_data = generate_spectra_plot(None)
    assert plot_data["has_spectra"] is False

def test_generate_spectra_plot_logic_with_data():
    """Verify handling of multiple spectra."""
    # We need a mock spectrum object that has .spectral_axis and .flux
    class MockAxis:
        def to(self, unit):
            return self
        @property
        def value(self):
            return [1, 2, 3]
            
    class MockFlux:
        @property
        def value(self):
            return [10, 20, 30]
            
    class MockSpectrum:
        def __init__(self):
            self.spectral_axis = MockAxis()
            self.flux = MockFlux()

    spectra_df = pd.DataFrame([
        {
            "observation_date": "2023-01-01",
            "regime": "NIR",
            "telescope": "Keck",
            "instrument": "NIRSPEC",
            "processed_spectrum": MockSpectrum()
        },
        {
            "observation_date": "2023-01-02",
            "regime": "Optical",
            "telescope": "VLT",
            "instrument": "X-Shooter",
            "processed_spectrum": MockSpectrum()
        }
    ])
    
    plot_data = generate_spectra_plot(spectra_df)
    assert plot_data["has_spectra"] is True
    assert plot_data["spectra_count"] == 2
    assert "script" in plot_data
    assert "div" in plot_data
    assert len(plot_data["spectra_metadata"]) == 2
    assert plot_data["spectra_metadata"][0]["display_status"] == "displayed"
