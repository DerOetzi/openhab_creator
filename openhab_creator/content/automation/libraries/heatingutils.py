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

    @staticmethod
    def __handle_single_command(heating_item, command):
        new_temperature = 0.0

        if command == 'CLOSED':
            new_temperature = heating_item.scripting('off_temp').floatValue()
        elif command == 'COMFORT':
            comfort_item = heating_item.from_scripting('comfort_item')
            new_temperature = comfort_item.get_float(21.0, True)
        elif command == 'ECO':
            eco_item = heating_item.from_scripting('eco_item')
            new_temperature = eco_item.get_float(17.0, True)
        elif command == 'BOOST':
            new_temperature = heating_item.scripting('boost_item').floatValue()

        if new_temperature != 0.0:
            setpoint_item = heating_item.from_scripting('setpoint_item')
            actual_temperature = setpoint_item.get_float()

            if actual_temperature is None or actual_temperature != new_temperature:
                setpoint_item.send_command(new_temperature)

    @classmethod
    def __handle_group_command(cls, heating_item, command):
        group_members = Group.from_list(
            heating_item.scripting('subequipment').split(','))

        for group_member in group_members:
            cls.__handle_single_command(group_member, command)
