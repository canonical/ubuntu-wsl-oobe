import logging
import os

from ubuntu_wsl_oobe.helpers import i18n

log = logging.getLogger('ubuntu_wsl_oobe.models.locale')


class LocaleModel(object):
    """ Model representing locale selection

    XXX Only represents *language* selection for now.
    """

    selected_language = None

    def get_languages(self, is_old_console):
        lang_path = '/usr/share/ubuntu-wsl-oobe/languagelist'
        build_lang_path = os.path.realpath(__file__ + '/../../../languagelist')
        if os.path.isfile(build_lang_path):
            lang_path = build_lang_path

        languages = []
        with open(lang_path) as lang_file:
            for line in lang_file:
                level, code, name = line.strip().split(':')
                if is_old_console and level == "new_console_only":
                    continue
                languages.append((code, name))
        languages.sort(key=lambda x: x[1])
        return languages

    def switch_language(self, code):
        self.selected_language = code
        i18n.switch_language(code)

    def __repr__(self):
        return "<Selected: {}>".format(self.selected_language)
