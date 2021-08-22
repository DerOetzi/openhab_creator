# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import ChannelEventTrigger, StartupTrigger, when
from personal.item import Group, Item
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


@rule('Wallswitch event')
class WallSwitchEvent(object):
    def __init__(self):
        self.log = logging.getLogger('{}.WallSwitchEvent'.format(LOG_PREFIX))
        self.triggers = [StartupTrigger(
            trigger_name='WallswitchStartup').trigger]

        for wallswitch in Group('Wallswitches'):
            trigger_name = 'ButtonPressed_{}'.format(wallswitch.name)
            trigger_channel = wallswitch.scripting('trigger_channel')
            self.triggers.append(ChannelEventTrigger(
                trigger_channel, trigger_name=trigger_name).trigger)

    def execute(self, action, inputs):
        module = inputs['module']
        modulecfg = module.split('_')

        if modulecfg[0] == 'WallswitchStartup':
            self.log.info('Wallswitch started up')
        elif modulecfg[0] == 'ButtonPressed':
            wallswitch = Item(modulecfg[1])
            event = inputs['event'].getEvent()
            self.log.info('Button %s pressed: %s',
                          wallswitch.name, event)
            self.execute_assigned_commands(wallswitch, event)

    def execute_assigned_commands(self, wallswitch, event):
        for assignment_item in Group(wallswitch.scripting('event_{}'.format(event))):
            self.log.info('%s: %s', assignment_item.name,
                          assignment_item.get_string())
