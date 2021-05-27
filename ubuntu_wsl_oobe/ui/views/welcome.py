""" Welcome

Welcome provides user with language selection.

"""

import logging
import os

from subiquitycore.ui.buttons import forward_btn, done_btn
from subiquitycore.ui.container import ListBox
from subiquitycore.ui.utils import screen, button_pile
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.views.welcome")

HELP = _("""
Select the language to use for the installer and to be configured in the
installed system.
""")


class WelcomeView(BaseView):
    title = "Bienvenue! Welcome! Bonvenon!"
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
        extented_excerpt_context = _(
            "You are using old Windows Console Host, Entering fallback mode. "
            "Use Windows Terminal to get more language options.") + "\n\n" + excerpt_context
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


class AlreadyCreatedView(BaseView):
    title = _("Ubuntu WSL - Already Completed")

    def __init__(self, controller):
        complete_text = _("You have already completed setup. Aborted.")

        self.controller = controller

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
        # wah!
        self.controller.done_and_exit()
