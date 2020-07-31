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

from subiquitycore.ui.buttons import done_btn
from subiquitycore.ui.utils import button_pile, screen
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.views.welcome")


class WelcomeView(BaseView):
    title = "Ubuntu WSL"
    excerpt = (
        "Thanks for downloading Ubuntu for WSL!\n"
        "This setup wizard will help you go though several setup:\n\n"
        "- Set up your account;\n"
        "- Set up the Ubuntu WSL/Windows Integration."
    )

    def __init__(self, controller):
        self.controller = controller
        super().__init__(
            screen(
                rows=[],
                buttons=button_pile([done_btn("OK", on_press=self.confirm)]),
                focus_buttons=True,
                excerpt=self.excerpt,
            )
        )

    def confirm(self, result):
        self.controller.done()