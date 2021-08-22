# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Item, Group
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
        for item in Group('WhiteGood'):
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
    typed = power_item.scripting('typed')

    start_item = power_item.from_scripting('start_item')
    start = start_item.get_datetime(DateUtils.now().minusHours(2))

    if typed == 'washingmachine_dryer':
        typed = 'washingmachine'

        max_power = power_item.maximum_since(start)
        limit = power_item.scripting('washing_dryer_limit').floatValue()

        if max_power > limit:
            if start.plusHours(4).isBefore(DateUtils.now()):
                typed = 'washingmachine_dryer'
        else:
            typed = 'dryer'

    start_item.post_update(NULL)

    message = power_item.scripting('{}_message'.format(typed))
    SignalMessenger.broadcast(message)

    whitegood_reminder(power_item, typed)


def whitegood_reminder(power_item, typed):
    if power_item.is_scripting('reminder') and power_item.scripting('reminder') in typed:
        default_cycles = power_item.scripting('reminder_cycles').intValue()
        countdown_item = power_item.from_scripting('countdown_item')
        done_item = power_item.from_scripting('done_item')

        countdown = countdown_item.get_int(default_cycles, True) - 1

        if countdown <= 0:
            countdown = 0
            done_item.post_update(OFF)
            message = power_item.scripting('reminder_message')
            SignalMessenger.broadcast(message)

        countdown_item.post_update(countdown)


@rule('White good reminder done')
@when('Member of WhiteGoodReminderDone received command ON')
def whitegood_reminder_done(event):
    done_item = Item.from_event(event)
    default_cycles = done_item.scripting('reminder_cycles').intValue()
    countdown_item = done_item.from_scripting('countdown_item')

    countdown_item.post_update(default_cycles)
