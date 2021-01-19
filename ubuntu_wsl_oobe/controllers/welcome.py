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
import os

from subiquitycore.controller import BaseController
from subiquitycore.ui.buttons import done_btn
from subiquitycore.ui.utils import button_pile, screen
from subiquitycore.utils import run_command
from subiquitycore.view import BaseView
from ubuntu_wsl_oobe.ui.views import WelcomeView

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
            run_command(["/usr/bin/rm", "-rf", "/tmp/ubuntu-wsl-oobe/created_account"])
        view = WelcomeView(self.model, self)
        if os.path.exists("/tmp/ubuntu-wsl-oobe/created_account"):
            view = AlreadyCreatedView()
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

    def cancel(self):
        # Can't go back from here!
        pass

    def serialize(self):
        return self.model.selected_language

    def deserialize(self, data):
        self.model.switch_language(data)


class AlreadyCreatedView(BaseView):
    title = _("Ubuntu WSL - Already Completed")

    def __init__(self):
        complete_text = _("You have already completed setup. Aborted.")

        super().__init__(
            screen(
                rows=[],
                buttons=button_pile(
                    [done_btn(_("Done"), on_press=self.confirm), ]),
                focus_buttons=True,
                excerpt=complete_text,
            )
        )

    def confirm(self, wah):
        self.done()

    def done(self):
        self.app.exit()

