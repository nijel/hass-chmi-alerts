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
