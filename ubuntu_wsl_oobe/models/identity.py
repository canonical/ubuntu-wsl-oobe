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
        if not os.path.exists('/var/lib/ubuntu-wsl/'):
            os.makedirs('/var/lib/ubuntu-wsl/')
        with open('/var/lib/ubuntu-wsl/assigned_account', 'w') as configfile:
            configfile.write(result['username'])

    @property
    def user(self):
        return self._user

    def encrypt_password(self, passinput):
        return crypt_password(passinput, 'MD5')

    def __repr__(self):
        return "<LocalUser: {} {}>".format(self.user, self.hostname)
