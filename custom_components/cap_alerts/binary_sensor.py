"""Binary sensor platform for CAP Alerts integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_AREA,
    ATTR_AWARENESS_LEVEL,
    ATTR_AWARENESS_TYPE,
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
    AWARENESS_LEVEL_METEOALARM,
    AWARENESS_LEVEL_ORANGE,
    AWARENESS_LEVEL_RED,
    AWARENESS_LEVEL_YELLOW,
    DOMAIN,
    EVENT_TYPE_METEOALARM,
    SEVERITY_TO_AWARENESS,
)
from .coordinator import CAPAlertsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CAP Alerts binary sensor from a config entry."""
    coordinator: CAPAlertsCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a binary sensor
    async_add_entities([CAPAlertsBinarySensor(coordinator, entry)])


class CAPAlertsBinarySensor(
    CoordinatorEntity[CAPAlertsCoordinator], BinarySensorEntity
):
    """Binary sensor showing CAP alerts with meteoalarm compatibility."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.SAFETY

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
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool:
        """Return True if alerts are active."""
        awareness_level = self._get_highest_awareness_level()
        return awareness_level != AWARENESS_LEVEL_GREEN

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
                ATTR_AWARENESS_LEVEL: AWARENESS_LEVEL_METEOALARM[AWARENESS_LEVEL_GREEN],
                ATTR_AWARENESS_TYPE: None,
                "alert_count": 0,
                "attribution": "Information provided by MeteoAlarm",
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

        # If no actionable alerts, return green status
        if not all_actionable_infos:
            return {
                ATTR_AWARENESS_LEVEL: AWARENESS_LEVEL_METEOALARM[AWARENESS_LEVEL_GREEN],
                ATTR_AWARENESS_TYPE: None,
                "alert_count": 0,
                "attribution": "Information provided by MeteoAlarm",
            }

        # Find the info block with highest severity
        highest_info = None
        highest_priority = 0

        for _alert, info in all_actionable_infos:
            severity = info.get("severity", "")
            awareness = SEVERITY_TO_AWARENESS.get(severity, AWARENESS_LEVEL_GREEN)
            priority = self._LEVEL_PRIORITY.get(awareness, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_info = info

        # Build details for all actionable alerts
        alerts_details = []
        for alert, info in all_actionable_infos:
            severity = info.get("severity", "")
            awareness_level = SEVERITY_TO_AWARENESS.get(severity, AWARENESS_LEVEL_GREEN)
            meteoalarm_level = AWARENESS_LEVEL_METEOALARM[awareness_level]

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
                ATTR_AWARENESS_LEVEL: meteoalarm_level,
                ATTR_AWARENESS_TYPE: meteoalarm_type,
            }
            alerts_details.append(alert_info)

        # Get highest awareness level in MeteoalarmCard format
        highest_severity = highest_info.get("severity", "") if highest_info else ""
        highest_awareness_level = SEVERITY_TO_AWARENESS.get(
            highest_severity, AWARENESS_LEVEL_GREEN
        )
        meteoalarm_awareness_level = AWARENESS_LEVEL_METEOALARM[highest_awareness_level]

        # Get awareness_type for highest alert
        highest_params = highest_info.get("parameters", {}) if highest_info else {}
        highest_event = highest_info.get("event", "") if highest_info else ""
        meteoalarm_awareness_type = self._get_meteoalarm_event_type(
            highest_event, highest_params
        )

        return {
            ATTR_AWARENESS_LEVEL: meteoalarm_awareness_level,
            ATTR_AWARENESS_TYPE: meteoalarm_awareness_type,
            "alert_count": len(all_actionable_infos),
            "alerts": alerts_details,
            "attribution": "Information provided by MeteoAlarm",
        }
