from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DAVEY_STATUS_SENSOR_KEY, PH_BIN_STATUS_KEY, ORP_BIN_STATUS_KEY, TEMP_BIN_STATUS_KEY, \
    SALT_BIN_STATUS_KEY, VSD_BIN_STATUS_KEY, FLOW_ERROR_KEY, PH_ERROR_KEY, ORP_ERROR_KEY, SALT_ERROR_KEY
from .utils import get_device_info


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Binary Sensors
    binary_sensors = [
        DaveyBinarySensor(coordinator, DAVEY_STATUS_SENSOR_KEY, "is_connected"),

        DaveyBinarySensor(coordinator, PH_BIN_STATUS_KEY, "ph_connected"),
        DaveyBinarySensor(coordinator, ORP_BIN_STATUS_KEY, "orp_connected"),
        DaveyBinarySensor(coordinator, TEMP_BIN_STATUS_KEY, "temp_connected"),
        DaveyBinarySensor(coordinator, SALT_BIN_STATUS_KEY, "salinity_connected"),
        DaveyBinarySensor(coordinator, VSD_BIN_STATUS_KEY, "vsd_connected"),

        DaveyErrorBinarySensor(coordinator, FLOW_ERROR_KEY, "flow_error"),
        DaveyErrorBinarySensor(coordinator, PH_ERROR_KEY, "ph_error"),
        DaveyErrorBinarySensor(coordinator, ORP_ERROR_KEY, "orp_error"),
        DaveyErrorBinarySensor(coordinator, SALT_ERROR_KEY, "salt_error"),
    ]

    async_add_entities(binary_sensors)

class DaveyBinarySensor(BinarySensorEntity, CoordinatorEntity):
    def __init__(self, coordinator, key, translation_key):
        super().__init__(coordinator)
        self._attr_translation_key = translation_key
        self._attr_has_entity_name = True
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
    def __init__(self, coordinator, key, translation_key):
        super().__init__(coordinator)
        self._attr_translation_key = translation_key
        self._attr_has_entity_name = True
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