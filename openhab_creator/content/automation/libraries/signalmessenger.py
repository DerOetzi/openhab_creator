# pylint: skip-file
from core.log import logging, LOG_PREFIX
from core.actions import Exec

from java.time import Duration

from configuration import PERSONS


class SignalMessenger():

    log = logging.getLogger(u"{}.signalmessenger".format(LOG_PREFIX))

    @staticmethod
    def notification(person, message):
        SignalMessenger.log.info(u'Signal message to %s' % person)
        command = u"/openhab/conf/scripts/signal_user.sh"
        SignalMessenger.log.debug(
            '%s %s %s', command, PERSONS[person], message)
        result = Exec.executeCommandLine(
            Duration.ofSeconds(10), command, PERSONS[person], message)
        SignalMessenger.log.debug('Result %s', result)

    @staticmethod
    def broadcast(message):
        SignalMessenger.notification('broadcast', message)
