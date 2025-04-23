from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUAL_OPTION_KEY, BOOT_OPTION_KEY


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    modes = [
        DaveyModeSwitch(coordinator, MANUAL_OPTION_KEY, "Mode Manuel", "mdi:hand"),
        DaveyModeSwitch(coordinator, BOOT_OPTION_KEY, "Mode Boost", "mdi:flash")
    ]

    async_add_entities(modes)

class DaveyModeSwitch(SwitchEntity, CoordinatorEntity):
    def __init__(self, coordinator, key, name, icon):
        super().__init__(coordinator)
        self._attr_name = name
        self.key = key
        self._attr_icon = icon

    @property
    def is_on(self) -> bool:
        return self.key in self.coordinator.data.get("modes", [])

    async def async_turn_on(self, **kwargs):
        await self._update_modes(enabled=True)

    async def async_turn_off(self, **kwargs):
        await self._update_modes(enabled=False)

    async def _update_modes(self, enabled: bool):
        current_modes = self.coordinator.data.get("modes", []).copy()
        if enabled:
            current_modes.append(self.key)
        else:
            if self.key in current_modes:
                current_modes.remove(self.key)

        await self.coordinator.davey_api.change_modes(current_modes)
        await self.coordinator.async_request_refresh()
