"""The CHMI Alerts integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CHMI_FEED_URL,
    CONF_AREA_FILTER,
    CONF_LANGUAGE_FILTER,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import CAPAlertsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CHMI Alerts from a config entry."""
    area_filter = entry.data.get(CONF_AREA_FILTER)
    language_filter = entry.data.get(CONF_LANGUAGE_FILTER)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL)

    coordinator = CAPAlertsCoordinator(
        hass,
        feed_url=CHMI_FEED_URL,
        area_filter=area_filter,
        language_filter=language_filter,
        scan_interval=scan_interval,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
