from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import String, Switch, DateTime
from openhab_creator.models.common import MapTransformation
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(1)
class CalendarItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        self._build_holiday()
        self._build_special_day()
        self._build_birthdays()
        self.write_file('calendar')

    def _build_holiday(self):
        String('holidayName')\
            .label(_('Holiday'))\
            .format('%s')\
            .icon('calendar')\
            .append_to(self)

        Switch('holiday')\
            .label(_('Holiday'))\
            .map(MapTransformation.ACTIVE)\
            .icon('calendar')\
            .append_to(self)

    def _build_special_day(self):
        DateTime('nextSpecialDay')\
            .label('NextSpecialDay')\
            .dateonly_weekday()\
            .icon('calendar')\
            .append_to(self)

        String('todaySpecialDay')\
            .label(_('Special today'))\
            .format('%s')\
            .icon('calendar')\
            .scripting({'birthday': _('Birthday: {}'), 'birthdays': _('Birthdays: {}')})\
            .append_to(self)

    def _build_birthdays(self) -> None:
        for i in range(0, 10):
            DateTime(f'nextBirthday{i}')\
                .label(f'Birthday {i}')\
                .dateonly_weekday()\
                .icon('birthday')\
                .append_to(self)
