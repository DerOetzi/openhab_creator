# pylint: skip-file
from core.rules import rule
from core.triggers import when
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
            trend_item.post_update('falling')
        elif delta > 0.0:
            trend_item.post_update('rising')
        else:
            trend_item.post_update('consistent')


@rule('Pressure sea level')
@when('System started')
@when('Member of PressureSealevel changed')
def pressure_sealevel(event_or_itemname):
    if event_or_itemname is None:
        for item in ir.getItem('PressureSealevel').members:
            pressure_sealevel(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        pressure_item = Item(event_or_itemname)
    else:
        pressure_item = Item.from_event(event_or_itemname)

    new_state = pressure_item.get_value(event=event_or_itemname)
    if new_state in [NULL, UNDEF]:
        return

    value = new_state.floatValue()
    temperature_item = Item('temperatureOutdoor')
    temperature = temperature_item.get_value(15.0) + 273.15

    altitude = pressure_item.scripting('altitude').intValue()

    sealevel_value = value * \
        pow(temperature / (temperature + 0.0065 * altitude), -5.255)

    pressure_item.from_scripting(
        'pressure_sealevel_item').post_update(sealevel_value)


@rule('Soil moisture notification')
@when('Descendent of moistureIndoor changed')
def moisture_notification(event):
    moisture_item = Item.from_event(event)
    percentage = moisture_item.get_value(-1, event)

    if percentage == -1:
        return

    if percentage < 40:
        reminder_item = moisture_item.from_scripting('reminder_item')
        reminder_time = reminder_item.get_value(
            DateUtils.now().minusHours(25))

        if reminder_time.plusHours(24).isBefore(DateUtils.now()):
            SignalMessenger.broadcast(reminder_item.scripting('message'))
            reminder_item.post_update(DateUtils.set_now())
    elif moisture_item.delta_since(DateUtils.now().minusMinutes(1)) > 10.0:
        watered_item = moisture_item.from_scripting('watered_item')
        watered_item.post_update(DateUtils.set_now())
        SignalMessenger.broadcast(watered_item.scripting('message'))
