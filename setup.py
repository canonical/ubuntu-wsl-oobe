#!/usr/bin/env python3
# -*- mode: python; -*-
#
# Copyright 2020 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import distutils.cmd
import distutils.command.build
import distutils.spawn
import glob
import os
import sys

from setuptools import setup, find_packages


class build_i18n(distutils.cmd.Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        data_files = self.distribution.data_files

        with open('po/POTFILES.in') as in_fp:
            with open('po/POTFILES.in.tmp', 'w') as out_fp:
                for line in in_fp:
                    if line.startswith('['):
                        continue
                    out_fp.write('../' + line)

        os.chdir('po')
        distutils.spawn.spawn([
            'xgettext',
            '--directory=.',
            '--add-comments',
            '--from-code=UTF-8',
            '--keyword=pgettext:1c,2',
            '--output=ubuntu_wsl_oobe.pot',
            '--files-from=POTFILES.in.tmp',
            ])
        os.chdir('..')
        os.unlink('po/POTFILES.in.tmp')

        for po_file in glob.glob("po/*.po"):
            lang = os.path.basename(po_file[:-3])
            mo_dir = os.path.join("build", "mo", lang, "LC_MESSAGES")
            mo_file = os.path.join(mo_dir, "ubuntu_wsl_oobe.mo")
            if not os.path.exists(mo_dir):
                os.makedirs(mo_dir)
            distutils.spawn.spawn(["msgfmt", po_file, "-o", mo_file])
            targetpath = os.path.join("share/locale", lang, "LC_MESSAGES")
            data_files.append((targetpath, (mo_file,)))


class build(distutils.command.build.build):

    sub_commands = distutils.command.build.build.sub_commands + [
        ("build_i18n", None)]


if sys.argv[-1] == 'clean':
    print("Cleaning up ...")
    os.system('rm -rf subiquity.egg-info build dist')
    sys.exit()

setup(name='ubuntu_wsl_oobe',
      version='0.0.4',
      description="Ubuntu WSL Onboarding Experience",
      long_description=__doc__,
      author='Patrick Wu',
      author_email='patrick.wu@canonical.com',
      url='https://github.com/canonical/ubuntu-wsl-oobe',
      license="AGPLv3+",
      packages=find_packages(exclude=["tests"]),
      entry_points={
          'console_scripts': [
               'ubuntu-wsl-oobe-tui = ubuntu_wsl_oobe.cmd.tui:main',
          ],
      },
      data_files=[],
      cmdclass={
          'build': build,
          'build_i18n': build_i18n,
          },
      )
