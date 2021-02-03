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

""" Integration

Integration provides user with options to set up integration configurations.

"""

import logging
import re

from urwid import (
    connect_signal,
)

from subiquitycore.ui.form import (
    Form,
    BooleanField,
    simple_field,
    WantsToKnowFormField
)
from subiquitycore.ui.interactive import StringEditor
from subiquitycore.ui.utils import screen
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.views.integration")


class MountEditor(StringEditor, WantsToKnowFormField):
    def keypress(self, size, key):
        ''' restrict what chars we allow for mountpoints '''

        mountpoint = r'[a-zA-Z0-9_/\.\-]'
        if re.match(mountpoint, key) is None:
            return False

        return super().keypress(size, key)


MountField = simple_field(MountEditor)
StringField = simple_field(StringEditor)


class IntegrationForm(Form):
    def __init__(self, initial):
        super().__init__(initial=initial)

    custom_path = MountField(_("Mount Location"), help=_("Location for the automount"))
    custom_mount_opt = StringField(_("Mount Option"), help=_("Mount option passed for the automount"))
    gen_host = BooleanField(_("Enable Host Generation"), help=_(
        "Selecting enables /etc/host re-generation at every start"))
    gen_resolvconf = BooleanField(_("Enable resolv.conf Generation"), help=_(
        "Selecting enables /etc/resolv.conf re-generation at every start"))
    gui_integration = BooleanField(_("GUI Integration"), help=_(
        "Selecting enables automatic DISPLAY environment set-up. Third-party X server required."))

    def validate_custom_path(self):
        p = self.custom_path.value
        if p != "" and (re.fullmatch(r"(/[^/ ]*)+/?", p) is None):
            return _("Mount location must be a absolute UNIX path without space.")

    def validate_custom_mount_opt(self):
        o = self.custom_mount_opt.value
        if o != "":
            p = o.split(',')
            x = True
            for i in p:
                if i == "":
                    x = x and False
                elif re.fullmatch(r"(metadata|(u|g)id=\d+|(u|f|d)mask=(4|2|1|0)?[0-7]{3})", i) is not None:
                    x = x and True
                else:
                    x = x and False
            if not x:
                return _("Input is not a valid set of DrvFs mount options. Please check "
                         "https://docs.microsoft.com/en-us/windows/wsl/wsl-config#mount-options "
                         "for correct valid input")


class IntegrationView(BaseView):
    title = _("Ubuntu WSL - Tweaks")
    excerpt = _("In this page, you can tweak Ubuntu WSL to your needs. \n"
    )

    def __init__(self, controller):
        initial = {
            'custom_path': "/mnt/",
            'custom_mount_opt': "",
            'gen_host': True,
            'gen_resolvconf': True,
            'gui_integration': False
        }
        self.form = IntegrationForm(initial=initial)
        self.controller = controller

        connect_signal(self.form, 'submit', self.confirm)
        super().__init__(
            screen(
                self.form.as_rows(),
                [self.form.done_btn],
                focus_buttons=True,
                excerpt=self.excerpt,
            )
        )

    def confirm(self, result):
        yes_no_converter = lambda x: 'true' if x else 'false'
        result = {
            'custom_path': self.form.custom_path.value,
            'custom_mount_opt': self.form.custom_mount_opt.value,
            'gen_host': yes_no_converter(self.form.gen_host.value),
            'gen_resolvconf': yes_no_converter(self.form.gen_resolvconf.value),
            'gui_integration': yes_no_converter(self.form.gui_integration.value)
        }
        self.controller.done(result)
