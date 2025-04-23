import asyncio
import logging
from datetime import timedelta

import async_timeout
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.exceptions import ConfigEntryAuthFailed

from .davey.davey_exception import DaveyAuthException, DaveyRequestException, DaveyAPIException
from .const import DOMAIN

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class DaveyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, davey_api, config_entry):
        scan_interval = config_entry.data[CONF_SCAN_INTERVAL]

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval), update_method=self._async_update_data)
        self.davey_api = davey_api

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                _LOGGER.debug("Fetching device data")
                account_data, status_data = await asyncio.gather(
                    self.davey_api.fetch_account_data(),
                    self.davey_api.fetch_status_data()
                )

                full_data = account_data | status_data

                if full_data is None:
                    _LOGGER.warning("No data received from the device...")
                    return None

                _LOGGER.debug("Device data fetched successfully")
                _LOGGER.debug(f"Device data: {full_data}")

                return full_data
        except DaveyAuthException as auth_err:
            _LOGGER.error(f'Authentication failed: {auth_err}')
            raise ConfigEntryAuthFailed from auth_err

        except DaveyRequestException as req_err:
            raise UpdateFailed(f'Request error: {req_err}') from req_err

        except DaveyAPIException as api_err:
            raise UpdateFailed(f'Unhandled API error: {api_err}') from api_err

    async def __handle_token_error(self):
        self.update_interval = None
