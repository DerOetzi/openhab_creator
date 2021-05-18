from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (DateTime, Group, PointType,
                                          PropertyType, String, Switch)
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
        self._build_garbage(configuration)
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

    def _build_garbage(self, configuration: Configuration) -> None:
        Group('garbagecan')\
            .label(_('Garbage cans events'))\
            .append_to(self)

        if configuration.equipment.has('garbagecan'):
            for garbagecan in configuration.equipment.equipment('garbagecan'):
                Group(garbagecan.item_ids.garbagecan)\
                    .label(garbagecan.blankname)\
                    .icon('garbagecan')\
                    .location(garbagecan.location)\
                    .semantic(garbagecan)\
                    .append_to(self)

                String(garbagecan.item_ids.title)\
                    .label(_('Event title'))\
                    .icon('garbagecan')\
                    .equipment(garbagecan)\
                    .semantic(PointType.STATUS)\
                    .channel(garbagecan.points.channel('title'))\
                    .append_to(self)

                DateTime(garbagecan.item_ids.begin)\
                    .dateonly_weekday()\
                    .label(garbagecan.blankname)\
                    .icon('garbagecan')\
                    .equipment(garbagecan)\
                    .groups('garbagecan')\
                    .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                    .channel(garbagecan.points.channel('begin'))\
                    .scripting({
                        'message': garbagecan.message,
                        'identifier': garbagecan.identifier
                    })\
                    .append_to(self)
