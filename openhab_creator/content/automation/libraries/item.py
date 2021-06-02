# pylint: skip-file
from core.jsr223.scope import itemRegistry, NULL, UNDEF, StringType, events
from core.date import to_java_zoneddatetime, format_date
from core.actions import PersistenceExtensions, Transformation
from core.metadata import get_metadata

from java.time import ZonedDateTime


class Item(object):
    def __init__(self, item_or_item_name):
        if isinstance(item_or_item_name, basestring):
            self._item = itemRegistry.getItem(item_or_item_name)
            self.name = item_or_item_name
        else:
            self._item = item_or_item_name
            self.name = item_or_item_name.name

        metadata = get_metadata(self.name, 'scripting')
        self.metadata = {} if metadata is None else metadata.configuration

    @classmethod
    def from_event(cls, event):
        return cls(event.itemName)

    def from_scripting(self, name):
        return self.__class__(self.scripting(name))

    def get_value(self, default_value=None, event=None, update_empty=False):
        if event is not None and hasattr(event, 'itemName') and event.itemName == self.name:
            new_state = event.itemCommand if hasattr(
                event, 'itemCommand') else event.itemState
        else:
            new_state = self._item.state

        if update_empty and new_state in [NULL, UNDEF]:
            new_state = self._typed_value(new_state, default_value)
            self.post_update(new_state)
        else:
            new_state = self._typed_value(new_state, default_value)

        return new_state

    def _typed_value(self, new_state, default_value=None):
        if isinstance(default_value, int):
            typed_value = self._typed_int(new_state, default_value)
        elif isinstance(default_value, float):
            typed_value = self._typed_float(new_state, default_value)
        elif isinstance(default_value, basestring):
            typed_value = new_state.toFullString() if new_state not in [
                NULL, UNDEF] else default_value
        elif isinstance(default_value, ZonedDateTime):
            typed_value = to_java_zoneddatetime(new_state) if new_state not in [
                NULL, UNDEF] else default_value
        else:
            typed_value = new_state if new_state not in [
                NULL, UNDEF] else default_value

        return typed_value

    def _typed_float(self, new_state, default_value):
        if isinstance(new_state, StringType):
            typed_value = float(new_state.toFullString())
        else:
            typed_value = new_state.floatValue() if new_state not in [
                NULL, UNDEF] else default_value

        return typed_value

    def _typed_int(self, new_state, default_value):
        if isinstance(new_state, StringType):
            typed_value = int(new_state.toFullString())
        else:
            typed_value = new_state.intValue() if new_state not in [
                NULL, UNDEF] else default_value

        return typed_value

    def scripting(self, key):
        return self.metadata[key]

    def set_label(self, label):
        self._item.setLabel(u'{}'.format(label))

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

    @staticmethod
    def transform_map(map_name, value):
        return Transformation.transform("MAP", map_name + ".map", u"{}".format(value))
