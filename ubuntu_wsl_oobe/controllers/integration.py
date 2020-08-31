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
import subprocess

from subiquitycore.controller import BaseController
from subiquitycore.utils import run_command
from ubuntu_wsl_oobe.ui.views import IntegrationView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.integration')


class IntegrationController(BaseController):
    integration_view = IntegrationView

    def start_ui(self):
        view = self.integration_view(self)
        self.ui.set_body(view)

    def done(self, result):
        user_settings = result.copy()
        if not self.opts.dry_run:
            # reset to keep everything as refreshed as new
            run_command(["/usr/bin/ubuntuwsl", "reset", "-y"], stdout=subprocess.DEVNULL)
            # set the settings
            run_command(["/usr/bin/ubuntuwsl", "update", "Ubuntu.Interop.guiintegration", user_settings['gui_integration']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.automount.root", user_settings['custom_path']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.automount.options", user_settings['custom_mount_opt']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.network.generatehosts", user_settings['gen_host']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.network.generateresolvconf", user_settings['gen_resolvconf']],
                        stdout=subprocess.DEVNULL)
        self.app.next_screen()

    def cancel(self):
        self.app.cancel()
