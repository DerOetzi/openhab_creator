# pylint: skip-file
from core.date import format_date
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.item import Group, Item
from personal.signalmessenger import SignalMessenger
from personal.stringutils import StringUtils

logger = logging.getLogger('{}.Weather'.format(LOG_PREFIX))


def send_warning_message(event, warning_item, event_mapped, severity_str):
    event_str = Item.transform_map('dwdevent', event_mapped)
    message = warning_item.scripting('text').format(severity_str, event_str)

    description_item = warning_item.from_scripting('description')
    if description_item is not None:
        message += u' {}'.format(description_item.get_string(''))

    instruction_item = warning_item.from_scripting('instruction')
    if instruction_item is not None:
        instruction = instruction_item.get_string('')
        if instruction != '':
            message += u' {}'.format(instruction)

    from_item = warning_item.from_scripting('from')
    from_datetime = from_item.get_datetime()
    message += u' {} {}'.format(from_item.scripting('text'),
                                format_date(from_datetime, 'dd.MM.yyyy HH:mm'))

    to_item = warning_item.from_scripting('to')
    to_datetime = to_item.get_datetime()
    if to_datetime is not None:
        message += u' {} {}'.format(to_item.scripting('text'),
                                    format_date(to_datetime, 'dd.MM.yyyy HH:mm'))

    logger.info(message)
    SignalMessenger.broadcast(message)


lock_until = {
    'warnings': DateUtils.now().minusSeconds(1)
}


@rule("Weather warning")
@when("System started")
@when("Member of WeatherWarning changed")
@when("Member of WeatherWarningSeverity changed")
@when("Member of WeatherWarningEvent changed")
@when("Member of WeatherWarningFrom changed")
@when("Member of WeatherWarningTo changed")
def weather_warning(event):
    global lock_until
    if lock_until['warnings'].isAfter(DateUtils.now()):
        return

    lock_until['warnings'] = DateUtils.now().plusSeconds(30)

    for warning_item in Group('WeatherWarning'):
        event_item = warning_item.from_scripting('event')
        event_mapped_item = warning_item.from_scripting('event_mapped')

        event_str = event_item.get_string('').upper()

        urgency_item = warning_item.from_scripting('urgency')

        if 'VORABINFORMATION' in event_str:
            event_str = event_str.replace('VORABINFORMATION', '')
            urgency_item.post_update(ON)
        else:
            urgency_item.post_update(OFF)

        event_str = event_str.replace(' ', '')
        event_mapped = Item.transform_map('dwdeventkeyword', event_str)

        severity_item = warning_item.from_scripting('severity')
        severity_value = severity_item.get_string('')
        severity_str = Item.transform_map(
            'dwdseverity', severity_value)

        event_mapped_item.set_label(u"{}".format(severity_str))
        event_mapped_item.send_command(event_mapped)

        if event is not None and warning_item.get_onoff():
            warning_active_item = Item(
                u'weatherwarning{}Active'.format(severity_value))

            if warning_active_item.get_onoff():
                send_warning_message(event, warning_item,
                                     event_mapped, severity_str)


@rule('GUI Weatherstation')
@when('Member of WeatherCondition changed')
@when('Item temperatureOutdoor changed')
@when('Member of WeatherWarningEventMapped received command')
def gui_weatherstation(event):
    weatherstation_item = Item('weatherstation', event)

    warning_item = Item.from_members_first('WeatherWarning', event)
    severity_item = warning_item.from_scripting('severity')
    severity_str = severity_item.get_string('')

    if severity_str in ['Severe', 'Extreme']:
        severity_str = Item.transform_map('dwdseverity', severity_str)

        event_mapped_item = warning_item.from_scripting('event_mapped')
        event_id = event_mapped_item.get_int(0)
        event_str = Item.transform_map('dwdevent', event_id)

        weatherstation_item.set_label(u'{}'.format(severity_str))

        weatherstation_icon(weatherstation_item,
                            warning_item, event_id, 'dwdevent')
        weatherstation_item.post_update(event_str)
    else:
        condition_item = Item.from_members_first('WeatherCondition', event)
        condition_id = condition_item.get_int(0)
        condition_str = Item.transform_map('weathercondition', condition_id)

        temperature = Item('temperatureOutdoor').get_float(0.0)
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


FITZPATRICK_COEFFICENT = [2.5, 3, 4, 5, 8, 15]


@rule('UVIndex calculate skin types')
@when('System started')
@when('Member of UVIndex changed')
def fitzpatrick_skin_types(event):
    if event is None:
        uvindex_item = Item.from_members_first('UVIndex')
    else:
        uvindex_item = Item.from_event(event)

    calculation_items = uvindex_item.scripting()

    uvindex = uvindex_item.get_float(0.0)

    for calculation_item_name in calculation_items:
        calculation_item = uvindex_item.from_scripting(calculation_item_name)

        if uvindex == 0.0:
            calculation_item.post_update(NULL)
        else:
            index = int(calculation_item_name[-1:]) - 1
            safeexposure = (
                200 * FITZPATRICK_COEFFICENT[index]) / (3 * uvindex)
            calculation_item.post_update(int(safeexposure))
