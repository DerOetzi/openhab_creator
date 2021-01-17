from pathlib import Path
import gettext

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

pwd = (Path(__file__).resolve().parent)

_ = gettext.gettext

gettext.bindtextdomain("messages", f'{pwd}/locale')
gettext.textdomain("messages")
gettext.install("messages")
