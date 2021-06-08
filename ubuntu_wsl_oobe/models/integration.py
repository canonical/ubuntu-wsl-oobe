import logging
import os
import subprocess

import attr

from subiquitycore.utils import run_command

log = logging.getLogger('ubuntu_wsl_oobe.models.identity')


@attr.s
class IntegrationSettings(object):
    custom_path = attr.ib()
    custom_mount_opt = attr.ib()
    gen_host = attr.ib()
    gen_resolvconf = attr.ib()


class IntegrationModel(object):
    """ Model representing integration
    """

    def __init__(self):
        self._integration = None

    def apply_settings(self, result, is_dry_run=False):
        self._integration = IntegrationSettings(**result)
        if not is_dry_run:
            # reset to keep everything as refreshed as new
            run_command(["/usr/bin/ubuntuwsl", "reset", "-y"], stdout=subprocess.DEVNULL)
            # set the settings
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.automount.root", result['custom_path']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.automount.options", result['custom_mount_opt']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.network.generatehosts", result['gen_host']],
                        stdout=subprocess.DEVNULL)
            run_command(["/usr/bin/ubuntuwsl", "update", "WSL.network.generateresolvconf", result['gen_resolvconf']],
                        stdout=subprocess.DEVNULL)
    @property
    def user(self):
        return self._user

    def __repr__(self):
        return "<LocalUser: {} {}>".format(self.user, self.hostname)
