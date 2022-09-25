# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.osgi import get_service
from core.rules import rule
from core.triggers import (ChannelEventTrigger, ItemCommandTrigger,
                           ItemStateChangeTrigger, StartupTrigger, when)
from personal.dateutils import DateUtils
from personal.heatingutils import HeatingUtils
from personal.item import Group, Item
from personal.signalmessenger import SignalMessenger
from personal.timermanager import TimerManager
from personal.autoitemmanager import AutoItemManager


class PseudoEvent:
    def __init__(self, itemName):
        self.itemName = itemName


@rule('Window events')
class WindowEvent(object):
    def __init__(self):
        self.log = logging.getLogger('{}.WindowEvent'.format(LOG_PREFIX))
        self.timers = TimerManager('WindowReminder')
        self.triggers = [StartupTrigger(
            trigger_name='WindowStartup').trigger]

        for window in Group('windows'):
            trigger_name = 'WindowStateOpen_{}'.format(window.name)
            self.triggers.append(ItemStateChangeTrigger(
                window.name, state='OPEN', trigger_name=trigger_name).trigger)

            trigger_name = 'WindowStateClosed_{}'.format(window.name)
            self.triggers.append(ItemStateChangeTrigger(
                window.name, state='CLOSED', trigger_name=trigger_name).trigger)

        self.triggers.append(ItemStateChangeTrigger(
            'Presences', state=0, trigger_name='WindowAbsence').trigger)

    def execute(self, action, inputs):
        self.log.debug(action)
        module = inputs['module']
        modulecfg = module.split('_')

        if modulecfg[0] == 'WindowStartup':
            self.log.info('Window started up')
        elif modulecfg[0] == 'WindowStateOpen':
            window_item = Item(modulecfg[1])
            self.log.info('Window open %s', window_item.name)
            self.open(window_item)
        elif modulecfg[0] == 'WindowStateClosed':
            window_item = Item(modulecfg[1])
            self.log.info('Window closed %s', window_item.name)
            self.closed(window_item)
        elif modulecfg[0] == 'WindowAbsence':
            self.absence()

    def open(self, window_item):

        is_absence = Item('Presences').get_int(0) == 0
        if is_absence:
            self.log.warning(window_item.scripting('alarm_message'))
            SignalMessenger.broadcast(window_item.scripting('alarm_message'))

        heating = Item('heating').get_onoff()
        if heating:
            heating_item = window_item.from_scripting('heating_item')

            heating_control = heating_item.from_scripting('control_item')
            save_item = window_item.from_scripting('heating_control_save')
            save_item.post_update(heating_control.get_string('CLOSED'))

            HeatingUtils.manual(heating_item, 'CLOSED',
                                PseudoEvent(heating_control.name))

            remindertime = self.get_remindertime(window_item)

            if remindertime > 0:
                self.timers.activate(window_item.name, lambda window_item=window_item: self.send_reminder(
                    window_item), DateUtils.now().plusMinutes(remindertime))

    def send_reminder(self, window_item):
        if window_item.get_openclosed():
            SignalMessenger.broadcast(
                window_item.scripting('reminder_message'))

            remindertime = self.get_remindertime(window_item)

            if remindertime > 0:
                self.timers.activate(window_item.name, lambda window_item=window_item: self.send_reminder(
                    window_item), DateUtils.now().plusMinutes(remindertime))

    def get_remindertime(self, window_item):
        remindertime = 0
        if window_item.is_scripting('remindertime_item'):
            remindertime_item = window_item.from_scripting('remindertime_item')
            remindertime = remindertime_item.get_int(0, True)

        return remindertime

    def closed(self, window_item):
        self.timers.cancel(window_item.name)

        heating = Item('heating').get_onoff()
        if heating:
            heating_item = window_item.from_scripting('heating_item')
            auto_item = heating_item.from_scripting('auto_item')

            reactivation_item = auto_item.from_scripting('reactivation_item')
            reactivation_period = reactivation_item.get_int(0, True)

            if reactivation_period > 0:
                auto_item.send_command(ON)
            else:
                display_item = auto_item.from_scripting('display_item')
                display_item.post_update(OFF)

                auto_item.post_update(ON)

                save_item = window_item.from_scripting('heating_control_save')
                HeatingUtils.command(
                    heating_item, save_item.get_string('CLOSED'))

    def abscence(self):
        for window_item in Group('windows'):
            if window_item.get_openclosed():
                SignalMessenger.broadcast(
                    window_item.scripting('absence_message'))
