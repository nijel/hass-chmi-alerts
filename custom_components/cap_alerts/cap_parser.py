"""CAP (Common Alerting Protocol) XML parser."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Any

_LOGGER = logging.getLogger(__name__)

# CAP XML namespaces
NAMESPACES = {
    "cap": "urn:oasis:names:tc:emergency:cap:1.2",
    "atom": "http://www.w3.org/2005/Atom",
}


class CAPAlert:
    """Representation of a CAP alert."""

    def __init__(self, alert_data: dict[str, Any]) -> None:
        """Initialize CAP alert."""
        self.data = alert_data
        self._language_filter: str | None = None

    @property
    def identifier(self) -> str:
        """Return alert identifier."""
        return self.data.get("identifier", "")

    @property
    def sender(self) -> str:
        """Return alert sender."""
        return self.data.get("sender", "")

    @property
    def sent(self) -> str:
        """Return when alert was sent."""
        return self.data.get("sent", "")

    @property
    def status(self) -> str:
        """Return alert status."""
        return self.data.get("status", "")

    @property
    def msg_type(self) -> str:
        """Return message type."""
        return self.data.get("msgType", "")

    @property
    def scope(self) -> str:
        """Return alert scope."""
        return self.data.get("scope", "")

    @property
    def info(self) -> list[dict[str, Any]]:
        """Return alert info sections."""
        return self.data.get("info", [])

    def set_language_filter(self, language_filter: str | None) -> None:
        """Set the language filter for this alert.

        This affects which info section is returned by properties like severity, event, etc.
        """
        self._language_filter = language_filter

    def _info_matches_language(self, info_language: str, language_filter: str) -> bool:
        """Check if an info section's language matches the language filter.

        Args:
            info_language: Language code from info section (e.g., 'cs', 'en-GB')
            language_filter: Language filter to match against (e.g., 'cs', 'en')

        Returns:
            True if languages match (exact or prefix match), False otherwise

        """
        if not info_language or not language_filter:
            return False

        info_language_lower = info_language.lower()
        language_filter_lower = language_filter.lower()

        # Exact match or prefix match with hyphen separator
        return (
            info_language_lower == language_filter_lower
            or info_language_lower.startswith(language_filter_lower + "-")
        )

    def _get_preferred_info(self) -> dict[str, Any] | None:
        """Get the preferred info section based on language filter and severity.

        Returns:
            - If language filter is set and matches: the matching info with highest severity
            - If language filter is set but no matches: falls back to first info section
            - If no language filter: the first info section

        """
        if not self.info:
            return None

        # If no language filter, return first info
        if not self._language_filter:
            return self.info[0]

        # Find all info sections matching the language filter
        matching_infos = []

        for info_item in self.info:
            info_language = info_item.get("language", "")
            if info_language and self._info_matches_language(
                info_language, self._language_filter
            ):
                matching_infos.append(info_item)

        # If no matching info found, return first (backward compatibility)
        if not matching_infos:
            return self.info[0]

        # Return the matching info with highest severity
        # Severity priority: Extreme > Severe > Moderate > Minor > Unknown
        severity_order = {
            "Extreme": 4,
            "Severe": 3,
            "Moderate": 2,
            "Minor": 1,
            "Unknown": 0,
        }

        best_info = matching_infos[0]
        best_severity = severity_order.get(best_info.get("severity", ""), 0)

        for info_item in matching_infos[1:]:
            severity = severity_order.get(info_item.get("severity", ""), 0)
            if severity > best_severity:
                best_severity = severity
                best_info = info_item

        return best_info

    @property
    def headline(self) -> str:
        """Return headline from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("headline", "")
        return ""

    @property
    def description(self) -> str:
        """Return description from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("description", "")
        return ""

    @property
    def severity(self) -> str:
        """Return severity from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("severity", "")
        return ""

    @property
    def urgency(self) -> str:
        """Return urgency from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("urgency", "")
        return ""

    @property
    def certainty(self) -> str:
        """Return certainty from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("certainty", "")
        return ""

    @property
    def event(self) -> str:
        """Return event from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("event", "")
        return ""

    @property
    def effective(self) -> str:
        """Return effective time from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("effective", "")
        return ""

    @property
    def expires(self) -> str:
        """Return expires time from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("expires", "")
        return ""

    @property
    def instruction(self) -> str:
        """Return instruction from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("instruction", "")
        return ""

    @property
    def category(self) -> str:
        """Return category from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("category", "")
        return ""

    @property
    def response_type(self) -> str:
        """Return first response type from preferred info section.

        Note: responseType can have multiple values, but this property
        returns only the first one for backward compatibility.
        Use response_types property to get all values.
        """
        info = self._get_preferred_info()
        if info:
            rt = info.get("responseType", "")
            # Handle both list (new format) and string (old format)
            if isinstance(rt, list):
                return rt[0] if rt else ""
            return rt
        return ""

    @property
    def response_types(self) -> list[str]:
        """Return all response types from preferred info section."""
        info = self._get_preferred_info()
        if info:
            rt = info.get("responseType", [])
            # Handle both list (new format) and string (old format)
            if isinstance(rt, list):
                return rt
            # Old format: single string
            return [rt] if rt else []
        return []

    @property
    def language(self) -> str:
        """Return language from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("language", "")
        return ""

    @property
    def audience(self) -> str:
        """Return audience from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("audience", "")
        return ""

    @property
    def sender_name(self) -> str:
        """Return sender name from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("senderName", "")
        return ""

    @property
    def event_code(self) -> dict[str, str]:
        """Return event code from preferred info section."""
        info = self._get_preferred_info()
        if info:
            return info.get("eventCode", {})
        return {}

    @property
    def areas(self) -> list[str]:
        """Return list of area names from all info sections.

        Note: This property aggregates areas from ALL info sections, not just the
        preferred one. This is intentional because different info sections (e.g.,
        different languages) may have different area coverage, and we want to show
        all affected areas for filtering purposes.
        """
        area_names = []
        for info_item in self.info:
            for area in info_item.get("areas", []):
                area_name = area.get("areaDesc", "")
                if area_name and area_name not in area_names:
                    area_names.append(area_name)
        return area_names

    @property
    def geocodes(self) -> list[str]:
        """Return list of all geocode values from all info sections.

        Note: This property aggregates geocodes from ALL info sections, not just the
        preferred one. This is intentional because different info sections (e.g.,
        different languages) may have different area coverage, and we want to show
        all affected geocodes for filtering purposes.
        """
        geocode_values = set()
        for info_item in self.info:
            for area in info_item.get("areas", []):
                geocode_list = area.get("geocode", [])
                for value in geocode_list:
                    if value:
                        geocode_values.add(value)
        return list(geocode_values)

    def matches_area(self, area_filter: str | None) -> bool:
        """Check if alert matches area filter.

        Matches against area descriptions and geocode values.
        """
        if not area_filter:
            return True
        area_filter_lower = area_filter.lower()

        # Check area descriptions
        if any(area_filter_lower in area.lower() for area in self.areas):
            return True

        # Check geocode values
        return any(area_filter_lower in geocode.lower() for geocode in self.geocodes)

    def matches_language(self, language_filter: str | None) -> bool:
        """Check if alert matches language filter.

        Matches against language codes in all info sections.
        Uses exact match or prefix matching where info language starts with filter.

        Examples:
            - 'cs' matches 'cs' or 'cs-CZ'
            - 'cs-CZ' matches only 'cs-CZ' (not 'cs')
            - 'en' does not match 'french' (no false positives)

        """
        if not language_filter:
            return True

        # Check language in all info sections using the helper method
        for info_item in self.info:
            info_language = info_item.get("language", "")
            if self._info_matches_language(info_language, language_filter):
                return True

        return False

    def get_actionable_info_blocks(
        self, language_filter: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all actionable info blocks (excluding 'no warning' alerts).

        Returns info blocks that:
        - Match the language filter (if specified)
        - Are not "no warning" type alerts
        - Have actual warning content (not certainty: Unlikely with severity: Minor)

        Args:
            language_filter: Language code to filter by (e.g., 'cs', 'en')

        Returns:
            List of info dictionaries representing actionable alerts

        """
        actionable_infos = []

        for info_item in self.info:
            # Check language filter
            if language_filter:
                info_language = info_item.get("language", "")
                if not self._info_matches_language(info_language, language_filter):
                    continue

            # Get event text
            event = info_item.get("event", "")

            # Skip "no warning" type alerts
            # Czech: "Žádná výstraha", "Žádný výhled"
            # English: "No ... Warning", "Minor ... Warning" with Unlikely certainty
            if event.startswith("Žádná výstraha") or event.startswith("Žádný výhled"):
                continue

            # Also filter out English "Minor ... Warning" with Unlikely certainty
            # These are placeholder alerts indicating no actual warning
            severity = info_item.get("severity", "")
            certainty = info_item.get("certainty", "")
            urgency = info_item.get("urgency", "")

            if (
                certainty == "Unlikely"
                and severity == "Minor"
                and (event.startswith("Minor ") or event.startswith("No "))
            ):
                continue

            # Skip past alerts
            if urgency == "Past":
                continue

            # This is an actionable alert
            actionable_infos.append(info_item)

        return actionable_infos


def parse_cap_xml(xml_content: str) -> list[CAPAlert]:
    """Parse CAP XML content and return list of alerts."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as err:
        _LOGGER.error("Failed to parse CAP XML: %s", err)
        return []

    alerts = []

    # Check if this is an Atom feed with CAP entries
    if root.tag == "{http://www.w3.org/2005/Atom}feed":
        # Parse Atom feed with CAP entries
        for entry in root.findall("atom:entry", NAMESPACES):
            # Try to find CAP alert in entry content
            content = entry.find("atom:content", NAMESPACES)
            if content is not None:
                # Look for cap:alert within content
                cap_alert = content.find("cap:alert", NAMESPACES)
                if cap_alert is not None:
                    alert_data = _parse_alert_element(cap_alert)
                    if alert_data:
                        alerts.append(CAPAlert(alert_data))
    elif root.tag.endswith("alert"):
        # Direct CAP alert
        alert_data = _parse_alert_element(root)
        if alert_data:
            alerts.append(CAPAlert(alert_data))
    else:
        # Try to find all alert elements
        for alert_elem in root.findall(".//cap:alert", NAMESPACES):
            alert_data = _parse_alert_element(alert_elem)
            if alert_data:
                alerts.append(CAPAlert(alert_data))

    return alerts


def _parse_alert_element(alert_elem: ET.Element) -> dict[str, Any] | None:
    """Parse a single CAP alert element."""
    # Remove namespace for easier processing
    ns = "{urn:oasis:names:tc:emergency:cap:1.2}"

    alert_data: dict[str, Any] = {}

    # Parse basic alert fields
    for field in ["identifier", "sender", "sent", "status", "msgType", "scope"]:
        elem = alert_elem.find(f"{ns}{field}")
        if elem is not None and elem.text:
            alert_data[field] = elem.text.strip()

    # Parse info sections
    info_list = []
    for info_elem in alert_elem.findall(f"{ns}info"):
        info_data = _parse_info_element(info_elem, ns)
        if info_data:
            info_list.append(info_data)

    if info_list:
        alert_data["info"] = info_list

    return alert_data if alert_data else None


def _parse_info_element(info_elem: ET.Element, ns: str) -> dict[str, Any]:
    """Parse CAP info element."""
    info_data: dict[str, Any] = {}

    # Parse simple text fields
    for field in [
        "language",
        "category",
        "event",
        "urgency",
        "severity",
        "certainty",
        "headline",
        "description",
        "instruction",
        "web",
        "contact",
        "effective",
        "onset",
        "expires",
        "audience",
        "senderName",
    ]:
        elem = info_elem.find(f"{ns}{field}")
        if elem is not None and elem.text:
            info_data[field] = elem.text.strip()

    # Parse responseType - can have multiple values
    response_types = [
        rt_elem.text.strip()
        for rt_elem in info_elem.findall(f"{ns}responseType")
        if rt_elem.text
    ]
    if response_types:
        info_data["responseType"] = response_types

    # Parse areas
    areas = []
    for area_elem in info_elem.findall(f"{ns}area"):
        area_data: dict[str, Any] = {}

        area_desc = area_elem.find(f"{ns}areaDesc")
        if area_desc is not None and area_desc.text:
            area_data["areaDesc"] = area_desc.text.strip()

        # Parse geocodes - collect all values (not as dict to avoid overwriting duplicates)
        geocode_values = []
        for geocode in area_elem.findall(f"{ns}geocode"):
            value_name = geocode.find(f"{ns}valueName")
            value = geocode.find(f"{ns}value")
            if value_name is not None and value is not None:
                if value_name.text and value.text:
                    geocode_values.append(value.text.strip())

        if geocode_values:
            area_data["geocode"] = geocode_values

        # Parse polygons and circles if present
        polygon = area_elem.find(f"{ns}polygon")
        if polygon is not None and polygon.text:
            area_data["polygon"] = polygon.text.strip()

        circle = area_elem.find(f"{ns}circle")
        if circle is not None and circle.text:
            area_data["circle"] = circle.text.strip()

        if area_data:
            areas.append(area_data)

    if areas:
        info_data["areas"] = areas

    # Parse eventCode elements
    event_codes = {}
    for ec in info_elem.findall(f"{ns}eventCode"):
        value_name = ec.find(f"{ns}valueName")
        value = ec.find(f"{ns}value")
        if value_name is not None and value is not None:
            if value_name.text and value.text:
                event_codes[value_name.text.strip()] = value.text.strip()

    if event_codes:
        info_data["eventCode"] = event_codes

    # Parse parameters
    parameters = {}
    for param in info_elem.findall(f"{ns}parameter"):
        value_name = param.find(f"{ns}valueName")
        value = param.find(f"{ns}value")
        if value_name is not None and value is not None:
            if value_name.text and value.text:
                parameters[value_name.text.strip()] = value.text.strip()

    if parameters:
        info_data["parameters"] = parameters

    return info_data
