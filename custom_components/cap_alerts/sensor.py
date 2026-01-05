"""Sensor platform for CAP Alerts integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .cap_parser import CAPAlert
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
    DOMAIN,
)
from .coordinator import CAPAlertsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up CAP Alerts sensors from a config entry."""
    coordinator: CAPAlertsCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a summary sensor
    async_add_entities([CAPAlertsSummarySensor(coordinator, entry)])


class CAPAlertsSummarySensor(CoordinatorEntity[CAPAlertsCoordinator], SensorEntity):
    """Sensor showing the count of active CAP alerts."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CAPAlertsCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alert_count"
        self._attr_name = "Alert count"
        self._attr_icon = "mdi:alert"

    @property
    def native_value(self) -> int:
        """Return the number of active alerts."""
        if self.coordinator.data is None:
            return 0
        return len(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        # Include details of all active alerts
        alerts_details = []
        for alert in self.coordinator.data:
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
            }
            alerts_details.append(alert_info)

        return {
            "alerts": alerts_details,
        }
