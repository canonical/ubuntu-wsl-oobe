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
###################################################
# This is a reimplementation for subiquitycore.core
# due to the issue that it is made for subiquity
###################################################

import platform
import re
import asyncio
import fcntl
import json
import logging
import os
import pathlib
import struct
import sys
import tty

import urwid
import yaml

from subiquitycore.prober import Prober
from subiquitycore.async_helpers import schedule_task
from subiquitycore.context import (
    Context,
    )
from subiquitycore.controller import (
    Skip,
    )
from subiquitycore.signals import Signal
from subiquitycore.ui.frame import SubiquityCoreUI
from subiquitycore.utils import arun_command

log = logging.getLogger('subiquitycore.core')


# From uapi/linux/kd.h:
KDGKBTYPE = 0x4B33  # get keyboard type

GIO_CMAP = 0x4B70  # gets colour palette on VGA+
PIO_CMAP = 0x4B71  # sets colour palette on VGA+
UO_R, UO_G, UO_B = 0xe9, 0x54, 0x20

# /usr/include/linux/kd.h
K_RAW = 0x00
K_XLATE = 0x01
K_MEDIUMRAW = 0x02
K_UNICODE = 0x03
K_OFF = 0x04

KDGKBMODE = 0x4B44  # gets current keyboard mode
KDSKBMODE = 0x4B45  # sets current keyboard mode


def is_wsl():
    # return true if it is WSL, otherwise return false
    return pathlib.Path("/proc/sys/fs/binfmt_misc/WSLInterop").is_file()


def is_linux_tty():
    try:
        r = fcntl.ioctl(sys.stdout.fileno(), KDGKBTYPE, ' ')
    except IOError as e:
        log.debug("KDGKBTYPE failed %r", e)
        return False
    log.debug("KDGKBTYPE returned %r, is_linux_tty %s", r, r == b'\x02')
    return r == b'\x02'


class WSLScreen(urwid.raw_display.Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write(self, data):
        if is_wsl() != 0:
            data = re.sub("[\x0e\x0f]", "", data)
        super().write(data)


class TwentyFourBitScreen(WSLScreen):

    def __init__(self, _urwid_name_to_rgb, **kwargs):
        self._urwid_name_to_rgb = _urwid_name_to_rgb
        super().__init__(**kwargs)

    def _cc(self, color):
        """Return the "SGR" parameter for selecting color.

        See https://en.wikipedia.org/wiki/ANSI_escape_code#SGR for an
        explanation.  We use the basic codes for black/white/default for
        maximum compatibility; they are the only colors used when the
        mono palette is selected.
        """
        if color == 'white':
            return '7'
        elif color == 'black':
            return '0'
        elif color == 'default':
            return '9'
        else:
            # This is almost but not quite a ISO 8613-3 code -- that
            # would use colons to separate the rgb values instead. But
            # it's what xterm, and hence everything else, supports.
            return '8;2;{};{};{}'.format(*self._urwid_name_to_rgb[color])

    def _attrspec_to_escape(self, a):
        return '\x1b[0;3{};4{}m'.format(
            self._cc(a.foreground),
            self._cc(a.background))


urwid_8_names = (
    'black',
    'dark red',
    'dark green',
    'brown',
    'dark blue',
    'dark magenta',
    'dark cyan',
    'light gray',
)


def make_palette(colors, styles):
    """Return a palette to be passed to MainLoop.

    colors is a list of exactly 8 tuples (name, (r, g, b))

    styles is a list of tuples (stylename, fg_color, bg_color) where
    fg_color and bg_color are defined in 'colors'
    """
    # The part that makes this "fun" is that urwid insists on referring
    # to the basic colors by their "standard" names but we overwrite
    # these colors to mean different things.  So we convert styles into
    # an urwid palette by mapping the names in colors to the standard
    # name.
    if len(colors) != 8:
        raise Exception(
            "make_palette must be passed a list of exactly 8 colors")
    urwid_name = dict(zip([c[0] for c in colors], urwid_8_names))

    urwid_palette = []
    for name, fg, bg in styles:
        urwid_fg, urwid_bg = urwid_name[fg], urwid_name[bg]
        urwid_palette.append((name, urwid_fg, urwid_bg))

    return urwid_palette


def extend_dec_special_charmap():
    urwid.escape.DEC_SPECIAL_CHARMAP.update({
        ord('\N{BLACK RIGHT-POINTING SMALL TRIANGLE}'): '>',
        ord('\N{BLACK LEFT-POINTING SMALL TRIANGLE}'): '<',
        ord('\N{BLACK DOWN-POINTING SMALL TRIANGLE}'): 'v',
        ord('\N{BLACK UP-POINTING SMALL TRIANGLE}'): '^',
        ord('\N{check mark}'): '+',
        ord('\N{bullet}'): '*',
        ord('\N{lower half block}'): '=',
        ord('\N{upper half block}'): '=',
        ord('\N{FULL BLOCK}'): urwid.escape.DEC_SPECIAL_CHARMAP[
            ord('\N{BOX DRAWINGS LIGHT VERTICAL}')],
    })


class KeyCodesFilter:
    """input_filter that can pass (medium) raw keycodes to the application

    See http://lct.sourceforge.net/lct/x60.html for terminology.

    Call enter_keycodes_mode()/exit_keycodes_mode() to switch into and
    out of keycodes mode. In keycodes mode, the only events passed to
    the application are "press $N" / "release $N" where $N is the
    keycode the user pressed or released.

    Much of this is cribbed from the source of the "showkeys" utility.
    """

    def __init__(self):
        self._fd = os.open("/proc/self/fd/"+str(sys.stdin.fileno()), os.O_RDWR)
        self.filtering = False

    def enter_keycodes_mode(self):
        log.debug("enter_keycodes_mode")
        self.filtering = True
        # Read the old keyboard mode (it will proably always be K_UNICODE but
        # well).
        o = bytearray(4)
        fcntl.ioctl(self._fd, KDGKBMODE, o)
        self._old_mode = struct.unpack('i', o)[0]
        # Set the keyboard mode to K_MEDIUMRAW, which causes the keyboard
        # driver in the kernel to pass us keycodes.
        fcntl.ioctl(self._fd, KDSKBMODE, K_MEDIUMRAW)

    def exit_keycodes_mode(self):
        log.debug("exit_keycodes_mode")
        self.filtering = False
        fcntl.ioctl(self._fd, KDSKBMODE, self._old_mode)

    def filter(self, keys, codes):
        # Luckily urwid passes us the raw results from read() we can
        # turn into keycodes.
        if self.filtering:
            i = 0
            r = []
            n = len(codes)
            while i < len(codes):
                # This is straight from showkeys.c.
                if codes[i] & 0x80:
                    p = 'release '
                else:
                    p = 'press '
                if i + 2 < n and (codes[i] & 0x7f) == 0:
                    if (codes[i + 1] & 0x80) != 0:
                        if (codes[i + 2] & 0x80) != 0:
                            kc = (((codes[i + 1] & 0x7f) << 7) |
                                  (codes[i + 2] & 0x7f))
                            i += 3
                else:
                    kc = codes[i] & 0x7f
                    i += 1
                r.append(p + str(kc))
            return r
        else:
            return keys


class DummyKeycodesFilter:
    # A dummy implementation of the same interface as KeyCodesFilter
    # we can use when not running in a linux tty.

    def enter_keycodes_mode(self):
        pass

    def exit_keycodes_mode(self):
        pass

    def filter(self, keys, codes):
        return keys


class AsyncioEventLoop(urwid.AsyncioEventLoop):
    # This is fixed in the latest urwid.

    def _exception_handler(self, loop, context):
        exc = context.get('exception')
        if exc:
            log.debug("_exception_handler %r", exc)
            loop.stop()
            if not isinstance(exc, urwid.ExitMainLoop):
                # Store the exc_info so we can re-raise after the loop stops
                self._exc_info = (type(exc), exc, exc.__traceback__)
        else:
            loop.default_exception_handler(context)


class ControllerSet:

    def __init__(self, app, names):
        self.app = app
        self.controller_names = names[:]
        self.index = -1
        self.instances = []
        self.controllers_mod = __import__(
            '{}.controllers'.format(self.app.project), None, None, [''])

    def _get_controller_class(self, name):
        return getattr(self.controllers_mod, name+"Controller")

    def load(self, name):
        self.controller_names.remove(name)
        log.debug("Importing controller: %s", name)
        klass = self._get_controller_class(name)
        if hasattr(self, name):
            c = 1
            for instance in self.instances:
                if isinstance(instance, klass):
                    c += 1
            rep_cls = self._get_controller_class("Repeated")
            inst = rep_cls(getattr(self, name), c)
            name = inst.name
        else:
            inst = klass(self.app)
        setattr(self, name, inst)
        self.instances.append(inst)

    def load_all(self):
        while self.controller_names:
            self.load(self.controller_names[0])

    @property
    def cur(self):
        if self.out_of_bounds():
            return None
        return self.instances[self.index]

    def out_of_bounds(self):
        return self.index < 0 or self.index >= len(self.instances)


class Application:

    make_ui = SubiquityCoreUI

    def __init__(self, opts):
        self.debug_flags = ()
        if opts.dry_run:
            # Recognized flags are:
            #  - install-fail: makes curtin install fail by replaying curtin
            #    events from a failed installation, see
            #    subiquity/controllers/installprogress.py
            #  - bpfail-full, bpfail-restricted: makes block probing fail, see
            #    subiquitycore/prober.py
            #  - copy-logs-fail: makes post-install copying of logs fail, see
            #    subiquity/controllers/installprogress.py
            self.debug_flags = os.environ.get('SUBIQUITY_DEBUG', '').split(',')

        prober = Prober(opts.machine_config, self.debug_flags)

        self.ui = self.make_ui()
        self.opts = opts
        opts.project = self.project

        self.root = '/'
        if opts.dry_run:
            self.root = '.subiquity'
        self.state_dir = os.path.join(self.root, 'run', self.project)
        os.makedirs(self.state_path('states'), exist_ok=True)

        self.answers = {}
        if opts.answers is not None:
            self.answers = yaml.safe_load(opts.answers.read())
            log.debug("Loaded answers %s", self.answers)
            if not opts.dry_run:
                open('/run/casper-no-prompt', 'w').close()

        # Set rich_mode to the opposite of what we want, so we can
        # call toggle_rich to get the right things set up.
        self.rich_mode = opts.run_on_serial
        self.color_palette = make_palette(self.COLORS, self.STYLES)

        self.is_linux_tty = is_linux_tty()
        self.is_wsl = is_wsl()

        if self.is_linux_tty:
            self.input_filter = KeyCodesFilter()
        else:
            self.input_filter = DummyKeycodesFilter()

        self.scale_factor = float(
            os.environ.get('SUBIQUITY_REPLAY_TIMESCALE', "1"))
        self.updated = os.path.exists(self.state_path('updating'))
        self.signal = Signal()
        self.new_event_loop()
        self.prober = prober
        self.urwid_loop = None
        self.controllers = ControllerSet(self, self.controllers)
        self.context = Context.new(self)

    def new_event_loop(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.aio_loop = new_loop

    def run_command_in_foreground(self, cmd, before_hook=None, after_hook=None,
                                  **kw):
        screen = self.urwid_loop.screen

        # Calling screen.stop() sends the INPUT_DESCRIPTORS_CHANGED
        # signal. This calls _reset_input_descriptors() which calls
        # unhook_event_loop / hook_event_loop on the screen. But this all
        # happens before _started is set to False on the screen and so this
        # does not actually do anything -- we end up attempting to read from
        # stdin while in a background process group, something that gets the
        # kernel upset at us.
        #
        # The cleanest fix seems to be to just send the signal again once
        # stop() has returned which, now that screen._started is False,
        # correctly stops listening from stdin.
        #
        # There is an exactly analagous problem with screen.start() except
        # there the symptom is that we are running in the foreground but not
        # listening to stdin! The fix is the same.

        async def _run():
            await arun_command(
                cmd, stdin=None, stdout=None, stderr=None, **kw)
            screen.start()
            urwid.emit_signal(
                screen, urwid.display_common.INPUT_DESCRIPTORS_CHANGED)
            self.setraw()
            if after_hook is not None:
                after_hook()

        screen.stop()
        urwid.emit_signal(
            screen, urwid.display_common.INPUT_DESCRIPTORS_CHANGED)
        if before_hook is not None:
            before_hook()
        schedule_task(_run())

    def _connect_base_signals(self):
        """Connect signals used in the core controller."""
        # Registers signals from each controller
        for controller in self.controllers.instances:
            controller.register_signals()
        log.debug("known signals: %s", self.signal.known_signals)

    def state_path(self, *parts):
        return os.path.join(self.state_dir, *parts)

    def save_state(self):
        cur = self.controllers.cur
        if cur is None:
            return
        with open(self.state_path('states', cur.name), 'w') as fp:
            json.dump(cur.serialize(), fp)

    def select_screen(self, new):
        new.context.enter("starting UI")
        if self.opts.screens and new.name not in self.opts.screens:
            raise Skip
        try:
            new.start_ui()
        except Skip:
            new.context.exit("(skipped)")
            raise
        with open(self.state_path('last-screen'), 'w') as fp:
            fp.write(new.name)

    def _move_screen(self, increment):
        self.save_state()
        old = self.controllers.cur
        if old is not None:
            old.context.exit("completed")
            old.end_ui()
        cur_index = self.controllers.index
        while True:
            self.controllers.index += increment
            if self.controllers.index < 0:
                self.controllers.index = cur_index
                return
            if self.controllers.index >= len(self.controllers.instances):
                self.exit()
            new = self.controllers.cur
            try:
                self.select_screen(new)
            except Skip:
                log.debug("skipping screen %s", new.name)
                continue
            else:
                return

    def fast_forward_screen(self, *args):
        self._move_screen(2)

    def next_screen(self, *args):
        self._move_screen(1)

    def prev_screen(self, *args):
        self._move_screen(-1)

    def select_initial_screen(self, controller_index):
        self.controllers.index = controller_index - 1
        self.next_screen()

    def report_start_event(self, context, description):
        log = logging.getLogger(context.full_name())
        level = getattr(logging, context.level)
        log.log(level, "start: %s", description)

    def report_finish_event(self, context, description, status):
        log = logging.getLogger(context.full_name())
        level = getattr(logging, context.level)
        log.log(level, "finish: %s %s", description, status.name)

# EventLoop -------------------------------------------------------------------

    def _remove_last_screen(self):
        last_screen = self.state_path('last-screen')
        if os.path.exists(last_screen):
            os.unlink(last_screen)

    def exit(self):
        self._remove_last_screen()
        self.aio_loop.stop()

    def run_scripts(self, scripts):
        # run_scripts runs (or rather arranges to run, it's all async)
        # a series of python snippets in a helpful namespace. This is
        # all in aid of being able to test some part of the UI without
        # having to click the same buttons over and over again to get
        # the UI to the part you are working on.
        #
        # In the namespace are:
        #  * everything from view_helpers
        #  * wait, delay execution of subsequent scripts for a while
        #  * c, a function that finds a button and clicks it. uses
        #    wait, above to wait for the button to appear in case it
        #    takes a while.
        from subiquitycore.testing import view_helpers

        class ScriptState:
            def __init__(self):
                self.ns = view_helpers.__dict__.copy()
                self.waiting = False
                self.wait_count = 0
                self.scripts = scripts

        ss = ScriptState()

        def _run_script():
            log.debug("running %s", ss.scripts[0])
            exec(ss.scripts[0], ss.ns)
            if ss.waiting:
                return
            ss.scripts = ss.scripts[1:]
            if ss.scripts:
                self.aio_loop.call_soon(_run_script)

        def c(pat):
            but = view_helpers.find_button_matching(self.ui, '.*' + pat + '.*')
            if not but:
                ss.wait_count += 1
                if ss.wait_count > 10:
                    raise Exception("no button found matching %r after"
                                    "waiting for 10 secs" % pat)
                wait(1, func=lambda: c(pat))
                return
            ss.wait_count = 0
            view_helpers.click(but)

        def wait(delay, func=None):
            ss.waiting = True

            def next():
                ss.waiting = False
                if func is not None:
                    func()
                if not ss.waiting:
                    ss.scripts = ss.scripts[1:]
                    if ss.scripts:
                        _run_script()
            self.aio_loop.call_later(delay, next)

        ss.ns['c'] = c
        ss.ns['wait'] = wait
        ss.ns['ui'] = self.ui

        self.aio_loop.call_later(0.06, _run_script)

    def toggle_rich(self):
        if self.rich_mode:
            urwid.util.set_encoding('ascii')
            new_palette = self.STYLES_MONO
            self.rich_mode = False
        else:
            urwid.util.set_encoding('utf-8')
            new_palette = self.color_palette
            self.rich_mode = True
        urwid.CanvasCache.clear()
        self.urwid_loop.screen.register_palette(new_palette)
        self.urwid_loop.screen.clear()

    def unhandled_input(self, key):
        if self.opts.dry_run and key == 'ctrl x':
            self.exit()
        elif key == 'f3':
            self.urwid_loop.screen.clear()
        elif self.opts.run_on_serial and key in ['ctrl t', 'f4']:
            self.toggle_rich()

    def start_controllers(self):
        log.debug("starting controllers")
        for controller in self.controllers.instances:
            controller.start()
        log.debug("controllers started")

    def load_serialized_state(self):
        for controller in self.controllers.instances:
            state_path = self.state_path('states', controller.name)
            if not os.path.exists(state_path):
                continue
            with open(state_path) as fp:
                controller.deserialize(json.load(fp))

        last_screen = None
        state_path = self.state_path('last-screen')
        if os.path.exists(state_path):
            with open(state_path) as fp:
                last_screen = fp.read().strip()
        controller_index = 0
        for i, controller in enumerate(self.controllers.instances):
            if controller.name == last_screen:
                controller_index = i
        # Screens that have already been seen should be marked as configured.
        for controller in self.controllers.instances[:controller_index]:
            controller.configured()
        return controller_index

    def setraw(self):
        fd = self.urwid_loop.screen._term_input_file.fileno()
        if os.isatty(fd):
            tty.setraw(fd)

    def make_screen(self, inputf=None, outputf=None):
        """Return a screen to be passed to MainLoop.

        colors is a list of exactly 8 tuples (name, (r, g, b)), the same as
        passed to make_palette.
        """
        # On the linux console, we overwrite the first 8 colors to be those
        # defined by colors. Otherwise, we return a screen that uses ISO
        # 8613-3ish codes to display the colors.
        if inputf is None:
            inputf = sys.stdin
        if outputf is None:
            outputf = sys.stdout

        if len(self.COLORS) != 8:
            raise Exception(
                "make_screen must be passed a list of exactly 8 colors")
        if self.is_linux_tty:
            # Perhaps we ought to return a screen subclass that does this
            # ioctl-ing in .start() and undoes it in .stop() but well.
            if self.is_wsl:
                _urwid_name_to_rgb = {}
                for i, n in enumerate(urwid_8_names):
                    _urwid_name_to_rgb[n] = self.COLORS[i][1]
                return TwentyFourBitScreen(_urwid_name_to_rgb,
                                           input=inputf, output=outputf)
            else:
                curpal = bytearray(16*3)
                fcntl.ioctl(sys.stdout.fileno(), GIO_CMAP, curpal)
                for i in range(8):
                    for j in range(3):
                        curpal[i*3+j] = self.COLORS[i][1][j]
                fcntl.ioctl(sys.stdout.fileno(), PIO_CMAP, curpal)
                return WSLScreen(input=inputf, output=outputf)
        elif self.opts.ascii:
            return WSLScreen(input=inputf, output=outputf)
        else:
            _urwid_name_to_rgb = {}
            for i, n in enumerate(urwid_8_names):
                _urwid_name_to_rgb[n] = self.COLORS[i][1]
            return TwentyFourBitScreen(_urwid_name_to_rgb,
                                       input=inputf, output=outputf)

    def run(self, input=None, output=None):
        log.debug("Application.run")
        screen = self.make_screen(input, output)

        self.urwid_loop = urwid.MainLoop(
            self.ui, palette=self.color_palette, screen=screen,
            handle_mouse=False, pop_ups=True,
            input_filter=self.input_filter.filter,
            unhandled_input=self.unhandled_input,
            event_loop=AsyncioEventLoop(loop=self.aio_loop))

        extend_dec_special_charmap()

        self.toggle_rich()

        self.base_model = self.make_model()
        try:
            if self.opts.scripts:
                self.run_scripts(self.opts.scripts)

            self.controllers.load_all()

            initial_controller_index = 0

            if self.updated:
                initial_controller_index = self.load_serialized_state()

            self.aio_loop.call_soon(self.setraw)
            self.aio_loop.call_soon(
                self.select_initial_screen, initial_controller_index)
            self._connect_base_signals()

            self.start_controllers()

            self.urwid_loop.run()
        except Exception:
            log.exception("Exception in controller.run():")
            raise
