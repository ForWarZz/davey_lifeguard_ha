from .const import DOMAIN

def get_device_info(device_sn, firmware_version, nipper_version) -> dict:
    return {
        "identifiers": {(DOMAIN, device_sn)},
        "name": "Davey Lifeguard",
        "manufacturer": "Davey",
        "model": "Lifeguard",
        "sw_version": firmware_version,
        "hw_version": nipper_version,
        "serial_number": device_sn,
    }