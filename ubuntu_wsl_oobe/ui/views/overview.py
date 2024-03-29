""" Overview

Overview provides user with the overview of all the current settings.

"""

import logging

from subiquitycore.ui.buttons import done_btn
from subiquitycore.ui.utils import button_pile, screen
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.ui.views.overview")


class OverviewView(BaseView):
    title = _("Ubuntu WSL - Setup Complete")

    def __init__(self, controller):
        self.controller = controller
        user_name = ""
        with open('/var/lib/ubuntu-wsl/assigned_account', 'r') as f:
            user_name = f.read()
        complete_text = _("Hi {username},\n"
                          "You have complete the setup!\n\n"
                          "It is suggested to run the following command to update your Ubuntu "
                          "to the latest version:\n\n\n"
                          "  $ sudo apt update\n  $ sudo apt upgrade\n\n\n"
                          "You can use the builtin `ubuntuwsl` command to manage your WSL settings:\n\n\n"
                          "  $ sudo ubuntuwsl ...\n\n\n"
                          "* All settings will take effect after first restart of Ubuntu.").format(username=user_name)

        super().__init__(
            screen(
                rows=[],
                buttons=button_pile(
                    [done_btn(_("Done"), on_press=self.confirm), ]),
                focus_buttons=True,
                excerpt=complete_text,
            )
        )

    def confirm(self, result):
        self.controller.done(result)
