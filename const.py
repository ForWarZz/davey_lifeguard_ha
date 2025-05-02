from homeassistant.const import Platform

DOMAIN = 'davey_lifeguard'
DEFAULT_NAME = 'Davey Lifeguard'
BASE_URL = 'https://lg.dwprod.co'

TIMESTAMP_INTERVAL = 10  # seconds

DEFAULT_SCAN_INTERVAL = 600  # seconds

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SELECT
]

# Auth
CONF_TOKEN = 'lifeguard_account_token'
CONF_REFRESH_TOKEN = 'lifeguard_refresh_token'
CONF_USER_ID = 'lifeguard_user_id'

DAVEY_STATUS_SENSOR_KEY = 'isConnected'

# Sensors
PH_SENSOR_KEY = 'ph'
TEMP_SENSOR_KEY = 'temp'
SALT_SENSOR_KEY = 'salinity'
ORP_SENSOR_KEY = 'orp'
VSD_PUMP_SPEED_KEY = 'vsdPumpSpeed'

CELL_OUTPUT_KEY = 'cellOutput'

# Targets
TEMP_TARGET_KEY = 'tempTarget'
PH_TARGET_KEY = 'phTarget'
ORP_TARGET_KEY = 'orpTarget'

VSD_TARGET_SPEED_KEY = 'vsdPumpSpeed'

# Binary status sensors
PH_BIN_STATUS_KEY = 'phConnected'
TEMP_BIN_STATUS_KEY = 'tempConnected'
SALT_BIN_STATUS_KEY = 'salinityConnected'
ORP_BIN_STATUS_KEY = 'orpConnected'

# Error status sensors
FLOW_ERROR_KEY = 'flowError'
PH_ERROR_KEY = 'phError'
SALT_ERROR_KEY = 'saltError'
ORP_ERROR_KEY = 'orpError'

VSD_BIN_STATUS_KEY = 'isVsdPumpConnected'

MANUAL_OPTION_KEY = 'MANUAL'
BOOT_OPTION_KEY = 'BOOST'