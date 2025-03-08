from aiohttp import ClientSession

from .token_error import TokenException

BASE_URL = 'https://lg.dwprod.co'

import logging

_LOGGER = logging.getLogger(__name__)

class DaveyDevice:
    def __init__(self, token, refresh_token, user_id):
        self.device_sn = None

        self.user_id = user_id
        self.token = token
        self.refresh_token = refresh_token

    async def setup_device_sn(self):
        data = await self.__make_request("GET", f'{BASE_URL}/device/me')
        self.device_sn = data['serialNumber']

    async def get_device_data(self):
        _LOGGER.debug('Fetch device data...')

        data = await self.__make_request("GET", f'{BASE_URL}/device/status/{self.device_sn}')
        _LOGGER.debug(data)

        return data

    async def refresh_token(self):
        _LOGGER.debug('Refresh token...')

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

                _LOGGER.debug('Token refreshed')

    async def __make_request(self, method, url, body=None, attempts=0):
        _LOGGER.debug('Make request...')

        if attempts > 3:
            raise TokenException('Failed to make request, your token/refresh token may be invalid.')

        async with ClientSession() as session:
            headers = {
                'Authorization': self.token
            }

            async with session.request(method, url, headers=headers, json=body) as response:
                if response.status == 401:
                    _LOGGER.debug('Need to refresh token')

                    await self.refresh_token()
                    return await self.__make_request(method, url, body, attempts=attempts + 1)
                elif response.status == 200:
                    _LOGGER.debug('Request good')

                    response.raise_for_status()
                    return await response.json()



async def login(email, password):
    async with ClientSession() as session:
        body = {
            'email': email,
            'password': password,
        }

        _LOGGER.info('Logging in with email: %s', email)
        _LOGGER.info('Logging in with password: %s', password)

        async with session.post(f'{BASE_URL}/user/signin', json=body) as response:
            response.raise_for_status()
            data = await response.json()

            _LOGGER.info(data)

            return data['token'], data['refreshToken'], data['user']['id']