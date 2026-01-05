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
