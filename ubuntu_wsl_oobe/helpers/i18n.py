###################################################
# This is a reimplementation for subiquitycore.i18n
# due to the issue that it is made for subiquity
###################################################

import os
import syslog

from subiquitycore import gettext38

syslog.syslog('i18n file is ' + __file__)
localedir = '/usr/share/locale'
build_mo = os.path.realpath(__file__ + '/../../../build/mo/')
if os.path.isdir(build_mo):
    localedir = build_mo
syslog.syslog('Final localedir is ' + localedir)


def switch_language(code='en_US'):
    syslog.syslog('switch_language ' + code)
    fake_trans = os.environ.get("FAKE_TRANSLATE", "0")
    if code != 'en_US' and fake_trans == "mangle":
        def my_gettext(message):
            return "_(%s)" % message
    elif fake_trans not in ("0", ""):
        def my_gettext(message):
            return message
    elif code:
        translation = gettext38.translation('ubuntu_wsl_oobe', localedir=localedir,
                                            languages=[code], fallback=True)

        def my_gettext(message):
            if not message:
                return message
            return translation.gettext(message)
    import builtins
    builtins.__dict__['_'] = my_gettext


switch_language()

__all__ = ['switch_language']
