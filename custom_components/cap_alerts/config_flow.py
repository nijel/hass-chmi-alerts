"""Config flow for CAP Alerts integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_AREA_FILTER,
    CONF_FEED_URL,
    CONF_LANGUAGE_FILTER,
    CONF_SCAN_INTERVAL,
    DEFAULT_CHMI_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class CAPAlertsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CAP Alerts."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the feed URL can be accessed
            # For now, we'll just accept any input
            # You could add URL validation here
            
            # Create a unique ID based on the feed URL
            await self.async_set_unique_id(user_input[CONF_FEED_URL])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input.get(CONF_AREA_FILTER, "CAP Alerts"),
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_FEED_URL, default=DEFAULT_CHMI_URL): cv.string,
                vol.Optional(CONF_AREA_FILTER): cv.string,
                vol.Optional(CONF_LANGUAGE_FILTER): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
