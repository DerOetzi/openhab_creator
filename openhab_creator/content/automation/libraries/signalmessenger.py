# pylint: skip-file
from configuration import SIGNAL, SIGNAL_ENDPOINT, SIGNAL_NUMBER
from core.actions import HTTP, Exec
from core.log import LOG_PREFIX, logging
from java.time import Duration

import json

TIMEOUT_MS = 5000


class SignalMessenger():

    log = logging.getLogger(u"{}.signalmessenger".format(LOG_PREFIX))

    @staticmethod
    def notification(person, message):
        SignalMessenger.log.info(u'Signal message to %s' % person)

        send_message = {
            'message': message,
            'number': SIGNAL_NUMBER,
            'recipients': [
                SIGNAL[person]
            ]
        }

        response = HTTP.sendHttpPostRequest('{}/v2/send'.format(SIGNAL_ENDPOINT),
                                            'application/json',
                                            json.dumps(send_message),
                                            {},
                                            TIMEOUT_MS)

        SignalMessenger.log.debug(response)

    @staticmethod
    def broadcast(message):
        SignalMessenger.notification('broadcast', message)
