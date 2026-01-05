"""CAP (Common Alerting Protocol) XML parser."""
from __future__ import annotations

import logging
from typing import Any
import xml.etree.ElementTree as ET

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

    @property
    def headline(self) -> str:
        """Return first headline from info."""
        if self.info:
            return self.info[0].get("headline", "")
        return ""

    @property
    def description(self) -> str:
        """Return first description from info."""
        if self.info:
            return self.info[0].get("description", "")
        return ""

    @property
    def severity(self) -> str:
        """Return first severity from info."""
        if self.info:
            return self.info[0].get("severity", "")
        return ""

    @property
    def urgency(self) -> str:
        """Return first urgency from info."""
        if self.info:
            return self.info[0].get("urgency", "")
        return ""

    @property
    def certainty(self) -> str:
        """Return first certainty from info."""
        if self.info:
            return self.info[0].get("certainty", "")
        return ""

    @property
    def event(self) -> str:
        """Return first event from info."""
        if self.info:
            return self.info[0].get("event", "")
        return ""

    @property
    def effective(self) -> str:
        """Return first effective time from info."""
        if self.info:
            return self.info[0].get("effective", "")
        return ""

    @property
    def expires(self) -> str:
        """Return first expires time from info."""
        if self.info:
            return self.info[0].get("expires", "")
        return ""

    @property
    def instruction(self) -> str:
        """Return first instruction from info."""
        if self.info:
            return self.info[0].get("instruction", "")
        return ""

    @property
    def category(self) -> str:
        """Return first category from info."""
        if self.info:
            return self.info[0].get("category", "")
        return ""

    @property
    def response_type(self) -> str:
        """Return first response type from info."""
        if self.info:
            return self.info[0].get("responseType", "")
        return ""

    @property
    def areas(self) -> list[str]:
        """Return list of area names from all info sections."""
        area_names = []
        for info_item in self.info:
            for area in info_item.get("areas", []):
                area_name = area.get("areaDesc", "")
                if area_name and area_name not in area_names:
                    area_names.append(area_name)
        return area_names

    def matches_area(self, area_filter: str | None) -> bool:
        """Check if alert matches area filter."""
        if not area_filter:
            return True
        area_filter_lower = area_filter.lower()
        return any(area_filter_lower in area.lower() for area in self.areas)


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
        "responseType",
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
    ]:
        elem = info_elem.find(f"{ns}{field}")
        if elem is not None and elem.text:
            info_data[field] = elem.text.strip()
    
    # Parse areas
    areas = []
    for area_elem in info_elem.findall(f"{ns}area"):
        area_data: dict[str, Any] = {}
        
        area_desc = area_elem.find(f"{ns}areaDesc")
        if area_desc is not None and area_desc.text:
            area_data["areaDesc"] = area_desc.text.strip()
        
        # Parse geocodes
        geocodes = {}
        for geocode in area_elem.findall(f"{ns}geocode"):
            value_name = geocode.find(f"{ns}valueName")
            value = geocode.find(f"{ns}value")
            if value_name is not None and value is not None:
                if value_name.text and value.text:
                    geocodes[value_name.text.strip()] = value.text.strip()
        
        if geocodes:
            area_data["geocode"] = geocodes
        
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
