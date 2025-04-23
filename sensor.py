import logging
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfElectricPotential,
    CONCENTRATION_PARTS_PER_MILLION
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .utils import get_device_info
from .const import (
    DOMAIN,
    PH_SENSOR_KEY, TEMP_SENSOR_KEY, SALT_SENSOR_KEY, ORP_SENSOR_KEY,
    VSD_PUMP_SPEED_KEY
)
from .coordinator import DaveyCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    davey = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = DaveyCoordinator(hass, davey, config_entry)

    await coordinator.async_config_entry_first_refresh()

    # Sensors
    sensors = [
        DaveySensor(coordinator, PH_SENSOR_KEY, "Niveau pH"),
        DaveySensor(coordinator, ORP_SENSOR_KEY, "Niveau ORP"),
        DaveySensor(coordinator, SALT_SENSOR_KEY, "Niveau sel"),
        DaveySensor(coordinator, TEMP_SENSOR_KEY, "Température eau"),
        DaveySensor(coordinator, VSD_PUMP_SPEED_KEY, "Vitesse VSD"),
    ]

    async_add_entities(sensors)


class DaveySensor(SensorEntity, CoordinatorEntity):
    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self._attr_name = name
        self.key = key

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return self.coordinator.data.get(self.key, None)

    @property
    def device_info(self) -> DeviceInfo:
        return get_device_info(
            self.coordinator.data["serialNumber"],
            self.coordinator.data["firmwareVersion"],
            self.coordinator.data["nipperVersion"],
        )

    @property
    def native_unit_of_measurement(self):
        if self.key == TEMP_SENSOR_KEY:
            return UnitOfTemperature.CELSIUS
        elif self.key == ORP_SENSOR_KEY:
            return UnitOfElectricPotential.MILLIVOLT
        elif self.key == SALT_SENSOR_KEY:
            return CONCENTRATION_PARTS_PER_MILLION
        elif self.key == PH_SENSOR_KEY:
            return "pH"
        return None

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.key}"

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def device_class(self):
        if self.key == TEMP_SENSOR_KEY:
            return SensorDeviceClass.TEMPERATURE
        return None
