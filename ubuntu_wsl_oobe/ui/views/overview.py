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
import logging

from urwid import Text

from subiquitycore.ui.buttons import done_btn
from subiquitycore.ui.container import ListBox, Pile
from subiquitycore.ui.utils import button_pile, screen
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.ui.views.overview")


class OverviewView(BaseView):
    title = _("Ubuntu WSL - Setup Complete")

    def __init__(self, controller):
        self.controller = controller
        changelog = _("\n - A brand new Onborading Experience;"
                     "\n - A new commandline tool `ubuntuwslctl` that allows you tweak Ubuntu and WSL settings;"
                     "\n - Update wslu to 3.2.0.")
        complete_text = _("You have complete the setup!\n\n Here is what's new for Ubuntu WSL:\n")
        complete_text += changelog

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
