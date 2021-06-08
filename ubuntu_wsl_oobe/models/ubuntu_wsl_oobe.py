#!/usr/bin/env python3

import asyncio
import logging

from .identity import IdentityModel
from .locale import LocaleModel
from .integration import IntegrationModel

log = logging.getLogger('ubuntu_wsl_oobe.models.ubuntu_wsl_oobe')

ALL_MODEL_NAMES = [
    "identity",
    "locale",
    "integration"
]


class OOBEModel:
    """The overall model for console-conf."""

    def __init__(self):
        self.identity = IdentityModel()
        self.locale = LocaleModel()
        self.integration = IntegrationModel()

        self._events = {
            name: asyncio.Event() for name in ALL_MODEL_NAMES
        }

    def configured(self, model_name):
        log.debug("model %s is configured", model_name)
        self._events[model_name].set()
