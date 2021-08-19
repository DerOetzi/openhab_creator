# pylint: skip-file

from core.jsr223.scope import (NULL, OFF, UNDEF, StringType, events,
                               itemRegistry)
from core.log import LOG_PREFIX, logging
from personal.item import Item


class LightUtils(object):
    log = logger.getLogger('{}.LightUtils'.format(LOG_PREFIX))
