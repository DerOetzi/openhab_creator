from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (
    AISensorDataType, Group, Number, PointType, PropertyType)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.pvsystem import PVSystem


@ItemsCreatorPipeline(4)
class PVSystemItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        for pvsystem in configuration.equipment.equipment('pvsystem'):
            self.build_pvsystem(pvsystem)
            self.build_inverter(pvsystem)
            self.build_pv_panels(pvsystem)

        self.write_file('pvsystem')

    def build_pvsystem(self, pvsystem: PVSystem) -> None:
        Group(pvsystem.item_ids.pvsystem)\
            .label(pvsystem.blankname)\
            .location(pvsystem.location)\
            .icon('pvsystem')\
            .semantic(pvsystem)\
            .append_to(self)
        
        Group(pvsystem.item_ids.inverter)\
            .label(_('Inverter'))\
            .equipment(pvsystem.item_ids.pvsystem)\
            .icon('inverter')\
            .semantic('Equipment')\
            .append_to(self)
        
        Group(pvsystem.item_ids.pv_panels)\
            .label(_('PV panels'))\
            .equipment(pvsystem.item_ids.pvsystem)\
            .icon('pvpanels')\
            .semantic('Equipment')\
            .append_to(self)
        
        Group(pvsystem.item_ids.pv_grid)\
            .label(_('Grid'))\
            .equipment(pvsystem.item_ids.pvsystem)\
            .icon('grid')\
            .semantic('Equipment')\
            .append_to(self)
        
        if pvsystem.has_battery:
            Group(pvsystem.item_ids.pv_battery)\
                .label(_('Battery'))\
                .equipment(pvsystem.item_ids.pvsystem)\
                .semantic('Battery')\
                .append_to(self)

    def build_inverter(self, pvsystem: PVSystem) -> None:
        if pvsystem.points.has_energy_produced:
            Number(pvsystem.item_ids.energy_produced)\
                .label(_('Produced energy inverter'))\
                .energy(1)\
                .unit('kWh')\
                .equipment(pvsystem.item_ids.inverter)\
                .icon('energy')\
                .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                .channel(pvsystem.points.channel('energy_produced'))\
                .append_to(self)
            
        if pvsystem.points.has_power_inverter_consumption:
            Number(pvsystem.item_ids.power_inverter_consumption)\
                .label(_('Consumption inverter'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.inverter)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_inverter_consumption'))\
                .append_to(self)
            
        if pvsystem.points.has_power_inverter_production:
            Number(pvsystem.item_ids.power_inverter_production)\
                .label(_('Production inverter'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.inverter)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_inverter_production'))\
                .append_to(self)

    def build_pv_panels(self, pvsystem: PVSystem) -> None:
        if pvsystem.points.has_power_pv:
            Number(pvsystem.item_ids.power_pv)\
                .label(_('Power PV'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_panels)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_pv'))\
                .append_to(self)

        if pvsystem.points.has_energy_pv_today:
            Number(pvsystem.item_ids.energy_pv_today)\
                .label(_('Energy PV today'))\
                .energy(3)\
                .unit('kWh')\
                .equipment(pvsystem.item_ids.pv_panels)\
                .icon('energy')\
                .semantic(PointType.MEASUREMENT, PropertyType.ENERGY)\
                .channel(pvsystem.points.channel('energy_pv_today'))\
                .append_to(self)
        