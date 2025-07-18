"""Integration for Davey Lifeguard API."""

import asyncio
import logging
from typing import Any

from aiohttp import ClientSession

from homeassistant.exceptions import ConfigEntryAuthFailed

from ..const import (
    BASE_URL,
    ORP_BIN_STATUS_KEY,
    ORP_TARGET_KEY,
    PH_BIN_STATUS_KEY,
    PH_TARGET_KEY,
    SALT_BIN_STATUS_KEY,
    TEMP_BIN_STATUS_KEY,
    TEMP_TARGET_KEY,
    VSD_BIN_STATUS_KEY,
    VSD_PUMP_SPEED_KEY,
)
from .davey_exception import (
    DaveyAPIException,
    DaveyAuthException,
    DaveyRequestException,
)

_LOGGER = logging.getLogger(__name__)


class DaveyAPI:
    """API client for interacting with the Davey Lifeguard system."""

    def __init__(self, token: str, refresh_token: str, user_id: str) -> None:
        """Initialize the API client."""
        self.token: str = token
        self.refresh_token: str = refresh_token
        self.user_id: str = user_id
        self.device_sn: str | None = None
        self._account_data: dict[str, Any] | None = None
        self._status_data: dict[str, Any] | None = None

    async def __refresh_token(self) -> None:
        """Refresh the authentication token."""
        _LOGGER.debug("Refreshing token")

        async with ClientSession() as session:
            body = {"refreshToken": self.refresh_token, "userId": self.user_id}

            async with session.post(f"{BASE_URL}/user/auth", json=body) as response:
                if response.status != 200:
                    _LOGGER.warning(
                        "Failed to refresh token, status code: %s", response.status
                    )
                    raise DaveyAuthException("Failed to refresh token")
                data = await response.json()

        self.token = data["token"]
        self.refresh_token = data["refreshToken"]
        _LOGGER.debug("Token refreshed successfully")

    async def __authenticated_call(
        self, method: str, url: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Make an authenticated API call."""
        _LOGGER.debug("Calling %s [%s]", url, method)

        try:
            async with ClientSession() as session:
                headers = {"Authorization": self.token}

                async with session.request(
                    method, url, headers=headers, json=body
                ) as response:
                    if response.status == 401:
                        _LOGGER.warning("Token expired or invalid, refreshing")

                        await self.__refresh_token()
                        return await self.__authenticated_call(method, url, body)

                    response.raise_for_status()
                    return await response.json()
        except TimeoutError as exc:
            _LOGGER.error("Timeout during request to %s: %s", url, exc)
            raise DaveyRequestException("Request timed out") from exc
        except DaveyAuthException:
            _LOGGER.error("Authentication failed during request to %s", url)
            raise
        except Exception as exc:
            _LOGGER.exception("Unexpected error during request")
            raise DaveyAPIException(f"Unexpected error: {exc}") from exc

    async def fetch_account_data(self) -> dict[str, Any]:
        """Fetch account data from the API."""
        _LOGGER.debug("Fetching account data")

        self._account_data = await self.__authenticated_call(
            "GET", f"{BASE_URL}/device/me"
        )

        if self.device_sn is None:
            self.device_sn = self._account_data.get("serialNumber")

        return self._account_data

    async def fetch_status_data(self) -> dict[str, Any]:
        """Fetch device status data from the API."""
        _LOGGER.debug("Fetching device status data")

        self._status_data = await self.__authenticated_call(
            "GET", f"{BASE_URL}/device/status/{self.device_sn}"
        )

        return self._status_data

    async def change_target(self, target_key: str, target_value: int) -> None:
        """Change a target value on the device."""
        _LOGGER.debug("Changing target %s to %s", target_key, target_value)

        account_data, status_data = await asyncio.gather(
            self.fetch_account_data()
            if self._account_data is None
            else asyncio.sleep(0, self._account_data),
            self.fetch_status_data()
            if self._status_data is None
            else asyncio.sleep(0, self._status_data),
        )

        body = {
            "serialNumber": self.device_sn,
            "targets": {
                "salinity": 1250,
                "ph": account_data.get(PH_TARGET_KEY),
                "orp": account_data.get(ORP_TARGET_KEY),
                "temp": account_data.get(TEMP_TARGET_KEY),
                "isVsdPumpConnected": account_data.get(VSD_BIN_STATUS_KEY),
                "vsdPumpSpeed": account_data.get(VSD_PUMP_SPEED_KEY),
                "phConnected": status_data.get(PH_BIN_STATUS_KEY),
                "salinityConnected": status_data.get(SALT_BIN_STATUS_KEY),
                "orpConnected": status_data.get(ORP_BIN_STATUS_KEY),
                "tempConnected": status_data.get(TEMP_BIN_STATUS_KEY),
                "cellOutput": account_data.get("cellOutput"),
                "backwashDuration": account_data.get("backwashDuration"),
                "boostDuration": account_data.get("boostDuration"),
                target_key: target_value,
            },
        }

        await self.__authenticated_call(
            "POST", f"{BASE_URL}/device/change-target", body
        )

    async def change_modes(self, active_modes: list[str]) -> None:
        """Change the active modes on the device."""
        _LOGGER.debug("Changing modes to: %s", active_modes)

        body = {"serialNumber": self.device_sn, "modes": active_modes}
        await self.__authenticated_call(
            "POST", f"{BASE_URL}/device/v2/change-mode", body
        )


async def authenticate(email: str, password: str) -> tuple[str, str, str]:
    """Authenticate with the Davey server and return tokens and user ID."""
    _LOGGER.debug("Authenticating with Davey server")

    async with ClientSession() as session:
        body = {"email": email, "password": password}
        async with session.post(f"{BASE_URL}/user/signin", json=body) as response:
            response.raise_for_status()
            data = await response.json()

    _LOGGER.debug("Authentication successful")
    return data["token"], data["refreshToken"], data["user"]["id"]
