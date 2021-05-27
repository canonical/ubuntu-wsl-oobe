import logging
import os

from subiquitycore.controller import BaseController
from subiquitycore.utils import run_command
from ubuntu_wsl_oobe.ui.views import WelcomeView, AlreadyCreatedView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.welcome')


class WelcomeController(BaseController):
    model_name = "locale"

    def __init__(self, app):
        super().__init__(app)
        self.autoinstall_applied = False
        self.context.set('controller', self)

    def start(self):
        lang = os.environ.get("LANG")
        if lang is not None and lang.endswith(".UTF-8"):
            lang = lang.rsplit('.', 1)[0]
        for code, name in self.model.get_languages(self.app.is_linux_tty):
            if code == lang:
                self.model.switch_language(code)
                break
        else:
            self.model.selected_language = lang

    def start_ui(self):
        # clean up old account setup if exist (although there is possibly none)
        if self.opts.dry_run:
            run_command(["/usr/bin/rm", "-rf", "/var/lib/ubuntu-wsl/assigned_account"])
        view = WelcomeView(self.model, self)
        if os.path.exists("/var/lib/ubuntu-wsl/assigned_account"):
            view = AlreadyCreatedView(self)
        self.ui.set_body(view)

    def interactive(self):
        if not self.app.autoinstall_config:
            return True
        i_sections = self.app.autoinstall_config.get(
            'interactive-sections', [])
        if '*' in i_sections:
            return True
        return False

    def configured(self):
        """Let the world know that this controller's model is now configured.
        """
        if self.model_name is not None:
            self.app.base_model.configured(self.model_name)

    def done(self, code):
        log.debug("WelcomeController.done %s next_screen", code)
        self.signal.emit_signal('l10n:language-selected', code)
        self.model.switch_language(code)
        self.configured()
        self.app.next_screen()

    def done_and_exit(self):
        self.app.exit()

    def cancel(self):
        # Can't go back from here!
        pass

    def serialize(self):
        return self.model.selected_language

    def deserialize(self, data):
        self.model.switch_language(data)


class AlreadyCreatedController(BaseController):

    def __init__(self, app):
        super().__init__(app)

    def start_ui(self):
        pass

    def cancel(self):
        pass





