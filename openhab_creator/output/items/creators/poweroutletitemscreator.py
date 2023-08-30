from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.items import (AISensorDataType, Group, Number,
                                          NumberType, PointType, PropertyType,
                                          String, Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.poweroutlet import \
        PowerOutlet
    from openhab_creator.models.configuration.equipment.types.wallswitch import \
        WallSwitch


@ItemsCreatorPipeline(7)
class PowerOutletItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('PowerOutlet')\
            .append_to(self)

        has_wallswitches, wallswitches = configuration.equipment.has(
            'wallswitch')

        for poweroutlet in configuration.equipment.equipment('poweroutlet'):
            poweroutlet_item = Group(poweroutlet.item_ids.poweroutlet)\
                .semantic('PowerOutlet')\
                .append_to(self)

            if poweroutlet.poweroutlet_is_subequipment:
                poweroutlet_item\
                    .label(_('Power outlet'))\
                    .equipment(poweroutlet)
            else:
                poweroutlet_item\
                    .label(poweroutlet.name_with_type)\
                    .location(poweroutlet.location)

                if poweroutlet.points.has_onoff and has_wallswitches:
                    self.__build_buttons_assignment(poweroutlet, wallswitches)

            if poweroutlet.has_subequipment:
                for subpoweroutlet in poweroutlet.subequipment:
                    self.build_poweroutlet(subpoweroutlet)
            else:
                self.build_poweroutlet(poweroutlet)

        self.write_file('poweroutlet')

    def __build_buttons_assignment(self,
                                   poweroutlet: PowerOutlet,
                                   wallswitches: List[WallSwitch]) -> None:
        for wallswitch in wallswitches:
            for button_key in range(0, wallswitch.buttons_count):
                String(wallswitch.item_ids.buttonassignment(button_key, poweroutlet))\
                    .label(wallswitch.buttonassignment_name(button_key))\
                    .icon('configuration')\
                    .groups(wallswitch.item_ids.buttonassignment(button_key))\
                    .scripting({
                        'poweroutlet_item': poweroutlet.item_ids.onoff
                    })\
                    .append_to(self)

    def build_poweroutlet(self, poweroutlet: PowerOutlet):
        if poweroutlet.points.has_onoff:
            onoff_item = Switch(poweroutlet.item_ids.onoff)\
                .label(_('On/Off'))\
                .equipment(poweroutlet.item_ids.poweroutlet)\
                .config()\
                .semantic(PointType.SWITCH)\
                .channel(poweroutlet.points.channel('onoff'))\
                .scripting(poweroutlet.scripting)\
                .append_to(self)

            if poweroutlet.onoff_group is not None:
                onoff_item.groups(poweroutlet.onoff_group)

        if poweroutlet.points.has_power:
            Number(poweroutlet.item_ids.power)\
                .typed(NumberType.POWER)\
                .label(_('Power'))\
                .format('%,.2f W')\
                .icon('poweroutlet')\
                .equipment(poweroutlet.item_ids.poweroutlet)\
                .groups(poweroutlet.group)\
                .sensor('power', poweroutlet.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(poweroutlet.points.channel('power'))\
                .scripting(poweroutlet.scripting)\
                .append_to(self)
