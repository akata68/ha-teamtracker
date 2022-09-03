"""Adds config flow for TeamTracker."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_LEAGUE_ID,
    CONF_LEAGUE_PATH,
    CONF_SPORT_PATH,
    CONF_TIMEOUT,
    CONF_TEAM_ID,
    DEFAULT_LEAGUE,
    DEFAULT_LEAGUE_PATH,
    DEFAULT_SPORT_PATH,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    LEAGUE_LIST,
    USER_AGENT,
)

JSON_FEATURES = "features"
JSON_PROPERTIES = "properties"
JSON_ID = "id"

_LOGGER = logging.getLogger(__name__)


def _get_schema(hass: Any, user_input: list, default_dict: list) -> Any:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key):
        """Gets default value for key."""
        return user_input.get(key, default_dict.get(key))

    return vol.Schema(
        {
            vol.Required(CONF_LEAGUE_ID, default=_get_default(CONF_LEAGUE_ID)): str,
            vol.Required(CONF_TEAM_ID, default=_get_default(CONF_TEAM_ID)): str,
            vol.Optional(CONF_NAME, default=_get_default(CONF_NAME)): str,
            vol.Optional(CONF_TIMEOUT, default=_get_default(CONF_TIMEOUT)): int,
        }
    )

def _get_path_schema(hass: Any, user_input: list, default_dict: list) -> Any:
    """Gets a schema using the default_dict as a backup."""
    if user_input is None:
        user_input = {}

    def _get_default(key):
        """Gets default value for key."""
        return user_input.get(key, default_dict.get(key))

    return vol.Schema(
        {
            vol.Required(CONF_SPORT_PATH, default=_get_default(CONF_SPORT_PATH)): str,
            vol.Required(CONF_LEAGUE_PATH, default=_get_default(CONF_LEAGUE_PATH)): str,
        }
    )

@config_entries.HANDLERS.register(DOMAIN)
class TeamTrackerScoresFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for TeamTracker."""

    VERSION = 3
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._data = {}
        self._errors = {}

    async def async_step_user(self, user_input={}):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            league_id = user_input[CONF_LEAGUE_ID].upper()
            if league_id == 'XXX':
                self._data.update(user_input)
                return await self.async_step_path()
            for x in range(len(LEAGUE_LIST)):
                if LEAGUE_LIST[x][0] == league_id:
                    user_input.update({CONF_SPORT_PATH: LEAGUE_LIST[x][1]})
                    user_input.update({CONF_LEAGUE_PATH: LEAGUE_LIST[x][2]})
                    self._data.update(user_input)
                    return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
            self._errors["base"] = "league"
        return await self._show_config_form(user_input)


    async def async_step_path(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
        return await self._show_path_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""

        # Defaults
        defaults = {
            CONF_LEAGUE_ID: DEFAULT_LEAGUE,
            CONF_NAME: DEFAULT_NAME,
            CONF_TIMEOUT: DEFAULT_TIMEOUT,
            CONF_TEAM_ID: '',
        }
        _LOGGER.debug("show_config_form() self._errors: %s", self._errors)
        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema(self.hass, user_input, defaults),
            errors=self._errors,
        )

    async def _show_path_form(self, user_input):
        """Show the path form to edit path data."""

        # Defaults
        defaults = {
            CONF_SPORT_PATH: '',
            CONF_LEAGUE_PATH: '',
        }
        return self.async_show_form(
            step_id="path",
            data_schema=_get_path_schema(self.hass, user_input, defaults),
            errors=self._errors,
        )