# pylint: skip-file
from personal.timermanager import TimerManager
from personal.scenemanager import SceneManager, TimeScene
from personal.lightutils import LightUtils
from personal.item import Group, Item
from personal.dateutils import DateUtils
from core.triggers import (ChannelEventTrigger, ItemCommandTrigger,
                           ItemStateChangeTrigger, StartupTrigger, when)
from core.rules import rule
from core.log import LOG_PREFIX, logging

import personal.lightutils
reload(personal.lightutils)


logger = logging.getLogger('{}.Lights'.format(LOG_PREFIX))


@rule('GUI Lightcontrols')
@when('Member of Lightcontrol received command')
def lightcontrol(event):
    lightcontrol_item = Item.from_event(event)
    command = lightcontrol_item.get_string('OFF', True)

    lightbulb_item = lightcontrol_item.from_scripting('lightbulb_item')

    logger.debug('%s: %s %s', lightbulb_item.name,
                 command, lightbulb_item.scripting())

    LightUtils.manual(lightbulb_item, command, event)


@rule('Reset Switching cycles')
@when('Member of SwitchingCyclesReset received command ON')
def reset_switchingcycles(event):
    reset_item = Item.from_event(event)
    cycles_item = reset_item.from_scripting('cycles_item')
    cycles_item.post_update(0)
    reset_item.post_update(OFF)


@rule('Change colors of RGB lights')
@when("Time cron 45 * * * * ?")
def change_colors(event):
    for lightbulb_item in Group('RGBLight'):
        control_item = lightbulb_item.from_scripting('control_item')
        command = control_item.get_string('OFF')
        LightUtils.command(lightbulb_item, command)


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
        event_key = 'event_{}'.format(event)
        if wallswitch.is_scripting(event_key):
            for assignment_item in Group(wallswitch.scripting(event_key)):
                command = assignment_item.get_string()
                if command is not None and command != 'NULL':
                    self.log.debug('%s: %s', assignment_item.name, command)
                    lightbulb_item = assignment_item.from_scripting(
                        'lightbulb_item')
                    LightUtils.manual(lightbulb_item, command)


@rule('Motion detector event')
class MotionDetectorEvent(object):
    def __init__(self):
        self.log = logging.getLogger(
            '{}.MotionDetectorEvent'.format(LOG_PREFIX))
        self.timers = TimerManager('Motiondetector')
        self.scenemanager = SceneManager.instance()
        self.scenemanager.read_timeconfig()

        self.triggers = [StartupTrigger(
            trigger_name='MotiondetectorStartup').trigger]

        for motiondetector in Group('MotionDetectorPresence'):
            trigger_name = 'MotionDetectedEvent_{}'.format(motiondetector.name)
            self.triggers.append(ItemStateChangeTrigger(
                motiondetector.name, state="ON", trigger_name=trigger_name).trigger)

        for timeconfig in Group('sceneTimeConfiguration'):
            trigger_name = 'MotionSceneConfig_{}'.format(
                timeconfig.name)
            self.triggers.append(ItemCommandTrigger(
                timeconfig.name, trigger_name=trigger_name).trigger)

    def execute(self, action, inputs):
        module = inputs['module']
        modulecfg = module.split('_')

        if modulecfg[0] == 'MotiondetectorStartup':
            self.log.info('Motiondetector started up')
        elif modulecfg[0] == 'MotionDetectedEvent':
            presence_item = Item(modulecfg[1])

            self.log.info('Motion detected by %s', presence_item.name)
            self.motion(presence_item)
        elif modulecfg[0] == 'MotionSceneConfig':
            self.scenemanager.read_timeconfig()

    def motion(self, presence_item):
        is_darkness = Item('darkness').get_onoff()
        is_night = TimeScene.NIGHT == self.scenemanager.actual_timescene()

        for assignment_item in Group(presence_item.scripting('assignment_group')):
            if assignment_item.get_onoff(True):
                darkness_item = assignment_item.from_scripting('darkness_item')
                if is_darkness or not darkness_item.get_onoff():
                    lightbulb_item = assignment_item.from_scripting(
                        'lightbulb_item')
                    self.turn_light_on(lightbulb_item, is_night)
                    self.start_timer(lightbulb_item)

    def turn_light_on(self, lightbulb_item, is_night):
        is_nightmode = lightbulb_item.is_scripting('nightmode_item')

        if is_nightmode and is_night:
            LightUtils.command(lightbulb_item, 'NIGHT')
        else:
            LightUtils.command(lightbulb_item, 'ALL')

    def start_timer(self, lightbulb_item):
        period_item = lightbulb_item.from_scripting('motionperiod_item')
        period = period_item.get_int(10, True)

        self.timers.activate(lightbulb_item.name, lambda: self.turn_light_off(
            lightbulb_item), DateUtils.now().plusSeconds(period))

    def turn_light_off(self, lightbulb_item):
        for assignment_item in Group(lightbulb_item.scripting('motiondetectors_group')):
            if not assignment_item.get_onoff(True):
                continue

            presence_item = assignment_item.from_scripting('presence_item')
            if presence_item.get_onoff():
                self.start_timer(lightbulb_item)
                return

        LightUtils.command(lightbulb_item, 'OFF')
