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

from subiquitycore.controller import BaseController
from subiquitycore.utils import run_command
from ubuntu_wsl_oobe.ui.views import OverviewView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.identity')

def disable_ubuntu_wsl_oobe():
    """ Stop running ubuntu_wsl_oobe and remove the package """
    log.info('disabling ubuntu-wsl-oobe service')
    run_command(["apt", "remove", "-y", "ubuntu-wsl-oobe", "subiquitycore-wsl"])
    return

class OverviewController(BaseController):

    overview_view = OverviewView

    def start_ui(self):
        view = self.overview_view(self)
        self.ui.set_body(view)

    def cancel(self):
        self.app.cancel()

    def done(self, result):
        if not self.opts.dry_run:
            disable_ubuntu_wsl_oobe()
        self.app.exit()
