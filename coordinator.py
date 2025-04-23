import asyncio
import logging
from datetime import timedelta

import async_timeout
from homeassistant.const import CONF_SCAN_INTERVAL

from .davey.token_error import TokenException
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
        except TokenException as err:
            _LOGGER.error(f'Token error: {err}', exc_info=True)
            await self.__handle_token_error()
        except Exception as e:
            raise UpdateFailed(f'Failed to update data: {e}')

    async def __handle_token_error(self):
        self.update_interval = None
