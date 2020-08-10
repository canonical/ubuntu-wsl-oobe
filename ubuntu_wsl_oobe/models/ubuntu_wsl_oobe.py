#!/usr/bin/env python3
# Copyright 2020 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import asyncio

from .identity import IdentityModel
from .locale import LocaleModel

log = logging.getLogger('ubuntu_wsl_oobe.models.ubuntu_wsl_oobe')

ALL_MODEL_NAMES = [
    "identity",
    "locale"
]

class OOBEModel:
    """The overall model for console-conf."""

    def __init__(self):
        self.identity = IdentityModel()
        self.locale = LocaleModel()

        self._events = {
            name: asyncio.Event() for name in ALL_MODEL_NAMES
            }

    def configured(self, model_name):
        log.debug("model %s is configured", model_name)
        self._events[model_name].set()
        