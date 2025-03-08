from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_TOKEN, PLATFORMS, CONF_REFRESH_TOKEN, CONF_USER_ID
from .davey.api import DaveyDevice
from homeassistant.const import Platform

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    try:
        hass.data.setdefault(DOMAIN, {})

        token = config_entry.data[CONF_TOKEN]
        refresh_token = config_entry.data[CONF_REFRESH_TOKEN]
        user_id = config_entry.data[CONF_USER_ID]

        davey_lifeguard = DaveyDevice(token, refresh_token, user_id)
        await davey_lifeguard.setup_device_sn()

        hass.data[DOMAIN][config_entry.entry_id] = davey_lifeguard

        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

        _LOGGER.info('Successfully set up Davey Lifeguard')
        return True

    except Exception as e:
        _LOGGER.error(f'Failed to setup Davey Lifeguard: {e}')
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    try:
        for platform in PLATFORMS:
            await hass.config_entries.async_forward_entry_unload(entry, platform)

        hass.data[DOMAIN].pop(entry.entry_id)

        _LOGGER.info('Successfully unloaded Davey Lifeguard')
        return True

    except Exception as e:
        _LOGGER.error(f'Failed to unload Davey Lifeguard: {e}')
        return False
