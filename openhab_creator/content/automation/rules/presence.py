# pylint: skip-file
from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX

from personal.dateutils import DateUtils
from personal.item import Item

logger = logging.getLogger('{}.Presence'.format(LOG_PREFIX))


@rule('Smartphone distance')
@when('Member of Distances changed')
def smartphone_distances(event):
    distance_item = Item.from_event(event)
    actual_distance = distance_item.get_value(-0.1, event)
    geofence_item = distance_item.from_scripting('geofence')

    if actual_distance <= 0.020 and actual_distance >= 0:
        geofence_item.post_update(ON)
    else:
        geofence_item.post_update(OFF)

        presence = Item('Presences').get_value(0, event)
        wayhome_item = Item('wayhome')
        wayhome = wayhome_item.get_value(OFF, event, True)

        if presence == 0 and wayhome == OFF and actual_distance <= 12.0:
            delta_distance = distance_item.delta_since(
                DateUtils.now().minusMinutes(5))

            if delta_distance <= -0.7:
                wayhome_item.send_command(ON)
                logger.info('Way home activated')
