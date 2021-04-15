from core.jsr223.scope import itemRegistry, NULL, UNDEF, StringType, events
from core.date import to_java_zoneddatetime
from core.actions import PersistenceExtensions
from core.metadata import get_metadata

from java.time import ZonedDateTime


class Item(object):
    def __init__(self, item_or_item_name):
        if isinstance(item_or_item_name, basestring):
            self.item = itemRegistry.getItem(item_or_item_name)
            self.name = item_or_item_name
        else:
            self.item = item_or_item_name
            self.name = item_or_item_name.name

        metadata = get_metadata(self.name, 'scripting')
        self.metadata = {} if metadata is None else metadata.configuration

    def get_value(self, default_value=None, event=None, update_empty=False):
        if event is not None and hasattr(event, 'itemName') and event.itemName == self.name:
            new_state = event.itemCommand if hasattr(
                event, 'itemCommand') else event.itemState
        else:
            new_state = self.item.state

        if update_empty and new_state in [NULL, UNDEF]:
            new_state = self.typed_value(new_state, default_value)
            self.post_update(new_state)
        else:
            new_state = self.typed_value(new_state, default_value)

        return new_state

    def typed_value(self, new_state, default_value=None):
        if isinstance(default_value, int):
            if isinstance(new_state, StringType):
                typed_value = int(new_state.toFullString())
            else:
                typed_value = new_state.intValue() if new_state not in [
                    NULL, UNDEF] else default_value
        elif isinstance(default_value, float):
            if isinstance(new_state, StringType):
                typed_value = float(new_state.toFullString())
            else:
                typed_value = new_state.floatValue() if new_state not in [
                    NULL, UNDEF] else default_value
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

    def scripting(self, key):
        return self.metadata[key]

    def post_update(self, value):
        events.postUpdate(self.item, value)

    def send_command(self, value):
        events.sendCommand(self.item, value)

    def delta_since(self, since):
        delta_since = PersistenceExtensions.deltaSince(
            self.item, since, 'influxdb')

        if delta_since is not None:
            delta_since = delta_since.floatValue()

        return delta_since
