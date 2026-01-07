"""Config flow for CHMI Alerts integration."""

from __future__ import annotations

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_AREA_FILTER,
    CONF_LANGUAGE_FILTER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class CHMIAlertsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CHMI Alerts."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create a unique ID for CHMI alerts
            # Since we only support one CHMI feed, we can use a static ID
            # but allow multiple instances with different area filters
            unique_id = f"chmi_{user_input.get(CONF_AREA_FILTER, 'all')}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input.get(CONF_AREA_FILTER) or "CHMI Alerts",
                data=user_input,
            )

        # Pre-select language based on Home Assistant configuration
        # Default to Czech if Home Assistant is using Czech language, English otherwise
        default_language = "en"
        if self.hass.config.language == "cs":
            default_language = "cs"

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_AREA_FILTER): cv.string,
                vol.Optional(
                    CONF_LANGUAGE_FILTER, default=default_language
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["cs", "en"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key=CONF_LANGUAGE_FILTER,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
