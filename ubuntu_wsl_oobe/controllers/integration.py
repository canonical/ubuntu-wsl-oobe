import logging
import subprocess

from subiquitycore.controller import BaseController
from ubuntu_wsl_oobe.ui.views import IntegrationView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.integration')


class IntegrationController(BaseController):
    model_name = "integration"

    def start_ui(self):
        self.ui.set_body(IntegrationView(self.model, self))

    def done(self, user_spec):
        user_spec = user_spec.copy()
        log.debug(
            "IntegrationController.done next_screen user_spec=%s",
            user_spec)
        self.model.apply_settings(user_spec, is_dry_run=self.opts.dry_run)
        self.app.next_screen()

    def cancel(self):
        self.app.cancel()
