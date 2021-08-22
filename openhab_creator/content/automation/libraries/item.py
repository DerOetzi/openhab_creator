# pylint: skip-file
from core.actions import PersistenceExtensions, Transformation
from core.date import format_date, to_java_zoneddatetime
from core.jsr223.scope import (NULL, OFF, UNDEF, StringType, events,
                               itemRegistry)
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

    @classmethod
    def from_event(cls, event):
        return cls(event.itemName, event)

    @classmethod
    def from_members_first(cls, group_name, event=None):
        return cls([item for item in itemRegistry.getItem(group_name).members][0], event)

    def from_scripting(self, name):
        item = None
        if self.is_scripting(name):
            item = self.__class__(self.scripting(name), self.event)

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

        return new_state

    def _update_empty(self, state, typed_state, update_empty):
        if update_empty and state in [NULL, UNDEF]:
            self.post_update(typed_state)

    def get_value(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        typed_state = state if state not in [NULL, UNDEF] else default_value
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_int(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        if isinstance(state, StringType):
            typed_state = int(state.toFullString())
        else:
            typed_state = state.intValue() if state not in [
                NULL, UNDEF] else default_value
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_float(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        if isinstance(state, StringType):
            typed_state = float(state.toFullString())
        else:
            typed_state = state.floatValue() if state not in [
                NULL, UNDEF] else default_value
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_string(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        typed_state = state.toFullString() if state not in [
            NULL, UNDEF] else default_value
        self._update_empty(state, typed_state, update_empty)
        return typed_state

    def get_datetime(self, default_value=None, update_empty=False, event=None):
        state = self._get_state(event)
        typed_state = to_java_zoneddatetime(state) if state not in [
            NULL, UNDEF] else default_value
        return typed_state

    def get_onoff(self, update_empty=False, default_value=OFF, event=None):
        return self.get_value(default_value, update_empty, event)

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

    def send_command(self, value):
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

    def maximum_since(self, since):
        maximum_since = PersistenceExtensions.maximumSince(
            self._item, since, 'influxdb')

        if maximum_since is not None:
            maximum_since = maximum_since.state.floatValue()

        return maximum_since

    @staticmethod
    def transform_map(map_name, value):
        return Transformation.transform("MAP", map_name + ".map", u"{}".format(value))


class Group(object):
    def __init__(self, item_or_item_name=None, event=None):
        self.item = None
        self.members = []
        self.members_names = []

        self.log = logging.getLogger('{}.Group'.format(LOG_PREFIX))

        if item_or_item_name is not None:
            self.item = Item(item_or_item_name, event)
            for member in self.item.item.members:
                self.members_names.append(member.name)
                self.members.append(Item(member, event))

    @classmethod
    def from_list(cls, member_list, event=None):
        group = cls(event=event)

        for member in member_list:
            group.members.append(Item(member))

        group.members_names = member_list

        return group

    def __iter__(self):
        return iter(self.members)
