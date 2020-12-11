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
        with open('/tmp/ubuntu-wsl-oobe/created_account', 'r') as f:
            user_name = f.read()
        complete_text = _("Hi {username},\n"
                          "You have complete the setup!\n\n"
                          "It is suggested to run the following command to update your Ubuntu "
                          "to the latest version:\n\n\n"
                          "  $ sudo apt update\n  $ sudo apt upgrade\n\n\n"
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
