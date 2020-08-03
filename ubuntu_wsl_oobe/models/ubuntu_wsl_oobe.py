from .identity import IdentityModel
from .locale import LocaleModel


class ConsoleConfModel:
    """The overall model for console-conf."""

    def __init__(self):
        self.identity = IdentityModel()
        self.locale = LocaleModel()
