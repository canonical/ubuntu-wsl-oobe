import logging

from subiquitycore.controller import BaseController
from ubuntu_wsl_oobe.ui.views import IdentityView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.identity')


class IdentityController(BaseController):
    model_name = "identity"

    def start_ui(self):
        self.ui.set_body(IdentityView(self.model, self))

    def cancel(self):
        pass

    def done(self, user_spec, show_advanced):
        safe_spec = user_spec.copy()
        safe_spec['password'] = '<REDACTED>'
        log.debug(
            "IdentityController.done next_screen user_spec=%s",
            safe_spec)
        self.model.add_user(user_spec, is_dry_run=self.opts.dry_run)
        if show_advanced:
            self.app.next_screen()
        else:
            self.app.fast_forward_screen()

