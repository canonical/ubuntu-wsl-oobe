import logging

from urwid import (
    connect_signal,
    )
from subiquitycore.ui.buttons import done_btn, cancel_btn
from subiquitycore.ui.utils import button_pile, screen
from subiquitycore.ui.form import (
    Form,
    BooleanField
)
from subiquitycore.view import BaseView

log = logging.getLogger("ubuntu_wsl_oobe.views.integration")


class IntegrationForm(Form):
    def __init__(self):
        super().__init__()

    gui_integration = BooleanField(_("GUI Integration"), help=_("This enables Automatic DISPLAY environment set-up. Third-party X server required."))
    audio_integration = BooleanField(_("Audio Integration"), help=_("This enables Audio server on WSL. PulseAudio on Windows is required."))
    advanced_detection = BooleanField(_("Advanced Detection"), help=_("This enables Advanced IP Detection to be used in the Integration."))


class IntegrationView(BaseView):
    title = _("Ubuntu WSL - Integration Setup")
    excerpt = _(
        "In this page, you can add some integration to your Ubuntu WSL, to make it suit your needs.\n\n"
    )

    def __init__(self, controller):
        initial = {
            'gui_integration': False,
            'audio_integration': False,
            'advanced_detection': False
        }
        self.form = IntegrationForm()
        self.controller = controller

        connect_signal(self.form, 'submit', self.confirm)
        connect_signal(self.form, 'cancel', self.cancel)
        super().__init__(
            screen(
                self.form.as_rows(),
                [self.form.done_btn, self.form.cancel_btn],
                focus_buttons=True,
                excerpt=self.excerpt,
            )
        )

    def confirm(self, result):
        self.controller.done()

    def cancel(self, button=None):
        self.controller.cancel()
