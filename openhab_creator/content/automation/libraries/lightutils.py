# pylint: skip-file
import random

import personal.autoitemmanager
from core.jsr223.scope import OFF, ON, DecimalType, HSBType, PercentType
from core.log import LOG_PREFIX, logging
from personal.autoitemmanager import AutoItemManager
from personal.dateutils import DateUtils
from personal.item import Group, Item

reload(personal.autoitemmanager)


class LightUtils(object):
    BLACK = HSBType(DecimalType(0), PercentType(0), PercentType(0))

    log = logging.getLogger('{}.LightUtils'.format(LOG_PREFIX))

    @classmethod
    def automation(cls, lightbulb_item, is_location_active, is_night, is_presences, is_darkness):
        presences_item = lightbulb_item.from_scripting('presences_item')
        darkness_item = lightbulb_item.from_scripting('darkness_item')

        cls.log.debug('Name: %s, active: %s, night: %s, presences: %s, darkness: %s, presences_item: %s, darkness_item: %s',
                      lightbulb_item.name, is_location_active, is_night, is_presences, is_darkness, presences_item.get_onoff(), darkness_item.get_onoff())

        is_darkness_or_always_configuration = (
            is_darkness or not darkness_item.get_onoff(True))

        is_precenses_or_always_configuration = (
            is_presences or presences_item.get_onoff(True))

        if ((is_location_active and is_precenses_or_always_configuration)
                and is_darkness_or_always_configuration):

            is_nightmode = is_night and lightbulb_item.is_scripting(
                'nightmode_item')
            if is_nightmode:
                cls.command(lightbulb_item, 'NIGHT')
            else:
                cls.command(lightbulb_item, 'ALL')
        else:
            cls.command(lightbulb_item, 'OFF')

    @classmethod
    def manual(cls, lightbulb_item, command, event=None):
        AutoItemManager.instance().change_auto(
            lightbulb_item.from_scripting('auto_item'), event)

        cls.command(lightbulb_item, command)

    @classmethod
    def command(cls, lightbulb_item, command):
        is_thing = lightbulb_item.scripting('is_thing')
        cls.log.debug('Command %s: %s', lightbulb_item, command)
        if is_thing:
            if lightbulb_item.is_scripting('brightnessgroup_item'):
                cls.log.debug('Brightnessgroup: %s', lightbulb_item)
                cls._handle_groupthing_command(lightbulb_item, command)
            else:
                cls.log.debug('Single: %s', lightbulb_item)
                cls._handle_single_command(lightbulb_item, command)
        else:
            cls.log.debug('Group: %s', lightbulb_item)
            cls._handle_group_command(lightbulb_item, command)

        lightcontrol_item = lightbulb_item.from_scripting('control_item')
        lightcontrol_item.post_update(command)

    @classmethod
    def _handle_groupthing_command(cls, lightbulb_item, command):
        if command in ['ALL', 'ON']:
            cls._execute(lightbulb_item, 100, ON, cls.color())
        elif command == 'NIGHT':
            cls._handle_group_command(lightbulb_item, command)
        elif command == 'OFF':
            group_members = Group.from_list(
                lightbulb_item.scripting('subequipment').split(','))

            on_items = []

            for group_member in group_members:
                if cls.get_brightness(group_member) > 0:
                    on_items.append(group_member)

            if len(on_items) > 0:
                cls._execute(lightbulb_item, 0, OFF, cls.BLACK)
                for on_item in on_items:
                    cls._increment_switchingcycles(on_item)
        else:
            cls._handle_group_command(lightbulb_item, command)

    @classmethod
    def _handle_single_command(cls, lightbulb_item, command):
        if command in ['ALL', 'ON']:
            cls._execute(lightbulb_item, 100, ON, cls.color())
        elif command == 'NIGHT':
            cls._execute(lightbulb_item, 10, None, cls.color(10))
        elif command == 'OFF':
            updated = cls._execute(lightbulb_item, 0, OFF, cls.BLACK)

            if updated:
                cls._increment_switchingcycles(lightbulb_item)

    @staticmethod
    def _increment_switchingcycles(lightbulb_item):
        if lightbulb_item.is_scripting('cycles_item'):
            cycles_item = lightbulb_item.from_scripting('cycles_item')
            cycles = cycles_item.get_int(0, True)
            cycles += 1
            cycles_item.post_update(cycles)

    @classmethod
    def _execute(cls, lightbulb_item, brightness, onoff, color):
        updated = False

        brightness_item = lightbulb_item.from_scripting('brightness_item')
        brightnessgroup_item = lightbulb_item.from_scripting(
            'brightnessgroup_item')
        onoff_item = lightbulb_item.from_scripting('onoff_item')
        rgb_item = lightbulb_item.from_scripting('rgb_item')

        cls.log.debug('_execute: %s, %d, %s, %s',
                      lightbulb_item, brightness, onoff, color)

        if brightness_item:
            updated = brightness_item.get_int(0) != brightness
            cls.log.debug('%s: %d', brightness_item, brightness)

            if brightnessgroup_item:
                cls.log.debug('%s, %d', brightnessgroup_item, brightness)
                brightnessgroup_item.send_command(brightness)
            else:
                cls.log.debug('%s, %d', brightness_item, brightness)
                brightness_item.send_command(brightness)

        elif onoff and onoff_item:
            updated = onoff_item.get_value() != onoff
            onoff_item.send_command(onoff)
        elif rgb_item:
            updated = rgb_item.get_value(cls.BLACK) != color
            rgb_item.send_command(color)

        return updated

    @staticmethod
    def color(brightness=100):
        color_of_minute = ((DateUtils.now().getMinute() + 1) * 6) - 1
        return HSBType(DecimalType(color_of_minute), PercentType(brightness), PercentType(100))

    @classmethod
    def _handle_group_command(cls, lightbulb_item, command):
        group_members = Group.from_list(
            lightbulb_item.scripting('subequipment').split(','))

        if command == 'ALL':
            for group_member in group_members:
                cls._handle_single_command(group_member, 'ON')
        elif command == 'NIGHT':
            cls._handle_nightmode(lightbulb_item, group_members)
        elif command == 'OFF':
            for group_member in group_members:
                cls._handle_single_command(group_member, 'OFF')
        else:
            lightbulb = 'lightbulb{}'.format(command)
            cls._handle_selected_lightbulb(lightbulb, group_members)

    @classmethod
    def _handle_nightmode(cls, lightbulb_item, group_members):
        nightmode_item = lightbulb_item.from_scripting('nightmode_item')
        if nightmode_item is None:
            return

        is_nightmode_active = False
        for group_member in group_members:
            brightness = cls.get_brightness(group_member)
            if brightness == 10:
                if is_nightmode_active:
                    is_nightmode_active = False
                    break
                else:
                    is_nightmode_active = True
            elif brightness > 0:
                is_nightmode_active = False
                break

        if is_nightmode_active:
            return

        nightmode = nightmode_item.get_string('RANDOM', True)

        if nightmode == 'RANDOM':
            nightmode = cls._select_random_nightmode(group_members)

        cls._handle_selected_lightbulb(nightmode, group_members, 'NIGHT')

    @classmethod
    def get_brightness(cls, lightbulb_item):
        brightness_item = lightbulb_item.from_scripting('brightness_item')
        rgb_item = lightbulb_item.from_scripting('rgb_item')

        brightness = 0
        if brightness_item:
            brightness = brightness_item.get_int(0)
        elif rgb_item:
            hsbcolor = rgb_item.get_value(cls.BLACK)
            brightness = hsbcolor.getBrightness().intValue()

        return brightness

    @staticmethod
    def _select_random_nightmode(group_members):
        cycles = {}

        for group_member in group_members:
            if group_member.is_scripting('cycles_item'):
                cycles_item = group_member.from_scripting('cycles_item')
                cycles[group_member.name] = cycles_item.get_int(0, True)
            else:
                cycles[group_member.name] = 0

        minimum_cycles = min(cycles.values())
        minimum_members = [
            k for k, v in cycles.iteritems() if v == minimum_cycles]

        return random.choice(minimum_members)

    @classmethod
    def _handle_selected_lightbulb(cls, lightbulb, group_members, on_command='ON'):
        for group_member in group_members:
            if group_member.name == lightbulb:
                cls._handle_single_command(group_member, on_command)

        for group_member in group_members:
            if group_member.name != lightbulb:
                cls._handle_single_command(group_member, 'OFF')
