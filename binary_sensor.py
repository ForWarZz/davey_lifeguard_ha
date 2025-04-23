from typing import Literal

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .utils import get_device_info
from .coordinator import DaveyCoordinator
from .const import DOMAIN, DAVEY_STATUS_SENSOR_KEY, PH_BIN_STATUS_KEY, ORP_BIN_STATUS_KEY, TEMP_BIN_STATUS_KEY, \
    SALT_BIN_STATUS_KEY, VSD_BIN_STATUS_KEY, FLOW_ERROR_KEY, PH_ERROR_KEY, ORP_ERROR_KEY, SALT_ERROR_KEY


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    davey = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = DaveyCoordinator(hass, davey, config_entry)

    await coordinator.async_config_entry_first_refresh()

    # Binary Sensors
    binary_sensors = [
        DaveyBinarySensor(coordinator, DAVEY_STATUS_SENSOR_KEY, "Statut de l'appareil"),

        DaveyBinarySensor(coordinator, PH_BIN_STATUS_KEY, "Sonde pH"),
        DaveyBinarySensor(coordinator, ORP_BIN_STATUS_KEY, "Sonde ORP"),
        DaveyBinarySensor(coordinator, TEMP_BIN_STATUS_KEY, "Sonde température"),
        DaveyBinarySensor(coordinator, SALT_BIN_STATUS_KEY, "Sonde sel"),
        DaveyBinarySensor(coordinator, VSD_BIN_STATUS_KEY, "Pompe VSD"),

        DaveyErrorBinarySensor(coordinator, FLOW_ERROR_KEY, "Erreur de débit"),
        DaveyErrorBinarySensor(coordinator, PH_ERROR_KEY, "Erreur pH"),
        DaveyErrorBinarySensor(coordinator, ORP_ERROR_KEY, "Erreur ORP"),
        DaveyErrorBinarySensor(coordinator, SALT_ERROR_KEY, "Erreur sel"),
    ]

    async_add_entities(binary_sensors)

class DaveyBinarySensor(BinarySensorEntity, CoordinatorEntity):
    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self._attr_name = name
        self.key = key

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(self.key, False)

    @property
    def unique_id(self):
        return f"{DOMAIN}_binary_{self.key}"

    @property
    def device_info(self) -> DeviceInfo:
        return get_device_info(
            self.coordinator.data["serialNumber"],
            self.coordinator.data["firmwareVersion"],
            self.coordinator.data["nipperVersion"],
        )

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

class DaveyErrorBinarySensor(BinarySensorEntity, CoordinatorEntity):
    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self._attr_name = name
        self.key = key

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(self.key) != "NORMAL"

    @property
    def device_info(self) -> DeviceInfo:
        return get_device_info(
            self.coordinator.data["serialNumber"],
            self.coordinator.data["firmwareVersion"],
            self.coordinator.data["nipperVersion"],
        )

    @property
    def device_class(self):
        return "problem"

    @property
    def icon(self):
        return "mdi:alert" if self.is_on else "mdi:check-circle"

    @property
    def entity_category(self) -> EntityCategory | None:
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_error_{self.key}"