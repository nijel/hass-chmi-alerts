"""Data update coordinator for CAP alerts."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .cap_parser import CAPAlert, parse_cap_xml
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class CAPAlertsCoordinator(DataUpdateCoordinator[list[CAPAlert]]):
    """Class to manage fetching CAP alerts data."""

    def __init__(
        self,
        hass: HomeAssistant,
        feed_url: str,
        area_filter: str | None = None,
        language_filter: str | None = None,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        self.feed_url = feed_url
        self.area_filter = area_filter
        self.language_filter = language_filter

        super().__init__(
            hass,
            _LOGGER,
            name="CAP Alerts",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> list[CAPAlert]:
        """Fetch data from CAP feed."""
        try:
            async with asyncio.timeout(30):
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.feed_url) as response:
                        if response.status != 200:
                            raise UpdateFailed(
                                f"Error fetching data: HTTP {response.status}"
                            )
                        xml_content = await response.text()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed("Timeout fetching data") from err

        # Parse the CAP XML
        all_alerts = parse_cap_xml(xml_content)

        # Filter by area if specified
        if self.area_filter:
            filtered_alerts = [
                alert for alert in all_alerts if alert.matches_area(self.area_filter)
            ]
            _LOGGER.debug(
                "Filtered %d alerts to %d matching area '%s'",
                len(all_alerts),
                len(filtered_alerts),
                self.area_filter,
            )
            all_alerts = filtered_alerts

        # Filter by language if specified
        if self.language_filter:
            filtered_alerts = [
                alert
                for alert in all_alerts
                if alert.matches_language(self.language_filter)
            ]
            _LOGGER.debug(
                "Filtered %d alerts to %d matching language '%s'",
                len(all_alerts),
                len(filtered_alerts),
                self.language_filter,
            )
            all_alerts = filtered_alerts

            # Set language filter on each alert so it returns the preferred info section
            for alert in all_alerts:
                alert.set_language_filter(self.language_filter)

        return all_alerts
