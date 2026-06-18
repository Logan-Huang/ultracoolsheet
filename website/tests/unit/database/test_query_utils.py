import pytest
from astro_web.database.query import parse_coordinates_string, convert_radius_to_degrees

def test_parse_coordinates_string_decimal():
    """Verify correct parsing of 'RA Dec' decimal strings."""
    ra, dec = parse_coordinates_string("209.30 14.48")
    assert ra == 209.30
    assert dec == 14.48
    
    # Test with extra spaces
    ra, dec = parse_coordinates_string("  180.0   -45.0  ")
    assert ra == 180.0
    assert dec == -45.0

def test_parse_coordinates_string_sexagesimal():
    """Verify correct parsing of sexagesimal strings."""
    # SkyCoord handles these, we just verify the output is as expected
    ra, dec = parse_coordinates_string("13h57m12s +14d28m39s")
    assert pytest.approx(ra, rel=1e-5) == 209.3
    assert pytest.approx(dec, rel=1e-5) == 14.4775
    
    # Another format
    ra, dec = parse_coordinates_string("13:57:12 +14:28:39")
    assert pytest.approx(ra, rel=1e-5) == 209.3
    assert pytest.approx(dec, rel=1e-5) == 14.4775

def test_parse_coordinates_string_invalid():
    """Verify ValueError is raised for invalid formats."""
    # Wrong number of parts
    with pytest.raises(ValueError, match="Expected two space-separated values"):
        parse_coordinates_string("209.30")
    
    # Non-numeric
    with pytest.raises(ValueError):
        parse_coordinates_string("abc def")
    
    # Out of range RA
    with pytest.raises(ValueError, match="RA must be between 0 and 360"):
        parse_coordinates_string("361.0 10.0")
    
    # Out of range Dec
    with pytest.raises(ValueError, match=r"Dec must be between -90 and \+90"):
        parse_coordinates_string("180.0 95.0")

def test_convert_radius_to_degrees():
    """Verify conversion from arcminutes/arcseconds to degrees."""
    # Degrees to degrees
    assert convert_radius_to_degrees(1.0, "degrees") == 1.0
    
    # Arcminutes to degrees
    assert convert_radius_to_degrees(60.0, "arcminutes") == 1.0
    assert convert_radius_to_degrees(1.0, "arcminutes") == 1.0/60.0
    
    # Arcseconds to degrees
    assert convert_radius_to_degrees(3600.0, "arcseconds") == 1.0
    assert convert_radius_to_degrees(1.0, "arcseconds") == 1.0/3600.0
    
    # Test with string input
    assert convert_radius_to_degrees("1.5", "degrees") == 1.5

def test_convert_radius_validation():
    """Verify errors for negative radius or radius > 10 degrees."""
    # Negative radius
    with pytest.raises(ValueError, match="Radius must be a positive number"):
        convert_radius_to_degrees(-1.0, "degrees")
    
    # Zero radius (should be positive)
    with pytest.raises(ValueError, match="Radius must be a positive number"):
        convert_radius_to_degrees(0.0, "degrees")
    
    # Too large radius
    with pytest.raises(ValueError, match="Radius must not exceed 10 degrees"):
        convert_radius_to_degrees(10.1, "degrees")
    
    # Too large radius after conversion (e.g., 601 arcminutes)
    with pytest.raises(ValueError, match="Radius must not exceed 10 degrees"):
        convert_radius_to_degrees(601.0, "arcminutes")
    
    # Invalid unit
    with pytest.raises(ValueError, match="Invalid radius unit"):
        convert_radius_to_degrees(1.0, "kiloparsecs")
