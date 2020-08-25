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

import attr

from subiquitycore.context import with_context
from subiquitycore.controller import BaseController
from ubuntu_wsl_oobe.ui.views import IdentityView

log = logging.getLogger('ubuntu_wsl_oobe.controllers.identity')


class IdentityController(BaseController):
    autoinstall_key = model_name = "identity"
    autoinstall_schema = {
        'type': 'object',
        'properties': {
            'username': {'type': 'string'},
            'password': {'type': 'string'},
        },
        'required': ['username', 'password'],
        'additionalProperties': False,
    }

    def load_autoinstall_data(self, data):
        if data is not None:
            self.model.add_user(data)

    @with_context()
    async def apply_autoinstall_config(self, context=None):
        if not self.model.user:
            if 'user-data' not in self.app.autoinstall_config:
                raise Exception("no identity data provided")

    def start_ui(self):
        self.ui.set_body(IdentityView(self.model, self))
        if all(elem in self.answers for elem in
               ['realname', 'username', 'password']):
            d = {
                'username': self.answers['username'],
                'password': self.answers['password'],
            }
            self.done(d)

    def cancel(self):
        self.app.prev_screen()

    def done(self, user_spec):
        safe_spec = user_spec.copy()
        safe_spec['password'] = '<REDACTED>'
        log.debug(
            "IdentityController.done next_screen user_spec=%s",
            safe_spec)
        self.model.add_user(user_spec)
        # self.configured()
        self.app.next_screen()

    def make_autoinstall(self):
        if self.model.user is None:
            return {}
        r = attr.asdict(self.model.user)
        return r
