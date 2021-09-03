# pylint: skip-file
from core.jsr223.scope import OFF, ON
from core.log import LOG_PREFIX, logging
from personal.dateutils import DateUtils
from personal.item import Group
from personal.timermanager import TimerManager


class AutoItemManager(object):
    log = logging.getLogger('{}.AutoItemManager'.format(LOG_PREFIX))

    __instance = None

    @staticmethod
    def instance():
        if AutoItemManager.__instance is None:
            AutoItemManager()

        return AutoItemManager.__instance

    def __init__(self):
        if AutoItemManager.__instance is None:
            self.timers = TimerManager('AutoItemManager')
            AutoItemManager.__instance = self
        else:
            raise RuntimeError('This class is a singleton')

    @staticmethod
    def startup():
        for group_name in ['AutoLight', 'AutoHeating']:
            for auto_item in Group(group_name):
                reactivation_item = auto_item.from_scripting(
                    'reactivation_item')
                reactivation_period = reactivation_item.get_int(0, True)
                if reactivation_period > 0:
                    auto_item.post_update(ON)

    def change_auto(self, auto_item, event=None):
        automodus = auto_item.get_onoff(True)
        reactivation_item = auto_item.from_scripting('reactivation_item')
        reactivation_period = reactivation_item.get_int(0, True)

        if (event is not None
                and (event.itemName == auto_item.scripting('control_item')
                     or (event.itemName == auto_item.name and not automodus))):
            auto_item.post_update(OFF)
            automodus = False

            if reactivation_period > 0:
                self.timers.activate(auto_item.name, lambda auto_item=auto_item: auto_item.send_command(
                    ON), DateUtils.now().plusMinutes(reactivation_period))

        display_item = auto_item.from_scripting('display_item')
        if display_item is not None:
            hide_item = auto_item.from_scripting('hide_item')
            if not automodus and not hide_item.get_onoff(True) and reactivation_period > 0:
                display_item.post_update(ON)
            else:
                display_item.post_update(OFF)

        return automodus
