"""Initialize the Davey Lifeguard integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import CONF_REFRESH_TOKEN, CONF_TOKEN, CONF_USER_ID, DOMAIN, PLATFORMS
from .coordinator import DaveyCoordinator
from .davey.api import DaveyAPI
from .davey.davey_exception import DaveyAuthException

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Davey Lifeguard from a config entry."""

    try:
        hass.data.setdefault(DOMAIN, {})

        token = config_entry.data[CONF_TOKEN]
        refresh_token = config_entry.data[CONF_REFRESH_TOKEN]
        user_id = config_entry.data[CONF_USER_ID]

        try:
            davey_api = DaveyAPI(token, refresh_token, user_id)
            await davey_api.fetch_account_data()
        except DaveyAuthException as e:
            _LOGGER.error("Authentication failed: %s", e)
            config_entry.async_start_reauth(hass)
            return False

        davey_coordinator = DaveyCoordinator(hass, davey_api, config_entry)

        _LOGGER.debug("Setting up davey coordinator")
        _LOGGER.debug(davey_coordinator)

        hass.data[DOMAIN][config_entry.entry_id] = davey_coordinator

        await davey_coordinator.async_config_entry_first_refresh()
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

        _LOGGER.info("Successfully set up Davey Lifeguard")
        return True
    except Exception:
        _LOGGER.exception("Failed to setup Davey Lifeguard")
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    try:
        for platform in PLATFORMS:
            await hass.config_entries.async_forward_entry_unload(entry, platform)

        hass.data[DOMAIN].pop(entry.entry_id)

        _LOGGER.info("Successfully unloaded Davey Lifeguard")
        return True
    except Exception:
        _LOGGER.exception("Failed to unload Davey Lifeguard")
        return False
