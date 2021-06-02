# pylint: skip-file
from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX

from personal.item import Item
from personal.signalmessenger import SignalMessenger

logger = logging.getLogger('{}.Weather'.format(LOG_PREFIX))


@rule("Weather warning")
@when("System started")
@when("Member of WeatherWarning changed")
def weather_warning(event):
    for warning_active in ir.getItem('WeatherWarning').members:
        warning_item = Item(warning_active)
        event_item = warning_item.from_scripting('event')
        event_mapped_item = warning_item.from_scripting('event_mapped')

        event_str = event_item.get_value('').upper()
        event_str = event_str.replace('VORABINFORMATION', '')
        event_str = event_str.replace(' ', '')
        event_mapped = Item.transform_map('dwdeventkeyword', event_str)
        event_mapped_item.post_update(event_mapped)

        event_str = Item.transform_map('dwdevent', event_mapped)
        urgency_item = warning_item.from_scripting('urgency')
        future = urgency_item.get_value('') == 'Future'
        severity_item = warning_item.from_scripting('severity')
        severity_str = Item.transform_map(
            'dwdseverity', severity_item.get_value(''))

        if future:
            event_mapped_item.set_label(
                u"{} - Vorabinformation".format(severity_str))
        else:
            event_mapped_item.set_label(u"{}".format(severity_str))

        logger.info('%s, %s, %s', event_str, future, severity_str)
