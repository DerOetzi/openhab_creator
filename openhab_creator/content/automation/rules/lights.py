# pylint: skip-file
from core.rules import rule
from core.triggers import when
from core.log import logging, LOG_PREFIX

from personal.item import Item
from personal.lightutils import LightUtils

logger = logging.getLogger('{}.Lights'.format(LOG_PREFIX))


@rule('GUI Lightcontrols')
@when('Member of Lightcontrol received command')
def lightcontrol(event):
    lightcontrol_item = Item.from_event(event)
    command = lightcontrol_item.get_string('OFF', True)

    lightbulb_item = lightcontrol_item.from_scripting('lightbulb_item')

    logger.info('%s: %s %s', lightbulb_item.name,
                command, lightbulb_item.scripting())

    LightUtils.command(lightbulb_item, command)


@rule('Reset Switching cycles')
@when('Member of SwitchingCyclesReset received command ON')
def reset_switchingcycles(event):
    reset_item = Item.from_event(event)
    cycles_item = reset_item.from_scripting('cycles_item')
    cycles_item.post_update(0)
    reset_item.post_update(OFF)
