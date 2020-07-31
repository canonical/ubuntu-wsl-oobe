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

import attr

from subiquitycore.utils import crypt_password
from subiquitycore.utils import run_command


log = logging.getLogger('subiquity.models.identity')


@attr.s
class User(object):
    username = attr.ib()
    password = attr.ib()


class IdentityModel(object):
    """ Model representing user identity
    """

    def __init__(self):
        self._user = None

    def add_user(self, result):
        result = result.copy()
        self._user = User(**result)
        run_command(["/usr/sbin/useradd", "-m", "-s", "/bin/bash", "-p", result['password'], result['username']])
        run_command(["/usr/sbin/usermod", "-a", "-G", "adm,dialout,cdrom,floppy,sudo,audio,dip,video,plugdev,netdev", result['username']])

    @property
    def user(self):
        return self._user

    def encrypt_password(self, passinput):
        return crypt_password(passinput, 'MD5')

    def __repr__(self):
        return "<LocalUser: {} {}>".format(self.user, self.hostname)
