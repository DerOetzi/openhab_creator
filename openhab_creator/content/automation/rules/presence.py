# pylint: skip-file
from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX

from personal.dateutils import DateUtils
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


@rule('Set person state by calendar')
@when('System started')
@when('Member of PersonStateBegins changed')
def personstate_by_calendar(event_or_itemname):
    if event_or_itemname is None:
        for item in Group('PersonStateBegins'):
            personstate_by_calendar(item.name)
        return
    elif isinstance(event_or_itemname, basestring):
        begin_item = Item(event_or_itemname)
    else:
        begin_item = Item.from_event(event)

    state_item = begin_item.from_scripting('state_item')
    statetype = state_item.scripting('statetype')

    begin = begin_item.get_datetime(DateUtils.now().plusSeconds(10))

    if statetype == 'holidays':
        if DateUtils.now().isAfter(begin):
            state_item.post_update(ON)
        else:
            state_item.post_update(OFF)
