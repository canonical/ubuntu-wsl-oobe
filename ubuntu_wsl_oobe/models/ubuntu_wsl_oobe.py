from .identity import IdentityModel


class ConsoleConfModel:
    """The overall model for console-conf."""

    def __init__(self):
        self.identity = IdentityModel()
