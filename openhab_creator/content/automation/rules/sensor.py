# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Group, Item
from personal.signalmessenger import SignalMessenger

logger = logging.getLogger('{}.Sensor'.format(LOG_PREFIX))


@rule('Trends')
@when('Member of Trend changed')
@when("Time cron 41 0/15 * * * ?")
@when("System started")
def trends(event):
    for item in Group('Trend'):
        delta = item.delta_since(DateUtils.now().minusHours(1))

        trend_item = item.from_scripting('trend_item')

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
        for item in Group('PressureSealevel'):
            pressure_sealevel(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        pressure_item = Item(event_or_itemname)
    else:
        pressure_item = Item.from_event(event_or_itemname)

    new_state = pressure_item.get_value()
    if new_state is None:
        return

    value = new_state.floatValue()
    temperature_item = Item('temperatureOutdoor')
    temperature = temperature_item.get_float(15.0) + 273.15

    altitude = pressure_item.scripting('altitude').intValue()

    sealevel_value = value * \
        pow(temperature / (temperature + 0.0065 * altitude), -5.255)

    pressure_item.from_scripting(
        'pressure_sealevel_item').post_update(sealevel_value)


@rule('Soil moisture notification')
@when('Descendent of moistureIndoor changed')
def moisture_notification(event):
    moisture_item = Item.from_event(event)
    percentage = moisture_item.get_int(-1)

    if percentage == -1:
        return

    if percentage < 40:
        reminder_item = moisture_item.from_scripting('reminder_item')
        reminder_time = reminder_item.get_datetime(
            DateUtils.now().minusHours(25))

        if reminder_time.plusHours(24).isBefore(DateUtils.now()):
            SignalMessenger.broadcast(reminder_item.scripting('message'))
            reminder_item.post_update(DateUtils.set_now())
    elif moisture_item.delta_since(DateUtils.now().minusMinutes(1)) > 10.0:
        watered_item = moisture_item.from_scripting('watered_item')
        watered_item.post_update(DateUtils.set_now())
        SignalMessenger.broadcast(watered_item.scripting('message'))


@rule('Average 7 days')
@when('System started')
@when('Member of Average7d changed')
def average7days(event_or_itemname):
    if event_or_itemname is None:
        for item in Group('Average7d'):
            average7days(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        sensor_item = Item(event_or_itemname)
    else:
        sensor_item = Item.from_event(event_or_itemname)

    average_item = sensor_item.from_scripting('average_item')
    average = sensor_item.average_since(DateUtils.now().minusDays(7))
    average_item.post_update(average)
