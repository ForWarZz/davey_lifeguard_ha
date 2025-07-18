"""Config flow for Davey Lifeguard integration."""

from collections.abc import Mapping
import logging
from typing import Any

from aiohttp import ClientResponseError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_REFRESH_TOKEN,
    CONF_TOKEN,
    CONF_USER_ID,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .davey.api import authenticate

_LOGGER = logging.getLogger(__name__)


class DaveyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Davey Lifeguard."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step for user configuration."""
        errors = {}

        if user_input is not None:
            try:
                token, refresh_token, user_id = await authenticate(
                    user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
                )

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_TOKEN: token,
                        CONF_REFRESH_TOKEN: refresh_token,
                        CONF_USER_ID: user_id,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

            except ClientResponseError as e:
                _LOGGER.error("Invalid credentials: %s", e)
                errors["base"] = "invalid_credentials"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle re-authentication step."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication with new credentials."""
        errors = {}

        if user_input is not None:
            try:
                token, refresh_token, user_id = await authenticate(
                    user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
                )

                _LOGGER.info("Authentication successful, updating entry")
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_TOKEN: token,
                        CONF_REFRESH_TOKEN: refresh_token,
                        CONF_USER_ID: user_id,
                    },
                )

            except ClientResponseError as e:
                _LOGGER.error("Invalid credentials during reauth: %s", e)
                errors["base"] = "invalid_credentials"

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_EMAIL,
                    default=self._get_reauth_entry().data.get(CONF_EMAIL, ""),
                ): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=data_schema,
            errors=errors,
        )
