""" ubuntu-wsl-oobe UI Views """

from .identity import IdentityView
from .integration import IntegrationView
from .overview import OverviewView
from .welcome import WelcomeView, AlreadyCreatedView

__all__ = [
    "IntegrationView",
    "IdentityView",
    "WelcomeView",
    "OverviewView",
    "AlreadyCreatedView"
]
