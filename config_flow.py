import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from typing import Any, Optional

from homeassistant.const import CONF_SCAN_INTERVAL, CONF_PASSWORD, CONF_EMAIL

from .davey.api import login
from .const import DOMAIN, CONF_TOKEN, DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, CONF_REFRESH_TOKEN, CONF_USER_ID
import logging

_LOGGER = logging.getLogger(__name__)


class DaveyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
            self, user_input: Optional[dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        errors = {}

        if user_input is not None:
            try:
                token, refresh_token, user_id = await login(user_input[CONF_EMAIL], user_input[CONF_PASSWORD])
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_TOKEN: token,
                        CONF_REFRESH_TOKEN: refresh_token,
                        CONF_USER_ID: user_id,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]
                    },
                )
            except Exception as e:
                _LOGGER.error(f'Invalid credentials: {e}')
                errors['base'] = 'invalid_credentials'

        data_schema = vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,

            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })

        return self.async_show_form(step_id='user', data_schema=data_schema, errors=errors)
