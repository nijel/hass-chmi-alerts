"""Constants for the CAP Alerts integration."""

DOMAIN = "cap_alerts"

# Configuration
CONF_FEED_URL = "feed_url"
CONF_AREA_FILTER = "area_filter"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_CHMI_URL = "https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml"

# Attributes
ATTR_HEADLINE = "headline"
ATTR_DESCRIPTION = "description"
ATTR_SEVERITY = "severity"
ATTR_URGENCY = "urgency"
ATTR_CERTAINTY = "certainty"
ATTR_AREA = "area"
ATTR_EFFECTIVE = "effective"
ATTR_EXPIRES = "expires"
ATTR_EVENT = "event"
ATTR_SENDER = "sender"
ATTR_INSTRUCTION = "instruction"
ATTR_CATEGORY = "category"
ATTR_RESPONSE_TYPE = "response_type"
ATTR_AWARENESS_LEVEL = "awareness_level"
ATTR_AWARENESS_TYPE = "awareness_type"

# Awareness levels (compatible with meteoalarm)
AWARENESS_LEVEL_GREEN = "green"
AWARENESS_LEVEL_YELLOW = "yellow"
AWARENESS_LEVEL_ORANGE = "orange"
AWARENESS_LEVEL_RED = "red"

# CAP Severity to awareness level mapping
# Maps CAP severity levels to meteoalarm-compatible awareness levels:
# - Minor: Yellow (Be aware)
# - Moderate/Severe: Orange (Be prepared)
# - Extreme: Red (Take action)
SEVERITY_TO_AWARENESS = {
    "Minor": AWARENESS_LEVEL_YELLOW,
    "Moderate": AWARENESS_LEVEL_ORANGE,
    "Severe": AWARENESS_LEVEL_ORANGE,
    "Extreme": AWARENESS_LEVEL_RED,
}

# Icons for awareness levels
AWARENESS_ICONS = {
    AWARENESS_LEVEL_GREEN: "mdi:check-circle",
    AWARENESS_LEVEL_YELLOW: "mdi:alert",
    AWARENESS_LEVEL_ORANGE: "mdi:alert-circle",
    AWARENESS_LEVEL_RED: "mdi:alert-octagon",
}

# MeteoalarmCard-compatible awareness level format
# Format: "level_id; Color" where level_id is 2-4
AWARENESS_LEVEL_METEOALARM = {
    AWARENESS_LEVEL_GREEN: "1; Green",
    AWARENESS_LEVEL_YELLOW: "2; Yellow",
    AWARENESS_LEVEL_ORANGE: "3; Orange",
    AWARENESS_LEVEL_RED: "4; Red",
}

# Common CAP event types to Meteoalarm event type mapping
# Meteoalarm uses numeric event types (1-13, ID 11 is reserved/unused): https://meteoalarm.org/
# Format: event type ID from 1-13
EVENT_TYPE_METEOALARM = {
    # Weather events
    "Wind": "1; Wind",
    "Snow": "2; Snow/Ice",
    "Ice": "2; Snow/Ice",
    "Snow/Ice": "2; Snow/Ice",
    "Thunderstorm": "3; Thunderstorm",
    "Thunderstorms": "3; Thunderstorm",
    "Fog": "4; Fog",
    "High Temperature": "5; High Temperature",
    "Heat": "5; High Temperature",
    "Low Temperature": "6; Low Temperature",
    "Cold": "6; Low Temperature",
    "Coastal Event": "7; Coastal Event",
    "Forest Fire": "8; Forest Fire",
    "Fire": "8; Forest Fire",
    "Avalanche": "9; Avalanches",
    "Avalanches": "9; Avalanches",
    "Rain": "10; Rain",
    "Flooding": "12; Flooding",
    "Flood": "12; Flooding",
    "Rain-Flood": "13; Rain-Flood",
}
