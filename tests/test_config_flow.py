"""Test the CHMI Alerts config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.chmi_alerts.config_flow import CHMIAlertsConfigFlow
from custom_components.chmi_alerts.const import (
    CONF_AREA_FILTER,
    CONF_LANGUAGE_FILTER,
    DOMAIN,
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


async def test_form_default_english(mock_hass):
    """Test the form with default English language."""
    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass

    # Show the initial form
    result = await flow.async_step_user()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    
    # Check that the default language is English when HA language is English
    schema_keys = result["data_schema"].schema.keys()
    # Find the language filter key and check its default
    for key in schema_keys:
        if hasattr(key, 'schema') and key.schema == CONF_LANGUAGE_FILTER:
            # The default should be "en"
            assert key.default() == "en"
            break
    else:
        pytest.fail("Language filter key not found in schema")


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
    schema_keys = result["data_schema"].schema.keys()
    # Find the language filter key and check its default
    for key in schema_keys:
        if hasattr(key, 'schema') and key.schema == CONF_LANGUAGE_FILTER:
            # The default should be "cs"
            assert key.default() == "cs"
            break
    else:
        pytest.fail("Language filter key not found in schema")


async def test_form_create_entry():
    """Test creating an entry with user input."""
    mock_hass = Mock()
    mock_hass.config = Mock()
    mock_hass.config.language = "en"
    
    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass
    
    # Mock the async_set_unique_id method
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = Mock()

    # Provide user input
    user_input = {
        CONF_AREA_FILTER: "Prague",
        CONF_LANGUAGE_FILTER: "cs",
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Prague"
    assert result["data"] == user_input
    assert result["data"][CONF_LANGUAGE_FILTER] == "cs"


async def test_form_create_entry_no_area_filter():
    """Test creating an entry without area filter."""
    mock_hass = Mock()
    mock_hass.config = Mock()
    mock_hass.config.language = "cs"
    
    flow = CHMIAlertsConfigFlow()
    flow.hass = mock_hass
    
    # Mock the async_set_unique_id method
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = Mock()

    # Provide user input without area filter
    user_input = {
        CONF_LANGUAGE_FILTER: "en",
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "CHMI Alerts"
    assert result["data"] == user_input
    assert result["data"][CONF_LANGUAGE_FILTER] == "en"
