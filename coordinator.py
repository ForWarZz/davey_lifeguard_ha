import logging
from datetime import timedelta

import async_timeout
from homeassistant.const import CONF_SCAN_INTERVAL

from .davey.token_error import TokenException
from .const import DOMAIN

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class DaveyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, davey_device, config_entry):
        scan_interval = config_entry.data[CONF_SCAN_INTERVAL]

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval), update_method=self._async_update_data)
        self.davey_device = davey_device

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                return await self.davey_device.get_device_data()
        except TokenException as err:
            _LOGGER.error(f'Token error: {err}', exc_info=True)
            await self.__handle_token_error()
        except Exception as e:
            raise UpdateFailed(f'Failed to update data: {e}')

    async def __handle_token_error(self):
        self.update_interval = None
