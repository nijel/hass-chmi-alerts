"""Sensor platform for CAP Alerts integration.

NOTE: This platform is NOT ENABLED by default and NOT RECOMMENDED for new installations.

The integration uses binary_sensor with MeteoalarmCard's 'meteoalarm' integration format,
which is a better fit for CAP alerts as it uses native awareness_level and awareness_type
parameters from the CAP XML.

This sensor platform provides compatibility with MeteoalarmCard's 'weatheralerts' integration
format. However, this requires appending English severity keywords (Advisory/Watch/Warning)
to event names, which is a workaround for non-English alerts.

To enable this platform (not recommended), modify __init__.py to include Platform.SENSOR
in PLATFORMS.

For new installations, use binary_sensor with meteoalarm integration instead.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_AREA,
    ATTR_CATEGORY,
    ATTR_CERTAINTY,
    ATTR_DESCRIPTION,
    ATTR_EFFECTIVE,
    ATTR_EVENT,
    ATTR_EXPIRES,
    ATTR_HEADLINE,
    ATTR_INSTRUCTION,
    ATTR_RESPONSE_TYPE,
    ATTR_SENDER,
    ATTR_SEVERITY,
    ATTR_URGENCY,
    AWARENESS_ICONS,
    AWARENESS_LEVEL_GREEN,
    AWARENESS_LEVEL_ORANGE,
    AWARENESS_LEVEL_RED,
    AWARENESS_LEVEL_YELLOW,
    DOMAIN,
    EVENT_TYPE_METEOALARM,
    SEVERITY_TO_AWARENESS,
)
from .coordinator import CAPAlertsCoordinator

_LOGGER = logging.getLogger(__name__)

# Mapping from our internal severity levels to weatheralerts severity format
SEVERITY_TO_WEATHERALERTS = {
    "Minor": "Advisory",
    "Moderate": "Watch",
    "Severe": "Warning",
    "Extreme": "Warning",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CAP Alerts sensor from a config entry."""
    coordinator: CAPAlertsCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a sensor
    async_add_entities([CAPAlertsSensor(coordinator, entry)])


class CAPAlertsSensor(CoordinatorEntity[CAPAlertsCoordinator], SensorEntity):
    """Sensor showing CAP alerts with weatheralerts compatibility."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "alerts"

    # Priority order for awareness levels: red > orange > yellow > green
    _LEVEL_PRIORITY = {
        AWARENESS_LEVEL_RED: 4,
        AWARENESS_LEVEL_ORANGE: 3,
        AWARENESS_LEVEL_YELLOW: 2,
        AWARENESS_LEVEL_GREEN: 1,
    }

    def __init__(
        self,
        coordinator: CAPAlertsCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alert"
        self._attr_name = "Alert"

    def _get_highest_awareness_level(self) -> str:
        """Get the highest awareness level from active alerts."""
        if not self.coordinator.data:
            return AWARENESS_LEVEL_GREEN

        highest_level = AWARENESS_LEVEL_GREEN
        highest_priority = 0

        # Check all actionable info blocks from all alerts
        for alert in self.coordinator.data:
            actionable_infos = alert.get_actionable_info_blocks(
                self.coordinator.language_filter
            )
            for info in actionable_infos:
                severity = info.get("severity", "")
                awareness = SEVERITY_TO_AWARENESS.get(severity, AWARENESS_LEVEL_GREEN)
                priority = self._LEVEL_PRIORITY.get(awareness, 0)
                if priority > highest_priority:
                    highest_priority = priority
                    highest_level = awareness

        return highest_level

    def _get_meteoalarm_event_type(
        self, event: str, parameters: dict[str, str] | None = None
    ) -> str:
        """Convert CAP event type to MeteoalarmCard format.

        Returns event in format "N; EventName" where N is the event type ID.
        First checks if awareness_type is provided in parameters, then falls back
        to deriving from event text.

        Args:
            event: Event description text
            parameters: Optional parameters dict that may contain awareness_type

        Returns:
            Event type in MeteoalarmCard format (e.g., "6; Low Temperature")

        """
        # First, check if awareness_type is provided in parameters
        # Some feeds (like CHMI) provide this directly
        if parameters and "awareness_type" in parameters:
            awareness_type = parameters["awareness_type"]
            # The awareness_type is already in the correct format
            # e.g., "6; low-temperature" - just capitalize properly
            if ";" in awareness_type:
                parts = awareness_type.split(";", 1)
                if len(parts) == 2:
                    type_id = parts[0].strip()
                    type_name = parts[1].strip()
                    # Capitalize the type name: "low-temperature" -> "Low-Temperature"
                    type_name_formatted = (
                        type_name.replace("-", " ").title().replace(" ", "-")
                    )
                    return f"{type_id}; {type_name_formatted}"

        # Fall back to deriving from event text
        if not event:
            return "1; Wind"  # Default fallback

        # Try exact match first
        if event in EVENT_TYPE_METEOALARM:
            return EVENT_TYPE_METEOALARM[event]

        # Try partial match (case insensitive)
        event_lower = event.lower()
        for key, value in EVENT_TYPE_METEOALARM.items():
            if key.lower() in event_lower or event_lower in key.lower():
                return value

        # Fallback based on keywords
        # NOTE: Order matters - check more specific conditions (rain without flood) before general ones
        if "flood" in event_lower:
            # Check flood first since it's more specific
            return "12; Flooding"
        if "rain" in event_lower:
            return "10; Rain"
        if any(word in event_lower for word in ["wind", "storm", "gale"]):
            return "1; Wind"
        if any(word in event_lower for word in ["snow", "ice", "winter"]):
            return "2; Snow/Ice"
        if any(word in event_lower for word in ["thunder", "lightning"]):
            return "3; Thunderstorm"
        if "fog" in event_lower:
            return "4; Fog"
        if any(word in event_lower for word in ["heat", "hot", "high temp"]):
            return "5; High Temperature"
        if any(
            word in event_lower
            for word in ["cold", "freeze", "frost", "low temp", "mráz"]
        ):
            return "6; Low Temperature"
        if any(word in event_lower for word in ["coastal", "sea", "tide"]):
            return "7; Coastal Event"
        if "fire" in event_lower:
            return "8; Forest Fire"
        if any(word in event_lower for word in ["avalanche", "snow slide"]):
            return "9; Avalanches"
        # Generic fallback - use wind as most common
        return "1; Wind"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor - number of active alerts."""
        if not self.coordinator.data:
            return 0

        # Count all actionable info blocks from all alerts
        alert_count = 0
        for alert in self.coordinator.data:
            actionable_infos = alert.get_actionable_info_blocks(
                self.coordinator.language_filter
            )
            alert_count += len(actionable_infos)

        return alert_count

    @property
    def icon(self) -> str:
        """Return the icon based on awareness level."""
        awareness_level = self._get_highest_awareness_level()
        return AWARENESS_ICONS.get(awareness_level, "mdi:alert")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {
                "integration": "weatheralerts",
                "alerts": [],
            }

        # Collect all actionable info blocks from all alerts
        # This handles cases where a single alert has multiple info blocks
        # representing different weather phenomena
        all_actionable_infos = []
        for alert in self.coordinator.data:
            actionable_infos = alert.get_actionable_info_blocks(
                self.coordinator.language_filter
            )
            all_actionable_infos.extend((alert, info) for info in actionable_infos)

        # If no actionable alerts, return empty
        if not all_actionable_infos:
            return {
                "integration": "weatheralerts",
                "alerts": [],
            }

        # Build weatheralerts-compatible alerts array
        # Each alert needs: event, severity, title
        weatheralerts_alerts = []
        for _alert, info in all_actionable_infos:
            severity = info.get("severity", "")
            event = info.get("event", "")
            headline = info.get("headline", "")

            # Convert severity to weatheralerts format (Advisory, Watch, Warning)
            weatheralerts_severity = SEVERITY_TO_WEATHERALERTS.get(severity, "Advisory")

            # Create weatheralerts-compatible alert object
            # The 'event' field should contain just the event type
            # Severity is separate to avoid redundancy
            weatheralerts_alert = {
                "event": event or "Unknown Event",
                "severity": weatheralerts_severity,
                "title": headline or event or "Weather Alert",
            }
            weatheralerts_alerts.append(weatheralerts_alert)

        # Also build detailed alerts for additional information
        alerts_details = []
        for alert, info in all_actionable_infos:
            severity = info.get("severity", "")

            # Get parameters and use awareness_type if available
            parameters = info.get("parameters", {})
            event = info.get("event", "")
            meteoalarm_type = self._get_meteoalarm_event_type(event, parameters)

            # Collect area names from this info block
            area_names = []
            for area in info.get("areas", []):
                area_name = area.get("areaDesc", "")
                if area_name and area_name not in area_names:
                    area_names.append(area_name)

            alert_info = {
                "identifier": alert.identifier,
                ATTR_HEADLINE: info.get("headline", ""),
                ATTR_DESCRIPTION: info.get("description", ""),
                ATTR_SEVERITY: severity,
                ATTR_URGENCY: info.get("urgency", ""),
                ATTR_CERTAINTY: info.get("certainty", ""),
                ATTR_EVENT: event,
                ATTR_EFFECTIVE: info.get("effective", ""),
                ATTR_EXPIRES: info.get("expires", ""),
                ATTR_SENDER: alert.sender,
                ATTR_INSTRUCTION: info.get("instruction", ""),
                ATTR_CATEGORY: info.get("category", ""),
                ATTR_RESPONSE_TYPE: (
                    info.get("responseType", [""])[0]
                    if isinstance(info.get("responseType"), list)
                    else info.get("responseType", "")
                ),
                ATTR_AREA: ", ".join(area_names),
                "awareness_type": meteoalarm_type,
            }
            alerts_details.append(alert_info)

        return {
            "integration": "weatheralerts",
            "alerts": weatheralerts_alerts,
            "alerts_detailed": alerts_details,
        }
