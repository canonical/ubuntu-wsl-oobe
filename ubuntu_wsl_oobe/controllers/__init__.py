""" ubuntu-wsl-oobe controllers """

from .identity import IdentityController
from .integration import IntegrationController
from .overview import OverviewController
from .welcome import WelcomeController

__all__ = [
    'IntegrationController',
    'IdentityController',
    'WelcomeController',
    'OverviewController'
]
