# pylint: skip-file
from personal.signalmessenger import SignalMessenger
from personal.item import Item
from personal.stringutils import StringUtils
from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX

import personal.item
reload(personal.item)

logger = logging.getLogger('{}.Weather'.format(LOG_PREFIX))


@rule("Weather warning")
@when("System started")
@when("Member of WeatherWarning changed")
@when("Member of WeatherWarningSeverity changed")
@when("Member of WeatherWarningUrgency changed")
@when("Member of WeatherWarningEvent changed")
@when("Member of WeatherWarningFrom changed")
@when("Member of WeatherWarningTo changed")
def weather_warning(event):
    for warning_active in ir.getItem('WeatherWarning').members:
        warning_item = Item(warning_active)
        event_item = warning_item.from_scripting('event')
        event_mapped_item = warning_item.from_scripting('event_mapped')

        event_str = event_item.get_value('').upper()
        event_str = event_str.replace('VORABINFORMATION', '')
        event_str = event_str.replace(' ', '')
        event_mapped = Item.transform_map('dwdeventkeyword', event_str)

        event_str = Item.transform_map('dwdevent', event_mapped)
        severity_item = warning_item.from_scripting('severity')
        severity_str = Item.transform_map(
            'dwdseverity', severity_item.get_value(''))

        event_mapped_item.set_label(u"{}".format(severity_str))
        event_mapped_item.send_command(event_mapped)


@rule('GUI Weatherstation')
@when('Member of WeatherCondition changed')
@when('Item temperatureOutdoor changed')
@when('Member of WeatherWarningEventMapped received command')
def gui_weatherstation(event):
    weatherstation_item = Item('weatherstation')

    warning_item = Item.from_members_first('WeatherWarning')
    severity_item = warning_item.from_scripting('severity')
    severity_str = severity_item.get_value('')

    if severity_str in ['Severe', 'Extreme']:
        severity_str = Item.transform_map('dwdseverity', severity_str)

        event_mapped_item = warning_item.from_scripting('event_mapped')
        event_id = event_mapped_item.get_value(0, event)
        event_str = Item.transform_map('dwdevent', event_id)

        weatherstation_item.set_label(u'{}'.format(severity_str))

        weatherstation_icon(weatherstation_item,
                            warning_item, event_id, 'dwdevent')
        weatherstation_item.post_update(event_str)
    else:
        condition_item = Item.from_members_first('WeatherCondition')
        condition_id = condition_item.get_value(0, event)
        condition_str = Item.transform_map('weathercondition', condition_id)

        temperature = Item('temperatureOutdoor').get_value(0.0, event)
        temperature = StringUtils.format_number(temperature, 1)

        weatherstation_item.set_label(weatherstation_item.scripting('label'))
        weatherstation_icon(weatherstation_item,
                            condition_item, condition_id, 'weather')
        weatherstation_item.post_update(
            u'{} ({} °C)'.format(condition_str, temperature))


def weatherstation_icon(weatherstation_item, mapping_item, identifier, prefix):
    icon_mappings = mapping_item.scripting('icons').split(',')
    icon_mappings = dict(map(lambda x: x.split('='), icon_mappings))
    icon_key = u'{}'.format(identifier)

    if icon_key in icon_mappings:
        weatherstation_item.set_icon(
            '{}{}'.format(prefix, icon_mappings[icon_key]))
    else:
        weatherstation_item.set_icon('{}{}'.format(prefix, identifier))
