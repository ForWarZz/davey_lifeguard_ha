from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceData:
    serial_number: str
    firmware: str
    pool_size: int
    vsd_connected: bool


@dataclass
class StatusData:
    ph: float
    orp: int
    temp: float
    salinity: int
    ph_error: str
    orp_error: str
    salt_error: str
    flow_error: str
    vsd_speed: int
    ph_connected: bool
    orp_connected: bool
    temp_connected: bool
    salinity_connected: bool
