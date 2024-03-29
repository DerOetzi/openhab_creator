# pylint: skip-file
from core.actions import PersistenceExtensions, Transformation
from core.date import format_date, to_java_zoneddatetime
from core.jsr223.scope import (CLOSED, NULL, OFF, ON, OPEN, UNDEF, StringType,
                               events, itemRegistry)
from core.log import LOG_PREFIX, logging
from core.metadata import get_metadata
from java.time import ZonedDateTime


class Item(object):
    def __init__(self, item_or_item_name, event=None):
        if isinstance(item_or_item_name, basestring):
            self._item = itemRegistry.getItem(item_or_item_name)
            self.name = item_or_item_name
        else:
            self._item = item_or_item_name
            self.name = item_or_item_name.name

        self.event = event

        self.logger = logging.getLogger('{}.Item'.format(LOG_PREFIX))

        metadata = get_metadata(self.name, 'scripting')
        self.metadata = {} if metadata is None else metadata.configuration

        self.location = None
        if self.is_scripting('location_item'):
            self.location = self.from_scripting('location_item')

    @classmethod
    def from_event(cls, event):
        return cls(event.itemName, event)

    @classmethod
    def from_members_first(cls, group_name, event=None):
        return cls([item for item in itemRegistry.getItem(group_name).members][0], event)

    def from_scripting(self, name, event=None):
        item = None

        if event is None:
            event = self.event

        if self.is_scripting(name):
            item = self.__class__(self.scripting(name), event)

        return item

    @property
    def item(self):
        return self._item

    def _get_state(self, event=None):
        if event is None:
            event = self.event

        if event is not None and hasattr(event, 'itemName') and event.itemName == self.name:
            new_state = event.itemCommand if hasattr(
                event, 'itemCommand') else event.itemState
        else:
            new_state = self._item.state

        if new_state in [NULL, UNDEF]:
            new_state = None

        return new_state

    def _update_empty(self, state, typed_state, update_empty):
        if update_empty and state is None:
            self.post_update(typed_state)

    def get_value(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        typed_state = default_value if state is None else state
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_int(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        if isinstance(state, StringType):
            typed_state = int(state.toFullString())
        else:
            typed_state = default_value if state is None else state.intValue()
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_float(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        if isinstance(state, StringType):
            typed_state = float(state.toFullString())
        else:
            typed_state = default_value if state is None else state.floatValue()
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_string(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        typed_state = default_value if state is None else state.toFullString()
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_datetime(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        typed_state = default_value if state is None else to_java_zoneddatetime(
            state)
        return typed_state

    def get_onoff(self, update_empty=False, default_value=OFF, event=None):
        onoff = self.get_value(default_value, update_empty, event)
        return onoff == ON

    def get_openclosed(self, update_empty=False, default_value=CLOSED, event=None):
        openclosed = self.get_value(default_value, update_empty, event)
        return openclosed == OPEN

    def get_call(self, event=None):
        return self.get_value(event=event)

    def is_scripting(self, key):
        return key in self.metadata

    def scripting(self, key=None):
        if key is None:
            return self.metadata

        return self.metadata[key]

    def set_label(self, label):
        self._item.setLabel(u'{}'.format(label))

    def set_icon(self, icon):
        self._item.setCategory(u'{}'.format(icon))

    def post_update(self, value):
        if isinstance(value, ZonedDateTime):
            events.postUpdate(self._item, format_date(value))
        else:
            events.postUpdate(self._item, value)

    def send_command(self, value, actual_value=None):
        if actual_value is None or actual_value != value:
            if isinstance(value, ZonedDateTime):
                events.sendCommand(self._item, format_date(value))
            else:
                events.sendCommand(self._item, value)

    def delta_since(self, since):
        delta_since = PersistenceExtensions.deltaSince(
            self._item, since, 'influxdb')

        if delta_since is not None:
            delta_since = delta_since.floatValue()

        return delta_since

    def average_since(self, since):
        average_since = PersistenceExtensions.averageSince(
            self._item, since, 'influxdb')

        if average_since is not None:
            average_since = average_since.floatValue()

        return average_since

    def maximum_since(self, since):
        maximum_since = PersistenceExtensions.maximumSince(
            self._item, since, 'influxdb')

        if maximum_since is not None:
            maximum_since = maximum_since.state.floatValue()

        return maximum_since

    @staticmethod
    def transform_map(map_name, value):
        return Transformation.transform("MAP", map_name + ".map", u"{}".format(value))

    def __str__(self):
        return self.name


class Group(object):
    def __init__(self, item_or_item_name=None, event=None, only_direct_childs=True):
        self.item = None
        self.members = []
        self.members_names = []

        self.log = logging.getLogger('{}.Group'.format(LOG_PREFIX))

        if item_or_item_name is not None:
            self.item = Item(item_or_item_name, event)

            if only_direct_childs:
                group_members = self.item.item.members
            else:
                group_members = self.item.item.allMembers

            for member in group_members:
                self.members_names.append(member.name)
                self.members.append(Item(member, event))

    @classmethod
    def from_list(cls, member_list, event=None):
        group = cls(event=event)

        for member in member_list:
            group.members.append(Item(member))

        group.members_names = member_list

        return group

    def update_event(self, event):
        self.item.event = event
        for member in self.members:
            member.event = event

    def __iter__(self):
        return iter(self.members)

    def __str__(self):
        items = [x.name for x in self.members]

        return '[{}]'.format(', '.join(items))
