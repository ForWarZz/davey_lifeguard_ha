import logging

from aiohttp import ClientSession

from ..const import BASE_URL, PH_TARGET_KEY, ORP_TARGET_KEY, TEMP_TARGET_KEY, VSD_BIN_STATUS_KEY, VSD_PUMP_SPEED_KEY, \
    PH_BIN_STATUS_KEY, SALT_BIN_STATUS_KEY, ORP_BIN_STATUS_KEY, TEMP_BIN_STATUS_KEY

_LOGGER = logging.getLogger(__name__)

class DaveyAPI:
    def __init__(self, token, refresh_token, user_id):
        self.token = token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.device_sn = None

    async def __refresh_token(self):
        _LOGGER.debug('Refreshing token...')

        async with ClientSession() as session:
            body = {
                'refreshToken': self.refresh_token,
                'userId': self.user_id
            }

            async with session.post(f'{BASE_URL}/user/auth', json=body) as response:
                response.raise_for_status()
                data = await response.json()

            self.token = data['token']
            self.refresh_token = data['refreshToken']

            _LOGGER.debug('Token refreshed successfully')

    async def __authenticated_call(self, method, url, body=None):
        _LOGGER.debug('Making authenticated call...')

        async with ClientSession() as session:
            headers = {
                'Authorization': self.token,
            }

            async with session.request(method, url, headers=headers, json=body) as response:
                if response.status == 401:
                    _LOGGER.debug('Token expired, refreshing...')
                    await self.__refresh_token()
                    return await self.__authenticated_call(method, url, body)
                elif response.status == 200:
                    _LOGGER.debug('Request successful')
                    return await response.json()
                else:
                    response.raise_for_status()

    async def fetch_account_data(self):
        _LOGGER.debug('Fetching device data...')

        data = await self.__authenticated_call("GET", f'{BASE_URL}/device/me')
        _LOGGER.debug(data)

        if self.device_sn is None:
            self.device_sn = data['serialNumber']

        return data

    async def fetch_device_data(self):
        _LOGGER.debug('Fetching device data...')

        data = await self.__authenticated_call("GET", f'{BASE_URL}/device/status/{self.device_sn}')
        _LOGGER.debug(data)

        return data

    async def change_target(self, target_key, target_value):
        _LOGGER.debug('Changing target...')

        account_data = await self.fetch_account_data()
        device_data = await self.fetch_device_data()

        body = {
            'serialNumber': self.device_sn,
            'targets': {
                'salinity': 1250,
                'ph': account_data[PH_TARGET_KEY],
                'orp': account_data[ORP_TARGET_KEY],
                'temp': account_data[TEMP_TARGET_KEY],

                'isVsdPumpConnected': account_data[VSD_BIN_STATUS_KEY],
                'vsdPumpSpeed': account_data[VSD_PUMP_SPEED_KEY],

                'phConnected': device_data[PH_BIN_STATUS_KEY],
                'salinityConnected': device_data[SALT_BIN_STATUS_KEY],
                'orpConnected': device_data[ORP_BIN_STATUS_KEY],
                'tempConnected': device_data[TEMP_BIN_STATUS_KEY],

                'cellOutput': device_data['cellOutput'],
                'backwashDuration': device_data['backwashDuration'],
                'boostDuration': device_data['boostDuration'],

                target_key: target_value,
            }
        }

        await self.__authenticated_call("POST", f'{BASE_URL}/device/change-target', body)

async def authenticate(email, password):
    _LOGGER.debug("Authenticating with Davey server...")

    async with ClientSession() as session:
        body = {
            'email': email,
            'password': password,
        }

        async with session.post(f'{BASE_URL}/user/signin', json=body) as response:
            response.raise_for_status()
            data = await response.json()

        token = data['token']
        refresh_token = data['refreshToken']
        user_id = data['user']['id']

        _LOGGER.debug("Authentication successful")

    return token, refresh_token, user_id