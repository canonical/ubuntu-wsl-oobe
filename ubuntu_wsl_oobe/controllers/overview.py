import logging

from subiquitycore.controller import BaseController
from subiquitycore.utils import run_command
from ubuntu_wsl_oobe.ui.views import OverviewView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.identity')


def disable_ubuntu_wsl_oobe():
    """ Stop running ubuntu_wsl_oobe and remove the package """
    log.info('disabling ubuntu-wsl-oobe service')
    run_command(["apt", "remove", "-y", "ubuntu-wsl-oobe", "ubuntu-wsl-oobe-subiquitycore"])
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
