# Copyright 2015 Canonical, Ltd.
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

""" Welcome

Welcome provides user with language selection

"""
import logging

from urwid import Text

from subiquitycore.ui.buttons import forward_btn, other_btn
from subiquitycore.ui.container import ListBox
from subiquitycore.ui.utils import button_pile, rewrap, screen
from subiquitycore.view import BaseView

log = logging.getLogger("subiquity.views.welcome")


HELP = _("""
Select the language to use for the installer and to be configured in the
installed system.
""")


class WelcomeView(BaseView):
    title = "Bienvenue! Welcome! Welkom! Bonvenon! 歡迎！こんにちは！"

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.is_linux_tty = controller.app.is_linux_tty
        s = self.make_language_choices()
        super().__init__(s)

    def make_language_choices(self):
        btns = []
        current_index = None
        langs = self.model.get_languages(self.is_linux_tty)
        cur = self.model.selected_language
        log.debug("_build_model_inputs selected_language=%s", cur)
        if cur in ["C", None]:
            cur = "en_US"
        for i, (code, native) in enumerate(langs):
            log.debug("%s", (code, self.model.selected_language))
            if code == cur:
                current_index = i
            btns.append(
                forward_btn(
                    label=native,
                    on_press=self.choose_language,
                    user_arg=code))

        lb = ListBox(btns)
        if current_index is not None:
            lb.base_widget.focus_position = current_index
        return screen(
            lb, buttons=None, narrow_rows=True,
            excerpt=_("Use UP, DOWN and ENTER keys to select your language."))

    def enable_rich(self, sender):
        self.controller.app.toggle_rich()
        self.title = self.__class__.title
        self.controller.ui.set_header(self.title)
        self._w = self.make_language_choices()

    def ssh_help(self, sender, password):
        menu = self.controller.app.help_menu
        menu.ssh_password = password
        menu.ssh_help()

    def choose_language(self, sender, code):
        log.debug('WelcomeView %s', code)
        self.controller.done(code)

    def local_help(self):
        return _("Help choosing a language"), _(HELP)