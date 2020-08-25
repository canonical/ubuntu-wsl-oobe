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

import attr

log = logging.getLogger("ubuntu_wsl_oobe.models.systems")


@attr.s
class Brand:
    ID = attr.ib()
    username = attr.ib()
    display_name = attr.ib()
    validation = attr.ib()

    def __eq__(self, other):
        return self.ID == other.ID and \
               self.username == other.username and \
               self.display_name == other.display_name and \
               self.validation == other.validation


@attr.s
class SystemModel:
    model = attr.ib()
    brand_id = attr.ib()
    display_name = attr.ib()

    def __eq__(self, other):
        return self.model == other.model and \
               self.brand_id == other.brand_id and \
               self.display_name == other.display_name


@attr.s
class SystemAction:
    title = attr.ib()
    mode = attr.ib()

    def __eq__(self, other):
        return self.title == other.title and \
               self.mode == other.mode


@attr.s
class SelectedSystemAction:
    system = attr.ib()
    action = attr.ib()

    def __eq__(self, other):
        return self.system == other.system and \
               self.action == other.action
