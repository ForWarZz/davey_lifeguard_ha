"""Select entities for Davey Lifeguard integration."""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ORP_TARGET_KEY, PH_TARGET_KEY, VSD_PUMP_SPEED_KEY
from .coordinator import DaveyCoordinator
from .utils import get_device_info


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Davey Lifeguard select entities from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    selects = [
        DaveySelect(
            coordinator=coordinator,
            translation_key="vsd_pump_speed",
            data_key=VSD_PUMP_SPEED_KEY,
            target_key=VSD_PUMP_SPEED_KEY,
            options=["2", "4", "6", "8", "10"],
            icon="mdi:fan",
        ),
        DaveySelect(
            coordinator=coordinator,
            translation_key="ph_target",
            data_key=PH_TARGET_KEY,
            target_key="ph",
            options=[f"{v:.1f}" for v in [x * 0.1 for x in range(70, 80)]],
            icon="mdi:flask-outline",
        ),
        DaveySelect(
            coordinator=coordinator,
            translation_key="orp_target",
            data_key=ORP_TARGET_KEY,
            target_key="orp",
            options=[str(v) for v in range(600, 1000, 50)],
            icon="mdi:current-dc",
        ),
    ]

    async_add_entities(selects)


class DaveySelect(CoordinatorEntity, SelectEntity):
    """Representation of a Davey Lifeguard select entity."""

    def __init__(
        self,
        coordinator: DaveyCoordinator,
        translation_key: str,
        data_key: str,
        target_key: str,
        options: list[str],
        icon: str,
    ) -> None:
        """Initialize the Davey select entity."""

        super().__init__(coordinator)
        self._attr_icon = icon
        self._attr_translation_key = translation_key
        self._attr_has_entity_name = True
        self._attr_options = options

        self.data_key = data_key
        self.target_key = target_key

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        value = self.coordinator.data.get(self.data_key)
        return str(value) if value is not None else None

    async def async_select_option(self, option: str) -> None:
        """Handle option selection."""
        await self.coordinator.davey_api.change_target(
            self.target_key, float(option) if "." in option else int(option)
        )
        await self.coordinator.async_request_refresh()

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the select entity."""
        return f"{DOMAIN}_select_{self.data_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the select entity."""
        return get_device_info(
            self.coordinator.data.get("serialNumber"),
            self.coordinator.data.get("firmwareVersion"),
            self.coordinator.data.get("nipperVersion"),
        )
