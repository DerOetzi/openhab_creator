from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)


class ReminderItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.reminder

    @property
    def reminder(self) -> str:
        return self._identifier('reminder')

    @property
    def datetime(self) -> str:
        return self._identifier('reminderDateTime')

    @property
    def confirm(self) -> str:
        return self._identifier('reminderConfirm')


@EquipmentType()
class Reminder(Equipment):
    #pylint: disable=too-many-instance-attributes

    def __init__(self,
                 message: str,
                 recipient: Optional[str] = 'broadcast',
                 icon: Optional[str] = 'calendar',
                 interval: Optional[int] = None,
                 time: Optional[str] = None,
                 counter: Optional[int] = None,
                 **equipment_configuration: Dict):
        #pylint: disable=too-many-arguments

        super().__init__(**equipment_configuration)

        self._item_ids = ReminderItemIdentifiers(self)

        self.message: str = message
        self.recipient: str = recipient
        self.icon: str = icon

        self.interval: int = interval
        self.hour: Optional[int] = None
        self.minutes: Optional[int] = None
        if time is not None:
            self.hour, self.minutes = [int(x) for x in time.split(':')]

        self.counter: Optional[int] = counter

    @property
    def item_ids(self) -> ReminderItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('reminder')
        if self.is_calendar:
            categories.append('calendar')
        elif self.is_counter:
            categories.append('countdown')

        return categories

    @property
    def is_calendar(self) -> bool:
        return not (self.hour is None or self.interval is None)

    @property
    def is_counter(self) -> bool:
        return self.counter is not None

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def name_with_type(self) -> str:
        typed = _("Reminder")
        return f'{self.name} ({typed})'
