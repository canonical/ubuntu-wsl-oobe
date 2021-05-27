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
