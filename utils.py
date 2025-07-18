"""Utility functions for the Davey Lifeguard integration."""

from .const import DOMAIN


def get_device_info(device_sn, firmware_version, nipper_version) -> dict:
    """Return device information for the Davey Lifeguard integration.

    Args:
        device_sn (str): The serial number of the device.
        firmware_version (str): The firmware version of the device.
        nipper_version (str): The hardware version of the device.

    Returns:
        dict: A dictionary containing device information.

    """
    return {
        "identifiers": {(DOMAIN, device_sn)},
        "name": "Davey Lifeguard",
        "manufacturer": "Davey",
        "model": "Lifeguard",
        "sw_version": firmware_version,
        "hw_version": nipper_version,
        "serial_number": device_sn,
    }
