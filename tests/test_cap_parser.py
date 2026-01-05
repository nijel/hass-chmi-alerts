"""Tests for CAP parser."""
import sys
from pathlib import Path

# Add custom_components to path to allow importing without Home Assistant
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.cap_alerts.cap_parser import CAPAlert, parse_cap_xml

# Sample CAP XML for testing
SAMPLE_CAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
    <identifier>TEST-ALERT-001</identifier>
    <sender>test@example.com</sender>
    <sent>2024-01-05T12:00:00+00:00</sent>
    <status>Actual</status>
    <msgType>Alert</msgType>
    <scope>Public</scope>
    <info>
        <language>en-US</language>
        <category>Met</category>
        <event>Severe Weather</event>
        <urgency>Immediate</urgency>
        <severity>Severe</severity>
        <certainty>Observed</certainty>
        <headline>Severe Weather Alert</headline>
        <description>Heavy rain and strong winds expected</description>
        <instruction>Stay indoors and avoid travel</instruction>
        <effective>2024-01-05T12:00:00+00:00</effective>
        <expires>2024-01-05T18:00:00+00:00</expires>
        <area>
            <areaDesc>Prague</areaDesc>
        </area>
        <area>
            <areaDesc>Central Bohemia</areaDesc>
        </area>
    </info>
</alert>
"""


def test_parse_single_alert():
    """Test parsing a single CAP alert."""
    alerts = parse_cap_xml(SAMPLE_CAP_XML)
    
    assert len(alerts) == 1
    alert = alerts[0]
    
    assert isinstance(alert, CAPAlert)
    assert alert.identifier == "TEST-ALERT-001"
    assert alert.sender == "test@example.com"
    assert alert.status == "Actual"
    assert alert.msg_type == "Alert"
    assert alert.scope == "Public"


def test_alert_info():
    """Test accessing alert info data."""
    alerts = parse_cap_xml(SAMPLE_CAP_XML)
    alert = alerts[0]
    
    assert alert.headline == "Severe Weather Alert"
    assert alert.description == "Heavy rain and strong winds expected"
    assert alert.severity == "Severe"
    assert alert.urgency == "Immediate"
    assert alert.certainty == "Observed"
    assert alert.event == "Severe Weather"
    assert alert.instruction == "Stay indoors and avoid travel"
    assert alert.category == "Met"


def test_alert_areas():
    """Test accessing alert areas."""
    alerts = parse_cap_xml(SAMPLE_CAP_XML)
    alert = alerts[0]
    
    areas = alert.areas
    assert len(areas) == 2
    assert "Prague" in areas
    assert "Central Bohemia" in areas


def test_area_filter_match():
    """Test area filtering with match."""
    alerts = parse_cap_xml(SAMPLE_CAP_XML)
    alert = alerts[0]
    
    assert alert.matches_area("Prague") is True
    assert alert.matches_area("prague") is True  # Case insensitive
    assert alert.matches_area("Bohemia") is True
    assert alert.matches_area(None) is True  # No filter matches all


def test_area_filter_no_match():
    """Test area filtering with no match."""
    alerts = parse_cap_xml(SAMPLE_CAP_XML)
    alert = alerts[0]
    
    assert alert.matches_area("Brno") is False
    assert alert.matches_area("Slovakia") is False


def test_empty_xml():
    """Test parsing empty XML."""
    alerts = parse_cap_xml("")
    assert len(alerts) == 0


def test_invalid_xml():
    """Test parsing invalid XML."""
    alerts = parse_cap_xml("<invalid>not cap xml</invalid>")
    assert len(alerts) == 0


def test_multiple_info_sections():
    """Test alert with multiple info sections."""
    multi_info_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-002</identifier>
        <sender>test@example.com</sender>
        <sent>2024-01-05T12:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>en-US</language>
            <headline>First Headline</headline>
            <severity>Severe</severity>
            <area>
                <areaDesc>Area 1</areaDesc>
            </area>
        </info>
        <info>
            <language>cs-CZ</language>
            <headline>Second Headline</headline>
            <severity>Moderate</severity>
            <area>
                <areaDesc>Area 2</areaDesc>
            </area>
        </info>
    </alert>
    """
    
    alerts = parse_cap_xml(multi_info_xml)
    assert len(alerts) == 1
    alert = alerts[0]
    
    # Should return first info section data
    assert alert.headline == "First Headline"
    assert alert.severity == "Severe"
    
    # Areas should include both sections
    areas = alert.areas
    assert len(areas) == 2
    assert "Area 1" in areas
    assert "Area 2" in areas


def test_geocode_parsing():
    """Test parsing geocode values from areas."""
    geocode_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-GEO-001</identifier>
        <sender>test@example.com</sender>
        <sent>2024-01-05T12:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs-CZ</language>
            <headline>Test Alert with Geocodes</headline>
            <severity>Moderate</severity>
            <area>
                <areaDesc>Středočeský kraj (Beroun, Brandýs nad Labem-Stará Boleslav, Černošice, Český Brod, Dobříš, Hořovice, Kladno, Kolín, Kralupy nad Vltavou, Lysá nad Labem, Mělník, Mladá Boleslav, Mnichovo Hradiště, Neratovice, Nymburk, Poděbrady, Rakovník, Říčany, Slaný)</areaDesc>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>2102</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ02102</value>
                </geocode>
            </area>
        </info>
    </alert>
    """
    
    alerts = parse_cap_xml(geocode_xml)
    assert len(alerts) == 1
    alert = alerts[0]
    
    # Check geocodes property
    geocodes = alert.geocodes
    assert len(geocodes) == 2
    assert "2102" in geocodes
    assert "CZ02102" in geocodes


def test_geocode_filter_match():
    """Test area filtering with geocode values."""
    geocode_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-GEO-002</identifier>
        <sender>test@example.com</sender>
        <sent>2024-01-05T12:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs-CZ</language>
            <headline>Test Alert with Geocodes</headline>
            <severity>Moderate</severity>
            <area>
                <areaDesc>Středočeský kraj</areaDesc>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>2102</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ02102</value>
                </geocode>
            </area>
        </info>
    </alert>
    """
    
    alerts = parse_cap_xml(geocode_xml)
    alert = alerts[0]
    
    # Test matching by CISORP code
    assert alert.matches_area("2102") is True
    
    # Test matching by EMMA_ID
    assert alert.matches_area("CZ02102") is True
    assert alert.matches_area("cz02102") is True  # Case insensitive
    
    # Test partial matching
    assert alert.matches_area("02102") is True
    assert alert.matches_area("CZ021") is True
    
    # Test still works with area description
    assert alert.matches_area("Středočeský") is True
    assert alert.matches_area("kraj") is True
    
    # Test no match
    assert alert.matches_area("9999") is False
    assert alert.matches_area("CZ03") is False


def test_multiple_areas_with_geocodes():
    """Test alert with multiple areas having different geocodes."""
    multi_area_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-MULTI-001</identifier>
        <sender>test@example.com</sender>
        <sent>2024-01-05T12:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs-CZ</language>
            <headline>Multi-Area Alert</headline>
            <severity>Severe</severity>
            <area>
                <areaDesc>Region 1</areaDesc>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>1001</value>
                </geocode>
            </area>
            <area>
                <areaDesc>Region 2</areaDesc>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>2002</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ02002</value>
                </geocode>
            </area>
        </info>
    </alert>
    """
    
    alerts = parse_cap_xml(multi_area_xml)
    alert = alerts[0]
    
    # Check all geocodes are collected
    geocodes = alert.geocodes
    assert len(geocodes) == 3
    assert "1001" in geocodes
    assert "2002" in geocodes
    assert "CZ02002" in geocodes
    
    # Test matching any of the geocodes
    assert alert.matches_area("1001") is True
    assert alert.matches_area("2002") is True
    assert alert.matches_area("CZ02002") is True
    
    # Test no duplicate values
    assert geocodes.count("1001") == 1


def test_area_without_geocode():
    """Test that areas without geocodes still work correctly."""
    no_geocode_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-NO-GEO-001</identifier>
        <sender>test@example.com</sender>
        <sent>2024-01-05T12:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>en-US</language>
            <headline>Alert without geocode</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """
    
    alerts = parse_cap_xml(no_geocode_xml)
    alert = alerts[0]
    
    # Should return empty list
    geocodes = alert.geocodes
    assert len(geocodes) == 0
    
    # Area description matching should still work
    assert alert.matches_area("Test Area") is True
    assert alert.matches_area("Test") is True
    assert alert.matches_area("Missing") is False
