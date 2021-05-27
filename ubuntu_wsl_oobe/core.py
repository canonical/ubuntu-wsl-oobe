import logging

from ubuntu_wsl_oobe.helpers.core import Application
from ubuntu_wsl_oobe.models.ubuntu_wsl_oobe import OOBEModel

log = logging.getLogger("ubuntu_wsl_oobe.core")


class UbuntuWslOobe(Application):

    from subiquitycore.palette import COLORS, STYLES, STYLES_MONO

    project = "ubuntu_wsl_oobe"

    make_model = OOBEModel

    controllers = [
        "Welcome",
        "Identity",
        "Integration",
        "Overview"
    ]
