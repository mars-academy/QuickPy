# -*- coding: utf-8 -*-

"""
clint.textui.progress
~~~~~~~~~~~~~~~~~

This module provides the progressbar functionality.

"""

from __future__ import absolute_import

import sys
import time

STREAM = sys.stderr
BAR_TEMPLATE = '{label}[{filled_chars}{empty_chars}] {progress}/{expected_size}{unit} - {etadisp}\r'
BAR_TEMPLATE_WITH_PERCENT = '{label}[{filled_chars}{empty_chars}] ' \
                            '{percent}% ({progress}/{expected_size}){unit} - {etadisp}\r'
MILL_TEMPLATE = '%s %s %i/%i\r'

DOTS_CHAR = '.'
BAR_FILLED_CHAR = '#'
BAR_EMPTY_CHAR = ' '
MILL_CHARS = ['|', '/', '-', '\\']

# How long to wait before recalculating the ETA
ETA_INTERVAL = 1
# How many intervals (excluding the current one) to calculate the simple moving
# average
ETA_SMA_WINDOW = 9


def get_percent(progress, expected_size):
    return progress / expected_size * 100


class Bar(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()
        return False  # we're not suppressing exceptions

    def __init__(self, label: str = '', unit: str = "it", width: int = 32, hide=None, empty_char=BAR_EMPTY_CHAR,
                 filled_char=BAR_FILLED_CHAR, expected_size=None, every=1, show_percent: bool = True):
        self.label = label
        self.width = width
        self.hide = hide
        # Only show bar in terminals by default (better for piping, logging etc.)
        if hide is None:
            try:
                self.hide = not STREAM.isatty()
            except AttributeError:  # output does not support isatty()
                self.hide = True
        self.empty_char = empty_char
        self.filled_char = filled_char
        self.unit = unit
        self.expected_size = expected_size
        self.every = every
        self.show_percent = show_percent

        self.start = time.time()
        self.ittimes = []
        self.eta = 0
        self.etadelta = time.time()
        self.eta_display = self.format_time(self.eta)
        self.last_progress = 0
        self.total_time = 0
        if self.expected_size:
            self.show(0)

    def show(self, progress, count=None):
        if count is not None:
            self.expected_size = count
        if self.expected_size is None:
            raise Exception("expected_size not initialized")
        self.last_progress = progress
        if (time.time() - self.etadelta) > ETA_INTERVAL:
            self.etadelta = time.time()
            self.ittimes = \
                self.ittimes[-ETA_SMA_WINDOW:] + \
                [-(self.start - time.time()) / (progress + 1)]
            self.eta = \
                sum(self.ittimes) / float(len(self.ittimes)) * \
                (self.expected_size - progress)
            self.eta_display = self.format_time(self.eta)
        x = int(self.width * progress / self.expected_size)
        if not self.hide:
            template = BAR_TEMPLATE_WITH_PERCENT if self.show_percent else BAR_TEMPLATE
            STREAM.write(template.format(label=self.label, filled_chars=self.filled_char * x,
                                         empty_chars=self.empty_char * (self.width - x), progress=progress,
                                         percent=get_percent(progress, self.expected_size),
                                         expected_size=self.expected_size, unit=self.unit, etadisp=self.eta_display))
            STREAM.flush()

    def done(self):
        self.total_time = time.time() - self.start
        total_time_display = self.format_time(self.total_time)
        if not self.hide:
            # Print completed bar with elapsed time
            template = BAR_TEMPLATE_WITH_PERCENT if self.show_percent else BAR_TEMPLATE
            STREAM.write(template.format(
                label=self.label, filled_chars=self.filled_char * self.width,
                empty_chars=self.empty_char * 0, progress=self.expected_size, unit=self.unit,
                percent=100, expected_size=self.expected_size, etadisp=total_time_display))
            STREAM.write('\n')
            STREAM.flush()

    @staticmethod
    def format_time(seconds):
        return time.strftime('%H:%M:%S', time.gmtime(seconds))


def bar(it, label='', width=32, hide=None, empty_char=BAR_EMPTY_CHAR,
        filled_char=BAR_FILLED_CHAR, expected_size=None, every=1):
    """Progress iterator. Wrap your iterables with it."""

    count = len(it) if expected_size is None else expected_size

    with Bar(label=label, width=width, hide=hide, empty_char=empty_char,
             filled_char=filled_char, expected_size=count, every=every) \
            as progress_bar:
        for i, item in enumerate(it):
            yield item
            progress_bar.show(i + 1)


def dots(it, label='', hide=None, every=1):
    """Progress iterator. Prints a dot for each item being iterated"""

    count = 0

    if not hide:
        STREAM.write(label)

    for i, item in enumerate(it):
        if not hide:
            if i % every == 0:  # True every "every" updates
                STREAM.write(DOTS_CHAR)
                sys.stderr.flush()

        count += 1

        yield item

    STREAM.write('\n')
    STREAM.flush()


def mill(it, label='', hide=None, expected_size=None, every=1):
    """Progress iterator. Prints a mill while iterating over the items."""

    def _mill_char(_i):
        if _i >= count:
            return ' '
        else:
            return MILL_CHARS[(_i // every) % len(MILL_CHARS)]

    def _show(_i):
        if not hide:
            if ((_i % every) == 0 or  # True every "every" updates
                    (_i == count)):  # And when we're done

                STREAM.write(MILL_TEMPLATE % (
                    label, _mill_char(_i), _i, count))
                STREAM.flush()

    count = len(it) if expected_size is None else expected_size

    if count:
        _show(0)

    for i, item in enumerate(it):
        yield item
        _show(i + 1)

    if not hide:
        STREAM.write('\n')
        STREAM.flush()
