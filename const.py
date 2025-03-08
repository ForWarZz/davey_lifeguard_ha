from homeassistant.const import Platform

DOMAIN = 'davey_lifeguard'
DEFAULT_NAME = 'Davey Lifeguard'

DEFAULT_SCAN_INTERVAL = 10  # seconds

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_TOKEN = 'lifeguard_account_token'
CONF_REFRESH_TOKEN = 'lifeguard_refresh_token'
CONF_USER_ID = 'lifeguard_user_id'


PH_SENSOR_KEY = 'ph'
TEMP_SENSOR_KEY = 'temp'
SALT_SENSOR_KEY = 'salinity'
ORP_SENSOR_KEY = 'orp'
