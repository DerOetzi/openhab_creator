# pylint: skip-file
import personal.heatingutils
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when

from personal.dateutils import DateUtils
from personal.heatingutils import HeatingUtils
from personal.item import Group, Item
from personal.scenemanager import SceneManager, TimeScene

reload(personal.heatingutils)

logger = logging.getLogger('{}.Heatings'.format(LOG_PREFIX))


@rule('GUI Heatingcontrols')
@when('Member of Heatcontrol received command')
def heatingcontrol(event):
    heatcontrol_item = Item.from_event(event)
    command = heatcontrol_item.get_string('CLOSED', True)

    heating_item = heatcontrol_item.from_scripting('heating_item')

    logger.info('%s: %s %s', heating_item.name,
                command, heating_item.scripting())

    HeatingUtils.manual(heating_item, command, event)


@rule('Heating settings')
@when('Member of HeatTemperature received command')
def heating_settings(event):
    temp_item = Item.from_event(event)
    heating_item = temp_item.from_scripting('heating_item')
    heatcontrol_item = temp_item.from_scripting('control_item')

    command = heatcontrol_item.get_string('CLOSED', True)

    HeatingUtils.command(heating_item, command)
