"""Test the CHMI Alerts binary sensor."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.chmi_alerts.binary_sensor import CAPAlertsBinarySensor
from custom_components.chmi_alerts.const import CONF_AREA_FILTER

# Enable asyncio for all tests in this module
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = []
    coordinator.language_filter = "en"
    coordinator.hass = Mock()
    coordinator.hass.config = Mock()
    coordinator.hass.config.language = "en"
    return coordinator


@pytest.fixture
def mock_entry_with_area():
    """Create a mock config entry with area filter."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {CONF_AREA_FILTER: "5106"}  # Nový Bor
    return entry


@pytest.fixture
def mock_entry_without_area():
    """Create a mock config entry without area filter."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_id"
    entry.data = {CONF_AREA_FILTER: ""}
    return entry


async def test_entity_name_with_area_english(mock_coordinator, mock_entry_with_area):
    """Test entity name includes location in English."""
    sensor = CAPAlertsBinarySensor(mock_coordinator, mock_entry_with_area)

    assert sensor.name == "Alerts Nový Bor"
    assert sensor.unique_id == "test_entry_id_chmi_alerts_5106"


async def test_entity_name_with_area_czech(mock_coordinator, mock_entry_with_area):
    """Test entity name includes location in Czech."""
    # Set coordinator language to Czech
    mock_coordinator.hass.config.language = "cs"

    sensor = CAPAlertsBinarySensor(mock_coordinator, mock_entry_with_area)

    assert sensor.name == "Výstrahy Nový Bor"
    assert sensor.unique_id == "test_entry_id_chmi_alerts_5106"


async def test_entity_name_without_area(mock_coordinator, mock_entry_without_area):
    """Test entity name without area filter uses translation key."""
    sensor = CAPAlertsBinarySensor(mock_coordinator, mock_entry_without_area)

    # When no area is specified, name should be None and translation_key should be set
    assert sensor.name is None
    assert sensor._attr_translation_key == "alert"  # noqa: SLF001
    assert sensor.unique_id == "test_entry_id_chmi_alerts"


async def test_entity_unique_id_format(mock_coordinator):
    """Test entity unique_id format."""
    # Test with Prague (code 1000)
    entry_prague = Mock(spec=ConfigEntry)
    entry_prague.entry_id = "entry_1"
    entry_prague.data = {CONF_AREA_FILTER: "1000"}

    sensor_prague = CAPAlertsBinarySensor(mock_coordinator, entry_prague)
    assert sensor_prague.unique_id == "entry_1_chmi_alerts_1000"

    # Test without area
    entry_no_area = Mock(spec=ConfigEntry)
    entry_no_area.entry_id = "entry_2"
    entry_no_area.data = {CONF_AREA_FILTER: ""}

    sensor_no_area = CAPAlertsBinarySensor(mock_coordinator, entry_no_area)
    assert sensor_no_area.unique_id == "entry_2_chmi_alerts"
