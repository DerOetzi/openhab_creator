# pylint: skip-file
import personal.autoitemmanager
from core.log import LOG_PREFIX, logging
from personal.autoitemmanager import AutoItemManager
from personal.dateutils import DateUtils
from personal.item import Group, Item

reload(personal.autoitemmanager)


class HeatingUtils(object):
    log = logging.getLogger('{}.HeatingUtils'.format(LOG_PREFIX))

    @classmethod
    def automation(cls, heating_item, is_active, is_heating):
        if is_heating:
            if is_active:
                cls.command(heating_item, 'COMFORT')
            else:
                cls.command(heating_item, 'ECO')
        else:
            cls.command(heating_item, 'CLOSED')

    @classmethod
    def manual(cls, heating_item, command, event=None):
        AutoItemManager.instance().change_auto(
            heating_item.from_scripting('auto_item'), event)

        cls.command(heating_item, command)

    @classmethod
    def command(cls, heating_item, command):
        is_thing = heating_item.scripting('is_thing')

        if is_thing:
            cls.__handle_single_command(heating_item, command)
        else:
            cls.__handle_group_command(heating_item, command)

        heatingcontrol_item = heating_item.from_scripting('control_item')
        heatingcontrol_item.post_update(command)

    @classmethod
    def __handle_single_command(cls, heating_item, command):
        if command == 'CLOSED':
            cls._execute(heating_item, 0.0, 'heatmode_off')
        elif command == 'COMFORT':
            comfort_item = heating_item.from_scripting('comfort_item')

            cls._execute(heating_item, comfort_item.get_float(
                21.0, True), 'heatmode_comfort')
        elif command == 'ECO':
            eco_item = heating_item.from_scripting('eco_item')
            cls._execute(heating_item, eco_item.get_float(
                17.0, True), 'heatmode_eco')
        elif command == 'BOOST':
            new_temperature = heating_item.scripting('boost_temp').floatValue()
            cls._execute(heating_item, new_temperature, 'heatmode_boost')

    @staticmethod
    def _execute(heating_item, new_temperature, new_heatmode_key):
        if new_temperature > 0.0:
            setpoint_item = heating_item.from_scripting('setpoint_item')
            actual_temperature = setpoint_item.get_float()

            if actual_temperature is None or actual_temperature != new_temperature:
                setpoint_item.send_command(new_temperature)

        heatmode_item = heating_item.from_scripting('heatmode_item')
        if heatmode_item.is_scripting(new_heatmode_key):
            heatmode_item.send_command(
                heatmode_item.scripting(new_heatmode_key))

    @classmethod
    def __handle_group_command(cls, heating_item, command):
        group_members = Group.from_list(
            heating_item.scripting('subequipment').split(','))

        for group_member in group_members:
            cls.__handle_single_command(group_member, command)
