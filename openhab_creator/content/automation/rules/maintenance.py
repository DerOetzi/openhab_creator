# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.item import Item
from personal.signalmessenger import SignalMessenger

logger = logging.getLogger('{}.maintenance', LOG_PREFIX)


@rule('Calculate battery low')
@when('Member of CalcLowBattery changed')
def calculate_battery_low(event):
    level_item = Item.from_event(event)
    low_item = level_item.from_scripting('low_item')

    if level_item.get_float(100.0) < 10:
        low_item.post_update(ON)
    else:
        low_item.post_update(OFF)


@rule('Battery low notification')
@when('Member of LowBattery changed to ON')
def battery_low_notification(event):
    battery_item = Item.from_event(event)
    SignalMessenger.broadcast(battery_item.scripting('message'))
