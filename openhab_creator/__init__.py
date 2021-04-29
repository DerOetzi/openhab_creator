from pathlib import Path
import gettext

import logging
import sys
import locale
import os

from ._version import get_versions

from enum import Enum

__version__ = get_versions()['version']
del get_versions

logger = logging.getLogger(__name__)


def prepare_language_for_windows():
    if sys.platform == 'win32':
        try:
            import ctypes
        except ImportError:
            return [locale.getdefaultlocale()[0]]

        lcid_user = ctypes.windll.kernel32.GetUserDefaultLCID()
        lcid_system = ctypes.windll.kernel32.GetSystemDefaultLCID()
        if lcid_user != lcid_system:
            lcids = [lcid_user, lcid_system]
        else:
            lcids = [lcid_user]

        languages = list(filter(None, [locale.windows_locale.get(i)
                                       for i in lcids])) or None

        if languages:
            os.environ['LANGUAGE'] = ':'.join(languages)


pwd = Path(__file__).resolve().parent

prepare_language_for_windows()

_ = gettext.gettext

gettext.bindtextdomain("messages", f'{pwd}/locale')
gettext.textdomain("messages")
gettext.install("messages")


class CreatorEnum(Enum):
    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __str__(self) -> str:
        return str(self.value)


class classproperty(object):
    def __init__(self, method=None):
        self.fget = method

    def __get__(self, instance, cls=None):
        return self.fget(cls)

    def getter(self, method):
        self.fget = method
        return self
