""" Identity

Identity helps user set up user accounts.

"""

import logging
import os
import re

from urwid import connect_signal
from subiquitycore.ui.form import (
    Form,
    simple_field,
    WantsToKnowFormField,
    BooleanField, Toggleable
)
from subiquitycore.ui.interactive import (
    PasswordEditor,
    StringEditor,
)
from subiquitycore.ui.utils import screen
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.views.identity")

HOSTNAME_MAXLEN = 64
REALNAME_MAXLEN = 160
SSH_IMPORT_MAXLEN = 256 + 3  # account for lp: or gh:
USERNAME_MAXLEN = 32


class UsernameEditor(StringEditor, WantsToKnowFormField):
    def __init__(self):
        self.valid_char_pat = r'[-a-z0-9_]'
        self.error_invalid_char = _("The only characters permitted in this "
                                    "field are a-z, 0-9, _ and -")
        super().__init__()

    def valid_char(self, ch):
        if len(ch) == 1 and not re.match(self.valid_char_pat, ch):
            self.bff.in_error = True
            self.bff.show_extra(("info_error", self.error_invalid_char))
            return False
        else:
            return super().valid_char(ch)


UsernameField = simple_field(UsernameEditor)
PasswordField = simple_field(PasswordEditor)


class IdentityForm(Form):

    def __init__(self, reserved_usernames, initial):
        self.reserved_usernames = reserved_usernames
        super().__init__(initial=initial)

    username = UsernameField(_("Pick a username:"), help=_("The username does not need to match your Windows username"))
    password = PasswordField(_("Choose a password:"))
    confirm_password = PasswordField(_("Confirm your password:"))
    show_advanced = BooleanField(_("Show Advanced Options Next Page"))

    def validate_username(self):
        username = self.username.value
        if len(username) < 1:
            return _("Username missing")

        if len(username) > USERNAME_MAXLEN:
            return _(
                "Username too long, must be less than {limit}"
            ).format(limit=USERNAME_MAXLEN)

        if not re.match(r'[a-z_][a-z0-9_-]*', username):
            return _("Username must match NAME_REGEX, i.e. [a-z_][a-z0-9_-]*")

        if username in self.reserved_usernames:
            return _(
                'The username "{username}" is reserved for use by the system.'
            ).format(username=username)

    def validate_password(self):
        if len(self.password.value) < 1:
            return _("Password must be set")

    def validate_confirm_password(self):
        if self.password.value != self.confirm_password.value:
            return _("Passwords do not match")

    def validate_show_advanced(self):
        pass


def setup_password_validation(form, desc):
    def _check_password(sender, new_text):
        password = form.password.value
        if not password.startswith(new_text):
            form.confirm_password.show_extra(
                # desc is "passwords" or "passphrases"
                ("info_error", _("{desc} do not match").format(desc=desc)))
        else:
            form.confirm_password.show_extra('')

    connect_signal(
        form.confirm_password.widget, 'change', _check_password)


class IdentityView(BaseView):
    title = _("Ubuntu WSL - Profile Setup")
    excerpt = _("Please create a default UNIX user account. "
                "For more information visit: https://aka.ms/wslusers")

    def __init__(self, model, controller):
        self.model = model
        self.controller = controller
        self.signal = controller.signal

        reserved_usernames_path = '/usr/share/ubuntu-wsl-oobe/reserved-usernames'
        build_reserved_usernames_path = os.path.realpath(__file__ + '/../../../../reserved-usernames')
        if os.path.isfile(build_reserved_usernames_path):
            reserved_usernames_path = build_reserved_usernames_path
        reserved_usernames = set()
        if os.path.exists(reserved_usernames_path):
            with open(reserved_usernames_path) as fp:
                for line in fp:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    reserved_usernames.add(line)
        else:
            reserved_usernames.add('root')

        if model.user:
            initial = {
                'username': model.user.username
            }
        else:
            initial = {}

        self.form = IdentityForm(reserved_usernames, initial)

        connect_signal(self.form, 'submit', self.done)
        setup_password_validation(self.form, _("passwords"))

        super().__init__(
            screen(
                self.form.as_rows(),
                [self.form.done_btn],
                excerpt=_(self.excerpt),
                focus_buttons=False))

    def done(self, result):
        result = {
            "username": self.form.username.value,
            "password": self.model.encrypt_password(self.form.password.value),
        }
        self.controller.done(result, self.form.show_advanced.value)
