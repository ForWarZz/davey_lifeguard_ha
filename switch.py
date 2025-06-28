"""Switch entities for Davey Lifeguard modes."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BOOT_OPTION_KEY, DOMAIN, MANUAL_OPTION_KEY
from .coordinator import DaveyCoordinator
from .utils import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Davey Lifeguard mode switches."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    modes = [
        DaveyModeSwitch(coordinator, MANUAL_OPTION_KEY, "mdi:hand-back-left"),
        DaveyModeSwitch(coordinator, BOOT_OPTION_KEY, "mdi:flash"),
    ]

    async_add_entities(modes)


class DaveyModeSwitch(SwitchEntity, CoordinatorEntity):
    """Representation of a Davey mode switch."""

    def __init__(self, coordinator: DaveyCoordinator, key, icon) -> None:
        """Initialize the Davey mode switch."""
        super().__init__(coordinator)
        self._attr_translation_key = key
        self._attr_has_entity_name = True
        self.key = key
        self._attr_icon = icon

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self.key in self.coordinator.data.get("modes", [])

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        await self._update_modes(enabled=True)

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        await self._update_modes(enabled=False)

    async def _update_modes(self, enabled: bool):
        current_modes = self.coordinator.data.get("modes", []).copy()
        if enabled:
            current_modes.append(self.key)
        elif self.key in current_modes:
            current_modes.remove(self.key)

        await self.coordinator.davey_api.change_modes(current_modes)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the switch."""
        return get_device_info(
            self.coordinator.data["serialNumber"],
            self.coordinator.data["firmwareVersion"],
            self.coordinator.data["nipperVersion"],
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the switch."""
        return f"{DOMAIN}_switch_{self.key}"
