"""Test the CHMI Alerts config flow."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from homeassistant.data_entry_flow import FlowResultType

from custom_components.chmi_alerts.config_flow import CHMIAlertsConfigFlow
from custom_components.chmi_alerts.const import (
    CONF_AREA_FILTER,
    CONF_LANGUAGE_FILTER,
)

# Enable asyncio for all tests in this module
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock()
    hass.config = Mock()
    hass.config.language = "en"
    return hass


def get_language_default_from_schema(schema):
    """Extract the default language value from the data schema.

    Helper function to inspect the voluptuous schema and find the default
    value for the language filter field.
    """
    for key in schema:
        if hasattr(key, "schema") and key.schema == CONF_LANGUAGE_FILTER:
            return key.default()
    return None


async def test_form_default_english(mock_hass):
    """Test the form with default English language."""
    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass

    # Show the initial form
    result = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Check that the default language is English when HA language is English
    default_language = get_language_default_from_schema(result["data_schema"].schema)
    assert default_language == "en"


async def test_form_default_czech(mock_hass):
    """Test the form with default Czech language."""
    mock_hass.config.language = "cs"

    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass

    # Show the initial form
    result = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Check that the default language is Czech when HA language is Czech
    default_language = get_language_default_from_schema(result["data_schema"].schema)
    assert default_language == "cs"


async def test_form_create_entry():
    """Test creating an entry with user input."""
    mock_hass = Mock()
    mock_hass.config = Mock()
    mock_hass.config.language = "en"

    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass

    # Provide user input with a CISORP code
    user_input = {
        CONF_AREA_FILTER: "1000",  # Prague CISORP code
        CONF_LANGUAGE_FILTER: "cs",
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Praha"  # Location name for code 1000
    assert result["data"] == user_input
    assert result["data"][CONF_LANGUAGE_FILTER] == "cs"


async def test_form_create_entry_no_area_filter():
    """Test creating an entry without area filter."""
    mock_hass = Mock()
    mock_hass.config = Mock()
    mock_hass.config.language = "cs"

    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass

    # Provide user input without area filter (empty string for all locations)
    user_input = {
        CONF_AREA_FILTER: "",
        CONF_LANGUAGE_FILTER: "en",
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "CHMI Alerts"
    assert result["data"] == user_input
    assert result["data"][CONF_LANGUAGE_FILTER] == "en"
