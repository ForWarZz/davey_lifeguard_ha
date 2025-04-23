class DaveySensorData:
    def __init__(self, name, value, target, unit, connected, error):
        self.name = name
        self.value = value
        self.target = target
        self.unit = unit
        self.connected = connected

class DaveyDeviceData:
    def __init__(self, serial_number, firmware_version, pool_size, sensors_data):
        self.serial_number = serial_number
        self.firmware_version = firmware_version
        self.pool_size = pool_size
        self.sensors_data = sensors_data