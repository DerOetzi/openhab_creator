# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Item
from personal.signalmessenger import SignalMessenger

logger = logging.getLogger('{}.WhiteGood'.format(LOG_PREFIX))

WHITEGOOD_OFF = 'OFF'
WHITEGOOD_STANDBY = 'STANDBY'
WHITEGOOD_RUNNING = 'RUNNING'
WHITEGOOD_READY = 'READY'


@rule('White good state')
@when('System started')
@when('Member of WhiteGood changed')
def whitegood_state(event_or_itemname):
    if event_or_itemname is None:
        for item in ir.getItem('WhiteGood').members:
            whitegood_state(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        power_item = Item(event_or_itemname)
    else:
        power_item = Item.from_event(event_or_itemname)

    power = power_item.get_float(0.0)

    status_item = power_item.from_scripting('status_item')
    status = status_item.get_string(WHITEGOOD_OFF, True)

    off_limit = power_item.scripting('off_limit').floatValue()
    standby_limit = power_item.scripting('standby_limit').floatValue()

    if power < off_limit:
        if status == WHITEGOOD_RUNNING:
            whitegood_finished(power_item)
        status_item.post_update(WHITEGOOD_OFF)
    elif power > standby_limit:
        if status != WHITEGOOD_RUNNING:
            start_item = power_item.from_scripting('start_item')
            start_item.post_update(DateUtils.now())

        status_item.post_update(WHITEGOOD_RUNNING)
    elif status == WHITEGOOD_OFF:
        status_item.post_update(WHITEGOOD_STANDBY)
    elif status == WHITEGOOD_RUNNING:
        whitegood_finished(power_item)
        status_item.post_update(WHITEGOOD_READY)


def whitegood_finished(power_item):
    logger.info('Finished whitegood')
