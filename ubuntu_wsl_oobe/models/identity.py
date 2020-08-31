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
import os

import attr

from subiquitycore.utils import crypt_password
from subiquitycore.utils import run_command

log = logging.getLogger('ubuntu_wsl_oobe.models.identity')


@attr.s
class User(object):
    username = attr.ib()
    password = attr.ib()


class IdentityModel(object):
    """ Model representing user identity
    """

    def __init__(self):
        self._user = None

    def add_user(self, result, is_dry_run=False):
        if is_dry_run:
            result = {'username': "dry-run-user"}
        else:
            result = result.copy()
            self._user = User(**result)

            usergroups_path = '/usr/share/ubuntu-wsl-oobe/usergroups'
            build_usergroups_path = os.path.realpath(__file__ + '/../../../usergroups')
            if os.path.isfile(build_usergroups_path):
                usergroups_path = build_usergroups_path
            user_groups = set()
            if os.path.exists(usergroups_path):
                with open(usergroups_path) as fp:
                    for line in fp:
                        line = line.strip()
                        if line.startswith('#') or not line:
                            continue
                        user_groups.add(line)
            oneline_usergroups = ",".join(user_groups)
            run_command(["/usr/sbin/useradd", "-m", "-s", "/bin/bash", "-p", result['password'], result['username']])
            run_command(["/usr/sbin/usermod", "-a", "-G", oneline_usergroups, result['username']])
        # creating location for UWP to read from
        run_command(["/usr/bin/mkdir", "-p", "/tmp/ubuntu-wsl-oobe/"])
        with open('/tmp/ubuntu-wsl-oobe/created_account', 'w') as configfile:
            configfile.write(result['username'])

    @property
    def user(self):
        return self._user

    def encrypt_password(self, passinput):
        return crypt_password(passinput, 'MD5')

    def __repr__(self):
        return "<LocalUser: {} {}>".format(self.user, self.hostname)
