#!/usr/bin/env python3
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

import argparse
import logging
import os
import sys

from subiquitycore.log import setup_logger
from ubuntu_wsl_oobe.core import UbuntuWslOobe


class ClickAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.scripts.append("c(" + repr(values) + ")")


def parse_options(argv):
    parser = argparse.ArgumentParser(
        description=(
            'ubuntu-wsl-oobe - Ubuntu WSL Onboarding Experience'),
        prog='ubuntu-wsl-oobe')
    parser.add_argument('--dry-run', action='store_true',
                        dest='dry_run',
                        help='menu-only, do not call installer function')
    parser.add_argument('--ascii', action='store_true',
                        dest='ascii',
                        help='Run the installer in ascii mode.')
    parser.add_argument('--machine-config', metavar='CONFIG',
                        dest='machine_config',
                        help="Don't Probe. Use probe data file")
    parser.add_argument('--screens', action='append', dest='screens',
                        default=[])
    parser.add_argument('--script', metavar="SCRIPT", action='append',
                        dest='scripts', default=[],
                        help=('Execute SCRIPT in a namespace containing view '
                              'helpers and "ui"'))
    parser.add_argument('--answers')
    return parser.parse_args(argv)


LOGDIR = "/var/log/ubuntu-wsl-oobe/"


def main():
    opts = parse_options(sys.argv[1:])
    global LOGDIR
    if opts.dry_run:
        LOGDIR = ".ubuntu_wsl_oobe"
    # disabling run_on_serial at all time
    # WSL is always not on serial
    opts.run_on_serial = False
    setup_logger(dir=LOGDIR)
    logger = logging.getLogger('ubuntu_wsl_oobe')
    logger.info("Starting ubuntu_wsl_oobe v{}".format("0.04"))
    logger.info("Arguments passed: {}".format(sys.argv))

    interface = UbuntuWslOobe(opts)

    interface.run()


if __name__ == '__main__':
    sys.exit(main())
