#!/usr/bin/env python3
"""Standalone test for CHMI alerts parser without requiring Home Assistant."""

import sys
from pathlib import Path

# Add the custom_components directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import only the parser module (not the whole package)
import importlib.util

spec = importlib.util.spec_from_file_location(
    "cap_parser",
    Path(__file__).parent.parent
    / "custom_components"
    / "chmi_alerts"
    / "cap_parser.py",
)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

# Test sample CAP XML
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


def run_tests():
    """Run parser tests."""
    print("Testing CAP Parser...")

    # Test 1: Parse single alert
    print("\n1. Testing parse_cap_xml...")
    alerts = parser.parse_cap_xml(SAMPLE_CAP_XML)
    assert len(alerts) == 1, f"Expected 1 alert, got {len(alerts)}"
    print("   ✓ Parsed 1 alert")

    # Test 2: Alert properties
    print("\n2. Testing alert properties...")
    alert = alerts[0]
    assert isinstance(alert, parser.CAPAlert), "Alert is not CAPAlert instance"
    assert alert.identifier == "TEST-ALERT-001"
    assert alert.sender == "test@example.com"
    assert alert.status == "Actual"
    assert alert.msg_type == "Alert"
    print("   ✓ Basic properties correct")

    # Test 3: Alert info
    print("\n3. Testing alert info...")
    assert alert.headline == "Severe Weather Alert"
    assert alert.description == "Heavy rain and strong winds expected"
    assert alert.severity == "Severe"
    assert alert.urgency == "Immediate"
    assert alert.certainty == "Observed"
    assert alert.event == "Severe Weather"
    print("   ✓ Info properties correct")

    # Test 4: Areas
    print("\n4. Testing areas...")
    areas = alert.areas
    assert len(areas) == 2, f"Expected 2 areas, got {len(areas)}"
    assert "Prague" in areas
    assert "Central Bohemia" in areas
    print("   ✓ Areas correct")

    # Test 5: Area filtering
    print("\n5. Testing area filtering...")
    assert alert.matches_area("Prague") is True
    assert alert.matches_area("prague") is True  # Case insensitive
    assert alert.matches_area("Bohemia") is True
    assert alert.matches_area("Brno") is False
    assert alert.matches_area(None) is True  # No filter matches all
    print("   ✓ Area filtering works")

    # Test 6: Geocode filtering
    print("\n6. Testing geocode filtering...")
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
    geocode_alerts = parser.parse_cap_xml(geocode_xml)
    assert len(geocode_alerts) == 1
    geo_alert = geocode_alerts[0]

    # Check geocodes property
    geocodes = geo_alert.geocodes
    assert len(geocodes) == 2, f"Expected 2 geocodes, got {len(geocodes)}"
    assert "2102" in geocodes
    assert "CZ02102" in geocodes

    # Test matching by geocode values
    assert geo_alert.matches_area("2102") is True
    assert geo_alert.matches_area("CZ02102") is True
    assert geo_alert.matches_area("cz02102") is True  # Case insensitive
    assert geo_alert.matches_area("9999") is False
    print("   ✓ Geocode filtering works")

    # Test 7: Invalid XML
    print("\n7. Testing invalid XML...")
    invalid_alerts = parser.parse_cap_xml("<invalid>test</invalid>")
    assert len(invalid_alerts) == 0
    print("   ✓ Invalid XML handled correctly")

    # Test 8: Empty XML
    print("\n8. Testing empty XML...")
    empty_alerts = parser.parse_cap_xml("")
    assert len(empty_alerts) == 0
    print("   ✓ Empty XML handled correctly")

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)


if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
