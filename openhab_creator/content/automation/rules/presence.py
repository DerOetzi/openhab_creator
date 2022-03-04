# pylint: skip-file
from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX

from personal.dateutils import DateUtils
from personal.ephemerisutils import EphemerisUtils
from personal.item import Item, Group

logger = logging.getLogger('{}.Presence'.format(LOG_PREFIX))


@rule('Smartphone distance')
@when('Member of Distances changed')
def smartphone_distances(event):
    distance_item = Item.from_event(event)
    actual_distance = distance_item.get_float(-0.1)
    geofence_item = distance_item.from_scripting('geofence')

    wayhome_item = Item('wayhome')
    wayhome = wayhome_item.get_onoff(True)

    if actual_distance <= 0.020 and actual_distance >= 0:
        geofence_item.post_update(ON)
    else:
        geofence_item.post_update(OFF)

        presence = Item('Presences').get_int(0)

        if presence == 0 and not wayhome and actual_distance <= 12.0:
            delta_distance = distance_item.delta_since(
                DateUtils.now().minusMinutes(5))

            if delta_distance <= -0.7:
                wayhome_item.send_command(ON)
                logger.info('Way home activated')


@rule('Coming home')
@when('Item Presences changed')
def coming_home(event):
    presence = Item('Presences', event).get_int(0) == 1

    wayhome_item = Item('wayhome')
    wayhome = wayhome_item.get_onoff(True)

    if presence and wayhome:
        wayhome_item.send_command(OFF)


FUTURE_TIME = 9999


def get_date_or_future(state_item=None, begin_item=None):
    date = DateUtils.now().plusDays(FUTURE_TIME)
    if state_item:
        begin_item = state_item.from_scripting('begin_item')

    if begin_item:
        date = begin_item.get_datetime(date)

    return date


def set_homeoffice(item):
    statetype = item.scripting('statetype')

    if statetype == 'homeoffice':
        homeoffice_item = item
    elif statetype in ('holidays', 'sickness'):
        homeoffice_item = item.from_scripting('homeoffice_item')

    if homeoffice_item:
        holidays_item = homeoffice_item.from_scripting('holidays_item')
        sickness_item = homeoffice_item.from_scripting('sickness_item')

        homeoffice_begin = get_date_or_future(homeoffice_item)
        holidays_begin = get_date_or_future(holidays_item)
        sickness_begin = get_date_or_future(sickness_item)

        if (not EphemerisUtils.is_freeday()
            and DateUtils.is_day_after(homeoffice_begin)
            and not (DateUtils.is_day_after(sickness_begin)
                     or DateUtils.is_day_after(holidays_begin))):
            homeoffice_item.post_update(ON)
        else:
            homeoffice_item.post_update(OFF)


@rule('Set person state by calendar')
@when('System started')
@when("Time cron 46 3 0 * * ?")
@when('Member of PersonStateBegins changed')
def personstate_by_calendar(event_or_itemname):
    if event_or_itemname is None:
        for item in Group('PersonStateBegins'):
            personstate_by_calendar(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        begin_item = Item(event_or_itemname)
    else:
        begin_item = Item.from_event(event_or_itemname)

    state_item = begin_item.from_scripting('state_item')
    statetype = state_item.scripting('statetype')

    begin = get_date_or_future(state_item)

    if statetype in ('holidays', 'sickness'):
        if DateUtils.is_day_after(begin):
            state_item.post_update(ON)
        else:
            state_item.post_update(OFF)

    set_homeoffice(state_item)


@rule('Set person state tomorrow by calendar')
@when('System started')
@when('Member of PersonStateBeginsNext changed')
def personstate_next_by_calendar(event_or_itemname):
    if event_or_itemname is None:
        for item in Group('PersonStateBeginsNext'):
            personstate_next_by_calendar(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        begin_next_item = Item(event_or_itemname)
    else:
        begin_next_item = Item.from_event(event_or_itemname)

    tomorrow_item = begin_next_item.from_scripting('tomorrow_item')

    begin = get_date_or_future(begin_next_item)
    begin_next = get_date_or_future(begin_item=begin_next_item)

    if DateUtils.is_day_after(begin, 1) or DateUtils.is_day_after(begin_next, 1):
        tomorrow_item.post_update(ON)
    else:
        tomorrow_item.post_update(OFF)
