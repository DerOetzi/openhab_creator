# pylint: skip-file
from personal.timermanager import TimerManager
from personal.scenemanager import SceneManager, TimeScene
from personal.lightutils import LightUtils
from personal.item import Group, Item
from personal.dateutils import DateUtils
from core.osgi import get_service
from core.jsr223.scope import OFF, ON
from core.triggers import (ChannelEventTrigger, ItemCommandTrigger,
                           ItemStateChangeTrigger, StartupTrigger, when)
from core.rules import rule
from core.log import LOG_PREFIX, logging

import personal.lightutils
reload(personal.lightutils)


logger = logging.getLogger('{}.Lights'.format(LOG_PREFIX))

rulemanager = get_service("org.openhab.core.automation.RuleManager")


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
        self.log.debug(action)
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
                self.command(assignment_item, command)

    def command(self, assignment_item, command):
        if command is not None and command != 'NULL':
            self.log.debug('%s: %s', assignment_item.name, command)
            if assignment_item.is_scripting('lightbulb_item'):
                self.lightbulb_command(assignment_item, command)
            elif assignment_item.is_scripting('poweroutlet_item'):
                self.poweroutlet_command(assignment_item, command)

    def lightbulb_command(self, assignment_item, command):
        lightbulb_item = assignment_item.from_scripting(
            'lightbulb_item')

        if command == 'UNBLOCK':
            MotionDetectorEvent.trigger_unblock(lightbulb_item)
        elif command == 'OFFUNBLOCK':
            MotionDetectorEvent.trigger_unblock(lightbulb_item)
            LightUtils.manual(lightbulb_item, 'OFF')
        elif command == 'TRIGGERMOTION':
            MotionDetectorEvent.trigger_motion(lightbulb_item)
        else:
            LightUtils.manual(lightbulb_item, command)
            MotionDetectorEvent().trigger_block(lightbulb_item)

    def poweroutlet_command(self, assignment_item, command):
        poweroutlet_item = assignment_item.from_scripting(
            'poweroutlet_item')

        if command == 'OFF':
            poweroutlet_item.send_command(OFF)
        elif command == 'ON':
            poweroutlet_item.send_command(ON)


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

        for motionblocked in Group('MotionDetectorBlocked'):
            lightbulb = motionblocked.scripting('lightbulb_item')
            trigger_name = 'MotionUnblock_{}'.format(lightbulb)
            self.triggers.append(ItemCommandTrigger(
                motionblocked.name, command="OFF", trigger_name=trigger_name).trigger)

        for timeconfig in Group('sceneTimeConfiguration'):
            trigger_name = 'MotionSceneConfig_{}'.format(
                timeconfig.name)
            self.triggers.append(ItemCommandTrigger(
                timeconfig.name, trigger_name=trigger_name).trigger)

        self.triggers.append(ItemStateChangeTrigger(
            'darkness', trigger_name='DarknessChanged').trigger)

    def execute(self, action, inputs):
        self.log.debug(action)
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
        elif modulecfg[0] == 'MotionUnblock':
            lightbulb_item = Item(modulecfg[1])
            self.unblock(lightbulb_item)
        elif modulecfg[0] == 'MotionBlock':
            lightbulb_item = Item(modulecfg[1])
            self.block(lightbulb_item)
        elif modulecfg[0] == 'MotionTrigger':
            lightbulb_item = Item(modulecfg[1])
            if self.get_period(lightbulb_item) > 0:
                self.turn_light_on(
                    lightbulb_item, self.scenemanager.is_night())
                self.unblock(lightbulb_item)
        elif modulecfg[0] == 'DarknessChanged':
            self.darkness_changed(
                {'itemName': 'darkness', 'itemCommand': inputs['newState']})
        else:
            self.log.info(inputs)

    def get_period(self, lightbulb_item):
        period_item = lightbulb_item.from_scripting('motionperiod_item')
        period = period_item.get_int(0, True)
        return period

    @classmethod
    def trigger_unblock(cls, lightbulb_item):
        rulemanager.runNow(MotionDetectorEvent.UID, False, {
            'module': 'MotionUnblock_{}'.format(lightbulb_item.name)})

    def unblock(self, lightbulb_item):
        if self.has_motion_period(lightbulb_item):
            self.log.debug('Unblock {}'.format(lightbulb_item.name))
            motionblocked_item = lightbulb_item.from_scripting(
                'motionblocked_item')

            motionblocked_item.post_update(OFF)
            self.turn_light_off(lightbulb_item)
            self.timers.cancel('unblock_{}'.format(lightbulb_item.name))

    @classmethod
    def trigger_block(cls, lightbulb_item):
        rulemanager.runNow(MotionDetectorEvent.UID, False, {
            'module': 'MotionBlock_{}'.format(lightbulb_item.name)})

    def block(self, lightbulb_item):
        if self.get_period(lightbulb_item) > 0:
            motionblocked_item = lightbulb_item.from_scripting(
                'motionblocked_item')

            motionblocked_item.post_update(ON)
            self.timers.cancel('turn_light_off_{}'.format(lightbulb_item.name))
            self.timers.activate('unblock_{}'.format(lightbulb_item.name),
                                 lambda: self.unblock(lightbulb_item),
                                 DateUtils.now().plusHours(2))

    @classmethod
    def trigger_motion(cls, lightbulb_item):
        rulemanager.runNow(MotionDetectorEvent.UID, False, {
            'module': 'MotionTrigger_{}'.format(lightbulb_item.name)})

    def motion(self, presence_item):
        is_darkness = Item('darkness').get_onoff()
        is_night = self.scenemanager.is_night()

        for assignment_item in Group(presence_item.scripting('assignment_group')):
            if assignment_item.get_onoff(True):
                darkness_item = assignment_item.from_scripting('darkness_item')
                if is_darkness or not darkness_item.get_onoff():
                    lightbulb_item = assignment_item.from_scripting(
                        'lightbulb_item')
                    motionblocked_item = lightbulb_item.from_scripting(
                        'motionblocked_item')

                    if motionblocked_item.get_onoff(True):
                        self.block(lightbulb_item)
                        continue

                    self.turn_light_on(lightbulb_item, is_night)
                    self.start_timer(lightbulb_item)

    @staticmethod
    def turn_light_on(lightbulb_item, is_night):
        is_nightmode = lightbulb_item.is_scripting('nightmode_item')

        if is_nightmode and is_night:
            LightUtils.command(lightbulb_item, 'NIGHT')
        else:
            LightUtils.command(lightbulb_item, 'ALL')

    def start_timer(self, lightbulb_item):
        period = self.get_period(lightbulb_item)

        self.timers.activate('turn_light_off_{}'.format(lightbulb_item.name),
                             lambda: self.turn_light_off(lightbulb_item),
                             DateUtils.now().plusSeconds(period))

    def turn_light_off(self, lightbulb_item, event=None):
        is_darkness = Item('darkness', event).get_onoff()
        darkness_item = lightbulb_item.from_scripting('darkness_item')
        if is_darkness or not darkness_item.get_onoff():
            for assignment_item in Group(lightbulb_item.scripting('motiondetectors_group')):
                if not assignment_item.get_onoff(True):
                    continue

                presence_item = assignment_item.from_scripting('presence_item')
                if presence_item.get_onoff():
                    self.start_timer(lightbulb_item)
                    return

        LightUtils.command(lightbulb_item, 'OFF')

    def has_motion_period(self, lightbulb_item):
        return self.get_period(lightbulb_item) > 0

    def darkness_changed(self, event):
        darkness_item = Item('darkness', event)
        is_darkness = darkness_item.get_onoff()

        if is_darkness:
            for presence_item in Group('MotionDetectorPresence'):
                if presence_item.get_onoff():
                    self.motion(presence_item)
        else:
            for lightbulb_item in Group('Lights'):
                motionblocked_item = lightbulb_item.from_scripting(
                    'motionblocked_item')

                if self.has_motion_period(lightbulb_item) \
                        and not motionblocked_item.get_onoff(True):

                    self.turn_light_off(lightbulb_item, event)
