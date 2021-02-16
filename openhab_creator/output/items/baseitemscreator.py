from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from openhab_creator import _
from openhab_creator.exception import BuildException
from openhab_creator.models.items import Group, Number, Switch
from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration import Configuration


class BaseItemsCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('items', outputdir)

    def build(self, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build")

    def _create_battery(self, equipment: Equipment, parent_equipment: str) -> None:
        if equipment.has_battery:
            Group(equipment.battery_id)\
                .label(_('Battery'))\
                .groups(parent_equipment)\
                .tags('Battery')\
                .append_to(self)

            if equipment.has_battery_low:
                Switch(equipment.lowbattery_id)\
                    .label(_('Battery low'))\
                    .icon('lowbattery')\
                    .groups('LowBattery')\
                    .channel(equipment.channel('battery_low'))\
                    .append_to(self)

            if equipment.has_battery_level:
                Number(equipment.levelbattery_id)\
                    .label(_('Battery level'))\
                    .percentage()\
                    .icon('battery')\
                    .groups(equipment.battery_id)\
                    .sensor('batteries', equipment.influxdb_tags)\
                    .channel(equipment.channel('battery_level'))\
                    .tags('Measurement', 'Level')\
                    .append_to(self)
