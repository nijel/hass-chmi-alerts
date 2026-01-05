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

        for alert in self.coordinator.data:
            awareness = SEVERITY_TO_AWARENESS.get(alert.severity, AWARENESS_LEVEL_GREEN)
            priority = self._LEVEL_PRIORITY.get(awareness, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_level = awareness

        return highest_level

    def _get_meteoalarm_event_type(self, event: str) -> str:
        """Convert CAP event type to MeteoalarmCard format.

        Returns event in format "N; EventName" where N is the event type ID.
        Falls back to generic event if no specific mapping exists.
        """
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
        if any(word in event_lower for word in ["cold", "freeze", "low temp"]):
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
            }

        # Get the alert with the highest severity
        highest_alert = None
        highest_priority = 0

        for alert in self.coordinator.data:
            awareness = SEVERITY_TO_AWARENESS.get(alert.severity, AWARENESS_LEVEL_GREEN)
            priority = self._LEVEL_PRIORITY.get(awareness, 0)
            if priority > highest_priority:
                highest_priority = priority
                highest_alert = alert

        # Include details of all active alerts
        alerts_details = []
        for alert in self.coordinator.data:
            awareness_level = SEVERITY_TO_AWARENESS.get(
                alert.severity, AWARENESS_LEVEL_GREEN
            )
            meteoalarm_level = AWARENESS_LEVEL_METEOALARM[awareness_level]
            meteoalarm_type = self._get_meteoalarm_event_type(alert.event)

            alert_info = {
                "identifier": alert.identifier,
                ATTR_HEADLINE: alert.headline,
                ATTR_DESCRIPTION: alert.description,
                ATTR_SEVERITY: alert.severity,
                ATTR_URGENCY: alert.urgency,
                ATTR_CERTAINTY: alert.certainty,
                ATTR_EVENT: alert.event,
                ATTR_EFFECTIVE: alert.effective,
                ATTR_EXPIRES: alert.expires,
                ATTR_SENDER: alert.sender,
                ATTR_INSTRUCTION: alert.instruction,
                ATTR_CATEGORY: alert.category,
                ATTR_RESPONSE_TYPE: alert.response_type,
                ATTR_AREA: ", ".join(alert.areas),
                ATTR_AWARENESS_LEVEL: meteoalarm_level,
                ATTR_AWARENESS_TYPE: meteoalarm_type,
            }
            alerts_details.append(alert_info)

        # Get highest awareness level in MeteoalarmCard format
        highest_awareness_level = self._get_highest_awareness_level()
        meteoalarm_awareness_level = AWARENESS_LEVEL_METEOALARM[highest_awareness_level]
        meteoalarm_awareness_type = self._get_meteoalarm_event_type(
            highest_alert.event if highest_alert else ""
        )

        return {
            ATTR_AWARENESS_LEVEL: meteoalarm_awareness_level,
            ATTR_AWARENESS_TYPE: meteoalarm_awareness_type,
            "alert_count": len(self.coordinator.data),
            "alerts": alerts_details,
        }
