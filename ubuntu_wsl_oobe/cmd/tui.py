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
import sys
import os
import logging
from subiquitycore.log import setup_logger
from subiquitycore import __version__ as VERSION
from ubuntu_wsl_oobe.core import UbuntuWslOobe


class ClickAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.scripts.append("c(" + repr(values) + ")")


def parse_options(argv):
    parser = argparse.ArgumentParser(
        description=(
            'console-conf - Pre-Ownership Configuration for Ubuntu Core'),
        prog='console-conf')
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
    logger.info("Starting console-conf v{}".format(VERSION))
    logger.info("Arguments passed: {}".format(sys.argv))

    interface = UbuntuWslOobe(opts)

    interface.run()


def restore_std_streams_from(from_file):
    """
    Attempt to restore the original sys.std{in,out} streams by inspecting the
    tty that stderr is hooked up to. Returns the chooser input/output streams.
    """
    tty = os.ttyname(from_file.fileno())
    # we have tty now
    chooser_input, chooser_output = sys.stdin, sys.stdout
    sys.stdin = open(tty, 'r')
    sys.stdout = open(tty, 'w')
    return chooser_input, chooser_output


if __name__ == '__main__':
    sys.exit(main())
