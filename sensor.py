"""Sensor platform for Davey Lifeguard integration."""

from datetime import date, datetime
from decimal import Decimal
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CELL_OUTPUT_KEY,
    DOMAIN,
    ORP_SENSOR_KEY,
    ORP_TARGET_KEY,
    PH_SENSOR_KEY,
    PH_TARGET_KEY,
    SALT_SENSOR_KEY,
    TEMP_SENSOR_KEY,
    VSD_PUMP_SPEED_KEY,
)
from .utils import get_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Davey Lifeguard sensors from a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Sensors
    sensors = [
        DaveySensor(coordinator, PH_SENSOR_KEY, "ph", "mdi:flask-outline"),
        DaveySensor(coordinator, ORP_SENSOR_KEY, "orp", "mdi:current-dc"),
        DaveySensor(coordinator, SALT_SENSOR_KEY, "salinity"),
        DaveySensor(coordinator, TEMP_SENSOR_KEY, "temp", "mdi:thermometer-water"),
        DaveySensor(coordinator, VSD_PUMP_SPEED_KEY, "vsd_pump_speed", "mdi:fan"),
        DaveySensor(coordinator, PH_TARGET_KEY, "ph_target", "mdi:flask-outline"),
        DaveySensor(coordinator, ORP_TARGET_KEY, "orp_target", "mdi:current-dc"),
        DaveySensor(coordinator, CELL_OUTPUT_KEY, "cell_output", "mdi:water-percent"),
    ]

    async_add_entities(sensors)


class DaveySensor(SensorEntity, CoordinatorEntity):
    """Representation of a Davey Lifeguard sensor."""

    def __init__(self, coordinator, key, translation_key, icon=None) -> None:
        """Initialize the Davey sensor."""
        super().__init__(coordinator)
        self._attr_translation_key = translation_key
        self._attr_has_entity_name = True
        self.key = key
        self._attr_icon = icon

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.key, None)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the sensor."""
        return get_device_info(
            self.coordinator.data["serialNumber"],
            self.coordinator.data["firmwareVersion"],
            self.coordinator.data["nipperVersion"],
        )

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement for the sensor."""
        if self.key == TEMP_SENSOR_KEY:
            return UnitOfTemperature.CELSIUS
        if "orp" in self.key:
            return UnitOfElectricPotential.MILLIVOLT
        if "salinity" in self.key:
            return CONCENTRATION_PARTS_PER_MILLION
        if "ph" in self.key:
            return "pH"
        if self.key == CELL_OUTPUT_KEY:
            return PERCENTAGE
        return None

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_sensor_{self.key}"

    @property
    def state_class(self):
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self.key == TEMP_SENSOR_KEY:
            return SensorDeviceClass.TEMPERATURE
        return None
