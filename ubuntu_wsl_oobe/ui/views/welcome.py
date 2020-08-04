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
import os
from urwid import Text

from subiquitycore.ui.buttons import forward_btn, other_btn
from subiquitycore.ui.container import ListBox
from subiquitycore.ui.utils import button_pile, rewrap, screen
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.views.welcome")


HELP = _("""
Select the language to use for the installer and to be configured in the
installed system.
""")


class WelcomeView(BaseView):
    title = "Bienvenue! Welcome! Welkom!"
    extented_title = title + " 歡迎！こんにちは！"

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.fallback_mode_checked = False
        s = self.make_language_choices()
        super().__init__(s)

    def make_language_choices(self):
        btns = []
        current_index = None
        excerpt_context = _("Use UP, DOWN and ENTER keys to select your language.")
        extented_excerpt_context = _("You are using old Windows Console Host, Entering fallback mode. Use Windows Terminal to get more language options.") + "\n\n" + excerpt_context
        if not self.fallback_mode_checked:
            if "WT_PROFILE_ID" in os.environ:
                self.__class__.title = self.__class__.extented_title
            else:
                excerpt_context = extented_excerpt_context
            self.fallback_mode_checked = True
        
        langs = self.model.get_languages("WT_PROFILE_ID" not in os.environ)
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
            excerpt=excerpt_context)

    def choose_language(self, sender, code):
        log.debug('WelcomeView %s', code)
        self.controller.done(code)

    def local_help(self):
        return _("Help choosing a language"), _(HELP)