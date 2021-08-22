# pylint: skip-file

import random

from core.jsr223.scope import (NULL, OFF, ON, UNDEF, DecimalType, HSBType,
                               PercentType, events, itemRegistry)
from core.log import LOG_PREFIX, logging
from personal.dateutils import DateUtils
from personal.item import Group, Item


class LightUtils(object):
    BLACK = HSBType(DecimalType(0), PercentType(0), PercentType(0))

    log = logging.getLogger('{}.LightUtils'.format(LOG_PREFIX))

    @classmethod
    def command(cls, lightbulb_item, command):
        is_thing = lightbulb_item.scripting('is_thing')

        if is_thing:
            cls._handle_single_command(lightbulb_item, command)
        else:
            cls._handle_group_command(lightbulb_item, command)

        lightcontrol_item = lightbulb_item.from_scripting('control_item')
        lightcontrol_item.post_update(command)

    @classmethod
    def _handle_single_command(cls, lightbulb_item, command):

        if command in ['ALL', 'ON']:
            cls._execute(lightbulb_item, 100, ON, cls.color())
        elif command == 'NIGHT':
            cls._execute(lightbulb_item, 10, ON, cls.color(10))
        elif command == 'OFF':
            updated = cls._execute(lightbulb_item, 0, OFF, cls.BLACK)

            if updated:
                cls._increment_switchingcycles(lightbulb_item)

    @staticmethod
    def _increment_switchingcycles(lightbulb_item):
        cycles_item = lightbulb_item.from_scripting('cycles_item')
        cycles = cycles_item.get_int(0, True)
        cycles += 1
        cycles_item.post_update(cycles)

    @classmethod
    def _execute(cls, lightbulb_item, brightness, onoff, color):
        updated = False

        brightness_item = lightbulb_item.from_scripting('brightness_item')
        onoff_item = lightbulb_item.from_scripting('onoff_item')
        rgb_item = lightbulb_item.from_scripting('rgb_item')

        if brightness_item:
            actual = brightness_item.get_int(0)
            if actual != brightness:
                brightness_item.send_command(brightness)
                updated = True
        elif onoff_item:
            actual = onoff_item.get_onoff()
            if actual != onoff:
                onoff_item.send_command(onoff)
                updated = True
        elif rgb_item:
            actual = rgb_item.get_value(cls.BLACK)
            if actual != color:
                rgb_item.send_command(color)
                updated = True

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
            command = 'lightbulb{}'.format(command)
            for group_member in group_members:
                if group_member.name == command:
                    cls._handle_single_command(group_member, 'ON')
                else:
                    cls._handle_single_command(group_member, 'OFF')

    @classmethod
    def _handle_nightmode(cls, lightbulb_item, group_members):
        nightmode_item = lightbulb_item.from_scripting('nightmode_item')
        if nightmode_item is None:
            return

        nightmode = nightmode_item.get_string('RANDOM', True)

        if nightmode == 'RANDOM':
            nightmode = random.choice(group_members.members_names)

        for group_member in group_members:
            if group_member.name == nightmode:
                cls._handle_single_command(group_member, 'NIGHT')
            else:
                cls._handle_single_command(group_member, 'OFF')
