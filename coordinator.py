"""Coordinator for Davey Lifeguard integration."""

import asyncio
from datetime import timedelta
import logging

from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    FLOW_BIN_STATUS_KEY,
    ORP_SENSOR_KEY,
    PH_SENSOR_KEY,
    SALT_SENSOR_KEY,
    TEMP_SENSOR_KEY,
)
from .davey.davey_exception import (
    DaveyAPIException,
    DaveyAuthException,
    DaveyRequestException,
)

_LOGGER = logging.getLogger(__name__)


class DaveyCoordinator(DataUpdateCoordinator):
    """Coordinator for managing updates from the Davey Lifeguard API."""

    def __init__(self, hass, davey_api, config_entry) -> None:
        """Initialize the Davey coordinator."""
        scan_interval = config_entry.data[CONF_SCAN_INTERVAL]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            update_method=self._async_update_data,
        )
        self.davey_api = davey_api

    async def _async_update_data(self):
        """Fetch data from the Davey Lifeguard API."""
        try:
            async with asyncio.timeout(10):
                _LOGGER.debug("Fetching device data")
                account_data, status_data = await asyncio.gather(
                    self.davey_api.fetch_account_data(),
                    self.davey_api.fetch_status_data(),
                )

                full_data = account_data | status_data

                if full_data is None:
                    _LOGGER.warning("No data received from the device")
                    return None

                previous_data = self.data or {}
                if self._is_flow_disabled(full_data.get(FLOW_BIN_STATUS_KEY)):
                    for sensor_key in (
                        PH_SENSOR_KEY,
                        ORP_SENSOR_KEY,
                        SALT_SENSOR_KEY,
                        TEMP_SENSOR_KEY,
                    ):
                        if sensor_key in previous_data:
                            full_data[sensor_key] = previous_data[sensor_key]

                _LOGGER.debug("Device data fetched successfully")
                _LOGGER.debug("Device data: %s", full_data)

                return full_data
        except DaveyAuthException as auth_err:
            _LOGGER.error("Authentication failed : %s", auth_err)
            _LOGGER.debug("Stopping coordinator updates due to authentication failure")
            await self.__handle_token_error()
            raise ConfigEntryAuthFailed from auth_err

        except DaveyRequestException as req_err:
            raise UpdateFailed(f"Request error: {req_err}") from req_err

        except DaveyAPIException as api_err:
            raise UpdateFailed(f"Unhandled API error: {api_err}") from api_err

    @staticmethod
    def _is_flow_disabled(flow_value: object) -> bool:
        """Return True when flow/pump state indicates a stopped circulation."""
        if isinstance(flow_value, bool):
            return not flow_value
        if isinstance(flow_value, (int, float)):
            return flow_value == 0
        if isinstance(flow_value, str):
            normalized = flow_value.strip().lower()
            return normalized in {
                "0",
                "false",
                "off",
                "no_flow",
                "no flow",
                "stopped",
            }
        return False

    async def __handle_token_error(self):
        self.update_interval = None
