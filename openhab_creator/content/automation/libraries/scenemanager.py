# pylint: skip-file
from core.jsr223.scope import (NULL, OFF, ON, UNDEF, DecimalType, HSBType,
                               PercentType, events, itemRegistry)
from core.log import LOG_PREFIX, logging
from personal.dateutils import DateUtils
from personal.ephemerisutils import EphemerisUtils
from personal.item import Group, Item
from personal.timermanager import TimerManager
from personal.lightutils import LightUtils
from personal.heatingutils import HeatingUtils
from personal.autoitemmanager import AutoItemManager


class TimeSceneItem:
    def __init__(self, identifier, default_time):
        self.identifier = identifier
        self.default_time = default_time

    def __str__(self):
        return self.identifier

    def __eq__(self, other):
        return isinstance(other, TimeSceneItem) and self.identifier == other.identifier


class TimeScene(object):
    NIGHT = TimeSceneItem('Night', 0)
    BREAKFAST = TimeSceneItem('Breakfast', 6)
    FORENOON = TimeSceneItem('Forenoon', 8)
    LUNCH = TimeSceneItem('Lunch', 13)
    AFTERNOON = TimeSceneItem('Afternoon', 14)
    DINNER = TimeSceneItem('Dinner', 18)
    EVENING = TimeSceneItem('Evening', 20)

    @classmethod
    def scenes(cls):
        return [cls.NIGHT, cls.BREAKFAST, cls.FORENOON, cls.LUNCH,
                cls.AFTERNOON, cls.DINNER, cls.EVENING]

    @classmethod
    def from_string(cls, identifier):
        found = None

        for time_scene in cls.scenes():
            if time_scene.identifier == identifier:
                found = time_scene
                break

        return found


class SpecialSceneItem(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return self.identifier

    def __eq__(self, other):
        return isinstance(other, SpecialSceneItem) and self.identifier == other.identifier


class SpecialScene(object):
    PARTY = SpecialSceneItem('Party')
    ABSENCE = SpecialSceneItem('Absence')

    @classmethod
    def scenes(cls):
        return [cls.ABSENCE, cls.PARTY]

    @classmethod
    def from_string(cls, identifier):
        found = None

        for time_scene in cls.scenes():
            if time_scene.identifier == identifier:
                found = time_scene
                break

        return found


class SceneItem(object):
    auto_scene = Item('autoScene')
    auto_scene_active = Item('autoSceneActive')
    wayhome = Item('wayhome')
    presences = Item('Presences')
    darkness = Item('darkness')
    heating = Item('heating')
    guest_stayed = Item('autoGuestStayed')
    holidays = Item('PersonStateHolidays')
    holidays_tomorrow = Item('PersonStateTomorrowHolidays')
    sickness = Item('PersonStateSickness')
    sickness_tomorrow = Item('PersonStateTomorrowSickness')

    @classmethod
    def update_event(cls, event):
        cls.auto_scene.event = event
        cls.auto_scene_active.event = event
        cls.wayhome.event = event
        cls.presences.event = event
        cls.darkness.event = event
        cls.heating.event = event
        cls.holidays.event = event
        cls.holidays_tomorrow.event = event
        cls.sickness.event = event
        cls.sickness_tomorrow.event = event


class SceneManager(object):
    log = logging.getLogger('{}.SceneManager'.format(LOG_PREFIX))

    __instance = None

    @staticmethod
    def instance():
        if SceneManager.__instance is None:
            SceneManager()

        return SceneManager.__instance

    def __init__(self):
        if SceneManager.__instance is None:
            self.timers = TimerManager('SceneManager')
            self.scenes = {}
            self.scene_members = None
            self.auto = False

            SceneManager.__instance = self
        else:
            raise RuntimeError('This class is a singleton')

    def read_timeconfig(self, event=None):
        self.scenes['WorkingDay'] = {}
        self.scenes['Weekend'] = {}

        for day_type in self.scenes.keys():
            for scene in TimeScene.scenes():
                time = Item('sceneTime{}{}'.format(day_type,
                                                   scene.identifier), event).get_int(scene.default_time, True)
                self.scenes[day_type][scene.identifier] = time

        self.log.debug(self.scenes)

    def start_scene_timer(self):
        day_type = self.day_type()
        date = DateUtils.now()

        found_scene = False
        for scene in TimeScene.scenes()[1:]:
            date = DateUtils.set_time(
                date, self.scenes[day_type][scene.identifier])
            if date.isAfter(DateUtils.now()):
                found_scene = True
                break

        if not found_scene:
            day_type = self.day_type(True)
            scene = TimeScene.NIGHT
            date = DateUtils.set_time(date.plusDays(
                1), self.scenes[day_type][scene.identifier])

        self.log.info('Next scene %s at %s', scene, date)

        def timer(): return SceneManager.instance().scene_timer_triggered()

        self.timers.activate('scenetimer', timer, date)

    def scene_timer_triggered(self):
        self.change_scene()
        self.start_scene_timer()

    def change_scene(self, event=None):
        SceneItem.update_event(event)
        self.auto = SceneItem.auto_scene.get_onoff()

        if event is not None:
            if event.itemName == 'wayhome' and self.wayhome():
                self.auto = True
                SceneItem.auto_scene.post_update(ON)
            elif event.itemName == 'autoSceneActive':
                self.auto = False
                SceneItem.auto_scene.post_update(OFF)

        actual_scene = self.actual_scene()
        SceneItem.auto_scene_active.post_update(actual_scene.identifier)
        self.log.info('Actual scene: %s', actual_scene)

        self.scene_members = Group('sceneAssignment{}'.format(actual_scene))
        self.log.debug(self.scene_members)
        self.activate_scene(event)

    def actual_scene(self):
        if self.auto or self.wayhome():
            if self.presences() or self.wayhome():
                actual_scene = self.actual_timescene()
            else:
                actual_scene = SpecialScene.ABSENCE
        else:
            actual_scene_string = SceneItem.auto_scene_active.get_string()
            actual_scene = TimeScene.from_string(actual_scene_string)
            if actual_scene is None:
                actual_scene = SpecialScene.from_string(actual_scene_string)

        return actual_scene

    def wayhome(self):
        return SceneItem.wayhome.get_onoff(True)

    def is_night(self):
        actual_scene = self.actual_scene()
        actual_timescene = self.actual_timescene()

        return (actual_scene == TimeScene.NIGHT
                or (actual_timescene == TimeScene.NIGHT and actual_scene != SpecialScene.PARTY))

    def actual_timescene(self):
        day_type = self.day_type()
        date = DateUtils.now()

        found_scene = False
        for scene in reversed(TimeScene.scenes()):
            date = DateUtils.set_time(
                date, self.scenes[day_type][scene.identifier])
            if DateUtils.now().isAfter(date):
                found_scene = True
                break

        if not found_scene or (TimeScene.NIGHT == scene and self.wayhome()):
            scene = TimeScene.EVENING

        self.log.debug('Actual time scene: %s', scene)

        return scene

    @staticmethod
    def day_type(tomorrow=False):
        day_type = 'WorkingDay'
        if tomorrow:
            if (EphemerisUtils.is_freeday(1)
                or SceneItem.holidays_tomorrow.get_int(0)
                    or SceneItem.sickness_tomorrow.get_int(0)):
                day_type = 'Weekend'
        else:
            if (EphemerisUtils.is_freeday()
                or SceneItem.holidays.get_int(0)
                    or SceneItem.sickness.get_int(0)):
                day_type = 'Weekend'

        return day_type

    def presences(self):
        return SceneItem.presences.get_int(0) == 1

    def activate_scene(self, event=None):
        SceneItem.update_event(event)
        guest_stayed = SceneItem.guest_stayed.get_onoff(True)
        is_weekend = EphemerisUtils.is_weekend() or EphemerisUtils.is_holiday()
        is_night = self.is_night()
        is_absence = not self.presences() or SpecialScene.ABSENCE == self.actual_scene()
        is_darkness = SceneItem.darkness.get_onoff()
        is_heating = SceneItem.heating.get_onoff()

        for assigned_item in self.scene_members:
            is_location_active = self.is_location_active(
                assigned_item, guest_stayed, is_weekend, event)
            self._handle_location(
                assigned_item, is_location_active, is_night, is_absence, is_darkness, is_heating, event)

    def is_location_active(self, assigned_item, guest_stayed, is_weekend, event=None):
        assigned = assigned_item.get_string('OFF', True, event)

        return (assigned == 'ALWAYS'
                or (not is_weekend and assigned == 'WORKINGDAY')
                or (is_weekend and assigned == 'WEEKEND')
                or (guest_stayed and assigned == 'GUEST'))

    def _handle_location(self, assigned_item,
                         is_location_active, is_night,
                         is_absence,
                         is_darkness, is_heating,
                         event=None):
        active_item = assigned_item.from_scripting('active_item', event)
        if is_location_active:
            active_item.post_update(ON)
        else:
            active_item.post_update(OFF)

        for auto_item in Group(assigned_item.scripting('equipment_group'), event):
            automodus = AutoItemManager.instance().change_auto(auto_item, event)
            self.log.debug('%s: %s', auto_item.name, automodus)

            if not automodus:
                continue

            if auto_item.is_scripting('lightbulb_item'):
                lightbulb_item = auto_item.from_scripting('lightbulb_item')
                LightUtils.automation(
                    lightbulb_item, is_location_active, is_night, is_absence, is_darkness)
            elif auto_item.is_scripting('heating_item'):
                heating_item = auto_item.from_scripting('heating_item')
                HeatingUtils.automation(
                    heating_item, is_location_active, is_heating)
            elif auto_item.is_scripting('pump_item'):
                control_item = auto_item.from_scripting('control_item')
                if is_location_active:
                    control_item.send_command(ON, control_item.get_value())
                else:
                    control_item.send_command(OFF, control_item.get_value())

    def clear_timer(self):
        self.timers.cancel_all()


def scriptUnloaded():  # NOSONAR
    manager = SceneManager.instance()
    manager.clear_timer()
