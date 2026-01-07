"""Config flow for CHMI Alerts integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CISORP_LOCATIONS,
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
            # Create entry without unique_id check (allow multiple instances)
            return self.async_create_entry(
                title=user_input.get(CONF_AREA_FILTER) or "CHMI Alerts",
                data=user_input,
            )

        # Pre-select language based on Home Assistant configuration
        # Default to Czech if Home Assistant is using Czech language, English otherwise
        default_language = "en"
        if self.hass.config.language == "cs":
            default_language = "cs"

        # Build location options for the selector
        location_options = [
            selector.SelectOptionDict(value="", label="All locations (no filter)")
        ]
        for code, name in CISORP_LOCATIONS:
            location_options.append(
                selector.SelectOptionDict(value=code, label=f"{name} ({code})")
            )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_AREA_FILTER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=location_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_LANGUAGE_FILTER, default=default_language
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value="cs", label="Czech"),
                            selector.SelectOptionDict(value="en", label="English"),
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
