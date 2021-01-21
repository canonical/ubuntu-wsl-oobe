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

from ubuntu_wsl_oobe.helpers.core import Application
from ubuntu_wsl_oobe.models.ubuntu_wsl_oobe import OOBEModel

log = logging.getLogger("ubuntu_wsl_oobe.core")


class UbuntuWslOobe(Application):

    from subiquitycore.palette import COLORS, STYLES, STYLES_MONO

    project = "ubuntu_wsl_oobe"

    make_model = OOBEModel

    controllers = [
        "Welcome",
        "Identity",
        "Integration",
        "Overview"
    ]
