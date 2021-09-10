# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when

from personal.item import Group, Item
from personal.signalmessenger import SignalMessenger


logger = logging.getLogger('{}.CallMonitor'.format(LOG_PREFIX))


@rule('Call Monitor')
@when('Member of CallState changed')
def callmonitor(event):
    callstate_item = Item.from_event(event)
    callstate = callstate_item.get_string('IDLE')

    laststate_item = callstate_item.from_scripting('laststate_item')
    incoming_item = callstate_item.from_scripting('incoming_item')
    lastincoming_item = callstate_item.from_scripting('lastincoming_item')

    if 'RINGING' == callstate:
        incoming_call = incoming_item.get_call().getValue(1)
        lastincoming_item.post_update(incoming_call)
        logger.info('%s (%s)', incoming_call, type(incoming_call))
    elif 'IDLE' == callstate:
        laststate = laststate_item.get_string('IDLE')
        if laststate == 'RINGING':
            lastincoming = lastincoming_item.get_string('')
            message = callstate_item.scripting(
                'message').format(caller=lastincoming)
            logger.info(message)
            SignalMessenger.broadcast(message)

        lastincoming_item.post_update(NULL)

    laststate_item.post_update(callstate)
