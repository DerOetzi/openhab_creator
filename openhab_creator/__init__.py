from pathlib import Path
import gettext

import logging

from ._version import get_versions

from enum import Enum

__version__ = get_versions()['version']
del get_versions

pwd = (Path(__file__).resolve().parent)

_ = gettext.gettext

gettext.bindtextdomain("messages", f'{pwd}/locale')
gettext.textdomain("messages")
gettext.install("messages")

logger = logging.getLogger(__name__)


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
