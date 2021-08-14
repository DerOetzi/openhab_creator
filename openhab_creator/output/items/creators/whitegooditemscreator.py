from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (DateTime, Group, Number, PointType,
                                          PropertyType, String, Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(5)
class WhiteGoodItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('WhiteGood')\
            .append_to(self)

        Group('WhiteGoodReminderDone')\
            .append_to(self)

        for whitegood in configuration.equipment.equipment('whitegood'):
            Group(whitegood.item_ids.whitegood)\
                .label(whitegood.blankname)\
                .location(whitegood.location)\
                .icon(whitegood.category)\
                .semantic(whitegood)\
                .append_to(self)

            String(whitegood.item_ids.state)\
                .label(_('State'))\
                .map(MapTransformation.WHITEGOOD_STATE)\
                .icon(whitegood.category)\
                .equipment(whitegood)\
                .config()\
                .semantic(PointType.STATUS)\
                .append_to(self)

            DateTime(whitegood.item_ids.start)\
                .label(_('Started at'))\
                .datetime()\
                .icon('datetime')\
                .equipment(whitegood)\
                .config()\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .append_to(self)

            if whitegood.has_reminder:
                Switch(whitegood.item_ids.done)\
                    .label(_('Cleaning {name}').format(name=whitegood.blankname))\
                    .icon('checked')\
                    .equipment(whitegood)\
                    .groups('WhiteGoodReminderDone')\
                    .config()\
                    .semantic(PointType.CONTROL)\
                    .scripting({
                        'countdown_item': whitegood.item_ids.countdown,
                        'reminder_cycles': whitegood.reminder['cycles']
                    })\
                    .append_to(self)

                Number(whitegood.item_ids.countdown)\
                    .label(_('Cleaning countdown'))\
                    .format('%d')\
                    .icon('countdown')\
                    .equipment(whitegood)\
                    .config()\
                    .semantic(PointType.SETPOINT)\
                    .append_to(self)

        self.write_file('whitegood')
