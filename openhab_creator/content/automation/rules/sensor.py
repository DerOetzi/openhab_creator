from core.rules import rule
from core.triggers import when
from core.actions import PersistenceExtensions
from core.log import logging, LOG_PREFIX

from personal.dateutils import DateUtils
from personal.item import Item
from personal.signalmessenger import SignalMessenger

logger = logging.getLogger('{}.Sensor'.format(LOG_PREFIX))


@rule('Trends')
@when('Member of Trend changed')
@when("Time cron 41 0/15 * * * ?")
@when("System started")
def trends(event):
    for item in ir.getItem('Trend').members:
        delta = Item(item).delta_since(DateUtils.now().minusHours(1))

        trend_item = Item('trend{}'.format(item.name))

        if delta < 0.0:
            trend_item.post_update('rising')
        elif delta > 0.0:
            trend_item.post_update('falling')
        else:
            trend_item.post_update('consistent')


@rule('Soil moisture notification')
@when('Descendent of moistureIndoor changed')
def moisture_notification(event):
    moisture_item = Item(event.itemName)
    percentage = moisture_item.get_value(-1, event)

    if percentage == -1:
        return

    if percentage < 40:
        reminder_item = Item(moisture_item.scripting('reminder_item'))
        reminder_time = reminder_item.get_value(
            DateUtils.now().minusHours(25))

        if reminder_time.plusHours(24).isBefore(DateUtils.now()):
            SignalMessenger.broadcast(reminder_item.scripting('message'))
            reminder_item.post_update(DateUtils.set_now())
    elif moisture_item.delta_since(DateUtils.now().minusMinutes(1)) > 10.0:
        watered_item = Item(moisture_item.scripting('watered_item'))
        watered_item.post_update(DateUtils.set_now())
        SignalMessenger.broadcast(watered_item.scripting('message'))
