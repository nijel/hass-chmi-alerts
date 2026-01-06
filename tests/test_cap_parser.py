"""Tests for CAP parser."""

import sys
from pathlib import Path

# Add custom_components to path to allow importing without Home Assistant
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.chmi_alerts.cap_parser import CAPAlert, parse_cap_xml

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


def test_language_property():
    """Test accessing language property from alert."""
    alerts = parse_cap_xml(SAMPLE_CAP_XML)
    alert = alerts[0]

    # Should return first info section's language
    assert alert.language == "en-US"


def test_language_filter_match():
    """Test language filtering with exact match."""
    language_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-LANG-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <headline>Czech Alert</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(language_xml)
    alert = alerts[0]

    assert alert.matches_language("cs") is True
    assert alert.matches_language("CS") is True  # Case insensitive
    assert alert.matches_language(None) is True  # No filter matches all


def test_language_filter_partial_match():
    """Test language filtering with partial match."""
    language_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-LANG-002</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs-CZ</language>
            <headline>Czech Alert with Region</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(language_xml)
    alert = alerts[0]

    # Prefix match: 'cs' should match 'cs-CZ'
    assert alert.matches_language("cs") is True
    assert alert.matches_language("cs-CZ") is True
    assert alert.matches_language("CS-CZ") is True  # Case insensitive

    # Partial match on region code should NOT match (not a prefix)
    assert alert.matches_language("CZ") is False


def test_language_filter_no_match():
    """Test language filtering with no match."""
    language_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-LANG-003</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs-CZ</language>
            <headline>Czech Alert</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(language_xml)
    alert = alerts[0]

    # Should not match different language codes
    assert alert.matches_language("en") is False
    assert alert.matches_language("de") is False
    assert alert.matches_language("fr-FR") is False


def test_language_filter_no_false_positives():
    """Test that language filtering doesn't produce false positives from substring matches."""
    # Test with 'en' language
    en_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-EN</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>en</language>
            <headline>Test</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(en_xml)
    alert = alerts[0]

    # 'en' should NOT match languages that just contain 'en' as substring
    # These would be false positives with naive substring matching
    assert alert.matches_language("french") is False
    assert alert.matches_language("denver") is False
    assert alert.matches_language("sven") is False

    # Only valid prefix/exact matches should work
    assert alert.matches_language("en") is True
    assert alert.matches_language("EN") is True


def test_language_filter_multiple_info_sections():
    """Test language filtering with multiple info sections."""
    multi_lang_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-MULTILANG-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>en-US</language>
            <headline>English Alert</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>cs</language>
            <headline>Czech Alert</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(multi_lang_xml)
    alert = alerts[0]

    # Should match if any info section has the language
    assert alert.matches_language("en") is True
    assert alert.matches_language("cs") is True
    assert alert.matches_language("en-US") is True

    # Should not match language not in any section
    assert alert.matches_language("de") is False


def test_language_filter_no_language():
    """Test language filtering when alert has no language."""
    no_lang_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-NOLANG-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <headline>Alert without language</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(no_lang_xml)
    alert = alerts[0]

    # Alert without language should not match any specific language filter
    assert alert.matches_language("en") is False
    assert alert.matches_language("cs") is False

    # But should match when no filter is provided
    assert alert.matches_language(None) is True

    # Language property should return empty string
    assert alert.language == ""


def test_multiple_geocodes_same_valuename():
    """Test parsing multiple geocodes with same valueName (e.g., multiple CISORP codes).

    This is a regression test for the issue where only the last geocode value
    for each valueName was kept, causing filtering to fail.
    """
    multi_geocode_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-MULTI-GEOCODE-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <headline>Test Alert with Multiple Geocodes</headline>
            <severity>Minor</severity>
            <area>
                <areaDesc>Královéhradecký kraj (Hořice, Hradec Králové, Jičín, Nový Bydžov)</areaDesc>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>5204</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ05204</value>
                </geocode>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>5205</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ05205</value>
                </geocode>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>5207</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ05207</value>
                </geocode>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>5212</value>
                </geocode>
                <geocode>
                    <valueName>EMMA_ID</valueName>
                    <value>CZ05212</value>
                </geocode>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(multi_geocode_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Check that ALL geocodes are collected, not just the last ones
    geocodes = alert.geocodes
    assert len(geocodes) == 8

    # All CISORP values should be present
    assert "5204" in geocodes
    assert "5205" in geocodes
    assert "5207" in geocodes
    assert "5212" in geocodes

    # All EMMA_ID values should be present
    assert "CZ05204" in geocodes
    assert "CZ05205" in geocodes
    assert "CZ05207" in geocodes
    assert "CZ05212" in geocodes

    # Test filtering matches any of the geocodes
    assert alert.matches_area("5204") is True
    assert alert.matches_area("5205") is True
    assert alert.matches_area("5207") is True
    assert alert.matches_area("5212") is True
    assert alert.matches_area("CZ05204") is True
    assert alert.matches_area("CZ05205") is True
    assert alert.matches_area("CZ05207") is True
    assert alert.matches_area("CZ05212") is True

    # Test that non-existent codes don't match
    assert alert.matches_area("5106") is False
    assert alert.matches_area("CZ05106") is False


def test_multiple_response_types():
    """Test parsing multiple responseType values in a single info section."""
    multi_response_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-RESPONSE-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>en</language>
            <event>Severe Weather</event>
            <responseType>Prepare</responseType>
            <responseType>Avoid</responseType>
            <responseType>Monitor</responseType>
            <severity>Moderate</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(multi_response_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Test new response_types property (returns list)
    response_types = alert.response_types
    assert isinstance(response_types, list)
    assert len(response_types) == 3
    assert "Prepare" in response_types
    assert "Avoid" in response_types
    assert "Monitor" in response_types

    # Test backward compatibility with response_type property (returns first)
    assert alert.response_type == "Prepare"


def test_audience_field():
    """Test parsing audience field from info section."""
    audience_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-AUDIENCE-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Test Alert</event>
            <severity>Minor</severity>
            <audience>veřejnost, HZS, web, Meteoalarm</audience>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(audience_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Test audience property
    assert alert.audience == "veřejnost, HZS, web, Meteoalarm"


def test_sender_name_field():
    """Test parsing senderName field from info section."""
    sender_name_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-SENDER-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Test Alert</event>
            <severity>Minor</severity>
            <senderName>ČHMÚ, Petra Sýkorová</senderName>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(sender_name_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Test sender_name property
    assert alert.sender_name == "ČHMÚ, Petra Sýkorová"


def test_event_code_field():
    """Test parsing eventCode field from info section."""
    event_code_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-EVENTCODE-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Silný mráz</event>
            <severity>Moderate</severity>
            <eventCode>
                <valueName>SIVS</valueName>
                <value>I.4</value>
            </eventCode>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(event_code_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Test event_code property
    event_code = alert.event_code
    assert isinstance(event_code, dict)
    assert "SIVS" in event_code
    assert event_code["SIVS"] == "I.4"


def test_all_new_fields_together():
    """Test parsing all new fields together in a realistic CAP alert."""
    full_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-FULL-001</identifier>
        <sender>chmi@chmi.cz</sender>
        <sent>2026-01-05T10:44:06+01:00</sent>
        <status>Actual</status>
        <msgType>Update</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <category>Met</category>
            <event>Silný mráz</event>
            <responseType>Prepare</responseType>
            <responseType>Avoid</responseType>
            <responseType>Monitor</responseType>
            <urgency>Future</urgency>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <audience>veřejnost, HZS, web, Meteoalarm</audience>
            <eventCode>
                <valueName>SIVS</valueName>
                <value>I.4</value>
            </eventCode>
            <onset>2026-01-05T21:00:00+01:00</onset>
            <expires>2026-01-08T10:00:00+01:00</expires>
            <senderName>ČHMÚ, Petra Sýkorová</senderName>
            <description>Během noci se místy očekává pokles teploty vzduchu pod -12 °C.</description>
            <instruction>Nebezpečí prochladnutí a omrznutí nechráněných částí těla.</instruction>
            <area>
                <areaDesc>Test Area</areaDesc>
                <geocode>
                    <valueName>CISORP</valueName>
                    <value>2101</value>
                </geocode>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(full_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Verify all new fields are parsed correctly
    assert alert.audience == "veřejnost, HZS, web, Meteoalarm"
    assert alert.sender_name == "ČHMÚ, Petra Sýkorová"
    assert alert.event_code == {"SIVS": "I.4"}
    assert alert.response_types == ["Prepare", "Avoid", "Monitor"]
    assert alert.response_type == "Prepare"  # Backward compatibility

    # Verify existing fields still work
    assert alert.event == "Silný mráz"
    assert alert.severity == "Moderate"
    assert (
        alert.description
        == "Během noci se místy očekává pokles teploty vzduchu pod -12 °C."
    )


def test_language_filter_selects_preferred_info():
    """Test that language filter selects the info section with matching language and highest severity.

    This is a regression test for the issue where alerts with multiple info sections
    in different languages would always return properties from the first info section,
    even when a language filter was applied.
    """
    multi_lang_severity_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-MULTILANG-SEVERITY-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Žádná výstraha před teplotou</event>
            <severity>Minor</severity>
            <certainty>Unlikely</certainty>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>en-GB</language>
            <event>Minor Temperature Warning</event>
            <severity>Minor</severity>
            <certainty>Unlikely</certainty>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>cs</language>
            <event>Silný mráz</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>en-GB</language>
            <event>Heavy Frost</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(multi_lang_severity_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Without language filter, should return first info section
    assert alert.event == "Žádná výstraha před teplotou"
    assert alert.severity == "Minor"
    assert alert.certainty == "Unlikely"
    assert alert.language == "cs"

    # With language filter set to 'cs', should return Czech info with highest severity
    alert.set_language_filter("cs")
    assert alert.event == "Silný mráz"
    assert alert.severity == "Moderate"
    assert alert.certainty == "Likely"
    assert alert.language == "cs"

    # With language filter set to 'en-GB', should return English info with highest severity
    alert.set_language_filter("en-GB")
    assert alert.event == "Heavy Frost"
    assert alert.severity == "Moderate"
    assert alert.certainty == "Likely"
    assert alert.language == "en-GB"

    # With language filter set to 'en' (prefix), should match 'en-GB'
    alert.set_language_filter("en")
    assert alert.event == "Heavy Frost"
    assert alert.severity == "Moderate"
    assert alert.language == "en-GB"


def test_language_filter_with_only_matching_severity():
    """Test language filter when only one severity level matches the language."""
    single_severity_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-SINGLE-SEVERITY-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Silný vítr</event>
            <severity>Severe</severity>
            <certainty>Likely</certainty>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>en</language>
            <event>Strong Wind</event>
            <severity>Severe</severity>
            <certainty>Likely</certainty>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(single_severity_xml)
    alert = alerts[0]

    # With Czech filter, should get Czech info
    alert.set_language_filter("cs")
    assert alert.event == "Silný vítr"
    assert alert.severity == "Severe"
    assert alert.language == "cs"

    # With English filter, should get English info
    alert.set_language_filter("en")
    assert alert.event == "Strong Wind"
    assert alert.severity == "Severe"
    assert alert.language == "en"


def test_language_filter_no_matching_language():
    """Test language filter falls back to first info when no language matches."""
    no_match_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-NO-MATCH-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Czech Alert</event>
            <severity>Minor</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>en</language>
            <event>English Alert</event>
            <severity>Moderate</severity>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(no_match_xml)
    alert = alerts[0]

    # With filter for language that doesn't exist, should fall back to first info
    alert.set_language_filter("fr")
    assert alert.event == "Czech Alert"
    assert alert.severity == "Minor"
    assert alert.language == "cs"


def test_get_actionable_info_blocks():
    """Test filtering of actionable info blocks (excluding 'no warning' alerts)."""
    mixed_alerts_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-ACTIONABLE-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Žádná výstraha před teplotou</event>
            <severity>Minor</severity>
            <certainty>Unlikely</certainty>
            <urgency>Immediate</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>cs</language>
            <event>Silný mráz</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <urgency>Future</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>cs</language>
            <event>Žádný výhled nebezpečných jevů</event>
            <severity>Minor</severity>
            <certainty>Unlikely</certainty>
            <urgency>Immediate</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>en</language>
            <event>Minor Temperature Warning</event>
            <severity>Minor</severity>
            <certainty>Unlikely</certainty>
            <urgency>Past</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(mixed_alerts_xml)
    assert len(alerts) == 1
    alert = alerts[0]

    # Get actionable info blocks for Czech language
    actionable = alert.get_actionable_info_blocks("cs")

    # Should only return the "Silný mráz" alert, filtering out:
    # - "Žádná výstraha" (no warning)
    # - "Žádný výhled" (no outlook)
    # - Past urgency alerts
    # - English alerts (when filtering for Czech)
    assert len(actionable) == 1
    assert actionable[0].get("event") == "Silný mráz"
    assert actionable[0].get("severity") == "Moderate"


def test_get_actionable_info_blocks_with_parameters():
    """Test that actionable info blocks include parameters."""
    alerts_with_params_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-PARAMS-001</identifier>
        <sender>chmi@chmi.cz</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Silný mráz</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <urgency>Future</urgency>
            <parameter>
                <valueName>awareness_type</valueName>
                <value>6; low-temperature</value>
            </parameter>
            <parameter>
                <valueName>awareness_level</valueName>
                <value>2; yellow; Moderate</value>
            </parameter>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(alerts_with_params_xml)
    alert = alerts[0]

    actionable = alert.get_actionable_info_blocks("cs")
    assert len(actionable) == 1

    # Check that parameters are included
    params = actionable[0].get("parameters", {})
    assert "awareness_type" in params
    assert params["awareness_type"] == "6; low-temperature"
    assert "awareness_level" in params
    assert params["awareness_level"] == "2; yellow; Moderate"


def test_get_actionable_info_blocks_filters_past_urgency():
    """Test that past urgency alerts are filtered out."""
    past_alert_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-PAST-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Some Alert</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <urgency>Past</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>cs</language>
            <event>Current Alert</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <urgency>Immediate</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(past_alert_xml)
    alert = alerts[0]

    actionable = alert.get_actionable_info_blocks("cs")

    # Should only get the current alert, not the past one
    assert len(actionable) == 1
    assert actionable[0].get("event") == "Current Alert"
    assert actionable[0].get("urgency") == "Immediate"


def test_get_actionable_info_blocks_no_language_filter():
    """Test actionable info blocks without language filter."""
    multi_lang_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>TEST-NOLANG-FILTER-001</identifier>
        <sender>test@example.com</sender>
        <sent>2026-01-05T10:00:00+00:00</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>cs</language>
            <event>Silný mráz</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <urgency>Future</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>en</language>
            <event>Heavy Frost</event>
            <severity>Moderate</severity>
            <certainty>Likely</certainty>
            <urgency>Future</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
        <info>
            <language>cs</language>
            <event>Žádná výstraha</event>
            <severity>Minor</severity>
            <certainty>Unlikely</certainty>
            <urgency>Immediate</urgency>
            <area>
                <areaDesc>Test Area</areaDesc>
            </area>
        </info>
    </alert>
    """

    alerts = parse_cap_xml(multi_lang_xml)
    alert = alerts[0]

    # Without language filter, should get both Czech and English actionable alerts
    actionable = alert.get_actionable_info_blocks(None)

    # Should get Czech and English alerts, but not the "no warning"
    assert len(actionable) == 2
    events = [info.get("event") for info in actionable]
    assert "Silný mráz" in events
    assert "Heavy Frost" in events
    assert "Žádná výstraha" not in events
