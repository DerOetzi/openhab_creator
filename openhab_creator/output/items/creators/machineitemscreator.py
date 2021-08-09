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
class MachineItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        for machine in configuration.equipment.equipment('machine'):
            Group(machine.item_ids.machine)\
                .label(machine.blankname)\
                .location(machine.location)\
                .semantic(machine)\
                .append_to(self)

            String(machine.item_ids.state)\
                .label(_('State'))\
                .map(MapTransformation.MACHINE_STATE)\
                .equipment(machine)\
                .config()\
                .semantic(PointType.STATUS)\
                .append_to(self)

            DateTime(machine.item_ids.start)\
                .label(_('Started at'))\
                .datetime()\
                .equipment(machine)\
                .config()\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .append_to(self)

            if machine.has_reminder:
                Switch(machine.item_ids.done)\
                    .label(_('Cleaning'))\
                    .equipment(machine)\
                    .config()\
                    .semantic(PointType.CONTROL)\
                    .append_to(self)

                Number(machine.item_ids.countdown)\
                    .label(_('Cleaning countdown'))\
                    .format('%d')\
                    .equipment(machine)\
                    .config()\
                    .semantic(PointType.SETPOINT)\
                    .append_to(self)

        self.write_file('machine')
