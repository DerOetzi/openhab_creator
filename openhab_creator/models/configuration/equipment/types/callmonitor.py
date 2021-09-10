from __future__ import annotations

from typing import Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)


class CallMonitorItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.callmonitor

    @property
    def callmonitor(self) -> str:
        return self._identifier('callmonitor')

    @property
    def incoming(self) -> str:
        return self._identifier('incoming')

    @property
    def incoming_resolved(self) -> str:
        return self._identifier('incomingResolved')

    @property
    def lastincoming(self) -> str:
        return self._identifier('lastIncoming')

    @property
    def state(self) -> str:
        return self._identifier('callstate')

    @property
    def laststate(self) -> str:
        return self._identifier('lastCallstate')


@EquipmentType()
class CallMonitor(Equipment):
    def __init__(self, **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: CallMonitorItemIdentifiers = CallMonitorItemIdentifiers(
            self)

    @property
    def item_ids(self) -> CallMonitorItemIdentifiers:
        return self._item_ids

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('callmonitor')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Call monitor")
        return f'{self.name} ({typed})'
