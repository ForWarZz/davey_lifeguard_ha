import asyncio
import logging
from aiohttp import ClientSession
from ..const import (
    BASE_URL, PH_TARGET_KEY, ORP_TARGET_KEY, TEMP_TARGET_KEY,
    VSD_BIN_STATUS_KEY, VSD_PUMP_SPEED_KEY,
    PH_BIN_STATUS_KEY, SALT_BIN_STATUS_KEY,
    ORP_BIN_STATUS_KEY, TEMP_BIN_STATUS_KEY
)

_LOGGER = logging.getLogger(__name__)

class DaveyAPI:
    def __init__(self, token, refresh_token, user_id):
        self.token = token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.device_sn = None

        self._account_data = None
        self._status_data = None

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
        _LOGGER.debug(f'Calling {url} [{method}]')

        async with ClientSession() as session:
            headers = {'Authorization': self.token}

            async with session.request(method, url, headers=headers, json=body) as response:
                if response.status == 401:
                    _LOGGER.debug('Token expired, refreshing...')
                    await self.__refresh_token()

                    return await self.__authenticated_call(method, url, body)

                response.raise_for_status()
                if response.status == 200:
                    return await response.json()

                return None

    async def fetch_account_data(self):
        _LOGGER.debug('Fetching account data...')

        self._account_data = await self.__authenticated_call("GET", f'{BASE_URL}/device/me')

        if self.device_sn is None:
            self.device_sn = self._account_data.get('serialNumber')

        return self._account_data

    async def fetch_status_data(self):
        _LOGGER.debug('Fetching device status data...')

        self._status_data = await self.__authenticated_call("GET", f'{BASE_URL}/device/status/{self.device_sn}')

        return self._status_data

    async def change_target(self, target_key, target_value):
        _LOGGER.debug(f'Changing target {target_key} to {target_value}...')

        if self._account_data is not None and self._status_data is not None:
            _LOGGER.debug('Using cached account and device data')

        account_data, status_data = await asyncio.gather(
            self.fetch_account_data() if self._account_data is None else asyncio.sleep(0, self._account_data),
            self.fetch_status_data() if self._status_data is None else asyncio.sleep(0, self._status_data)
        )

        body = {
            'serialNumber': self.device_sn,
            'targets': {
                'salinity': 1250,
                'ph': account_data.get(PH_TARGET_KEY),
                'orp': account_data.get(ORP_TARGET_KEY),
                'temp': account_data.get(TEMP_TARGET_KEY),

                'isVsdPumpConnected': account_data.get(VSD_BIN_STATUS_KEY),
                'vsdPumpSpeed': account_data.get(VSD_PUMP_SPEED_KEY),

                'phConnected': status_data.get(PH_BIN_STATUS_KEY),
                'salinityConnected': status_data.get(SALT_BIN_STATUS_KEY),
                'orpConnected': status_data.get(ORP_BIN_STATUS_KEY),
                'tempConnected': status_data.get(TEMP_BIN_STATUS_KEY),

                'cellOutput': account_data.get('cellOutput'),
                'backwashDuration': account_data.get('backwashDuration'),
                'boostDuration': account_data.get('boostDuration'),

                target_key: target_value
            }
        }

        await self.__authenticated_call("POST", f'{BASE_URL}/device/change-target', body)

    async def change_modes(self, active_modes: list[str]):
        _LOGGER.debug(f'Changing modes to: {active_modes}')

        body = {
            'serialNumber': self.device_sn,
            'modes': active_modes,
        }

        await self.__authenticated_call("POST", f'{BASE_URL}/device/v2/change-mode', body)


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
