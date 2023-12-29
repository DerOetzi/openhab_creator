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
            Group(pvsystem.item_ids.powerflow)\
                .append_to(self)

            self.build_pvsystem(pvsystem)
            self.build_inverter(pvsystem)
            self.build_pv_panels(pvsystem)
            self.build_grid(pvsystem)
            self.build_battery(pvsystem)
            self.build_consumer(pvsystem)

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
            
        if pvsystem.has_wallbox:
            Group(pvsystem.item_ids.pv_wallbox)\
                .label(_('Wallbox'))\
                .equipment(pvsystem.item_ids.pvsystem)\
                .semantic('Equipment')\
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
                .sensor('pv_energy', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_inverter_consumption:
            Number(pvsystem.item_ids.power_inverter_consumption)\
                .label(_('Consumption inverter'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.inverter)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_inverter_consumption'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_inverter_production:
            Number(pvsystem.item_ids.power_inverter_production)\
                .label(_('Production inverter'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.inverter)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_inverter_production'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_inverter_pv_production:
            Number(pvsystem.item_ids.power_inverter_pv_production)\
                .label(_('Production PV inverter'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.inverter)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_inverter_pv_production'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_inverter_battery_production:
            Number(pvsystem.item_ids.power_inverter_battery_production)\
                .label(_('Production battery inverter'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.inverter)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_inverter_battery_production'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)

        if pvsystem.points.has_power_inverter_factor:
            Number(pvsystem.item_ids.power_inverter_factor)\
                .label(_('Power factor inverter'))\
                .percentage(2)\
                .unit('%')\
                .equipment(pvsystem.item_ids.inverter)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT)\
                .channel(pvsystem.points.channel('power_inverter_factor'))\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)

    def build_pv_panels(self, pvsystem: PVSystem) -> None:
        if pvsystem.points.has_power_pv:
            Number(pvsystem.item_ids.power_pv)\
                .label(_('Power PV'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_panels)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_pv'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
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
                .sensor('pv_energy', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
    def build_grid(self, pvsystem: PVSystem) -> None:
        if pvsystem.points.has_power_grid:
            Number(pvsystem.item_ids.power_grid)\
                .label(_('Power grid'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_grid)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_grid'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_grid_consumption:
            Number(pvsystem.item_ids.power_grid_consumption)\
                .label(_('Consumption grid'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_grid)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_grid_consumption'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_grid_delivery:
            Number(pvsystem.item_ids.power_grid_delivery)\
                .label(_('Delivery grid'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_grid)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_grid_delivery'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
    def build_battery(self, pvsystem: PVSystem) -> None:

        if pvsystem.points.has_power_battery:
            Number(pvsystem.item_ids.power_battery)\
                .label(_('Power battery'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_battery)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_battery'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_battery_charge:
            Number(pvsystem.item_ids.power_battery_charge)\
                .label(_('Charge power battery'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_battery)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_battery_charge'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_power_battery_discharge:
            Number(pvsystem.item_ids.power_battery_discharge)\
                .label(_('Discharge power battery'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_battery)\
                .groups(pvsystem.item_ids.powerflow)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_battery_discharge'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
            
        if pvsystem.points.has_battery_soc:
            Number(pvsystem.item_ids.battery_soc)\
                .percentage(0)\
                .label(_('Battery SoC'))\
                .equipment(pvsystem.item_ids.pv_battery)\
                .icon('battery')\
                .semantic(PointType.MEASUREMENT, PropertyType.LEVEL)\
                .channel(pvsystem.points.channel('battery_soc'))\
                .sensor('pv_battery', pvsystem.influxdb_tags)\
                .append_to(self)
        
    def build_consumer(self, pvsystem: PVSystem) -> None:
        if pvsystem.points.has_power_house:
            Number(pvsystem.item_ids.power_house)\
                .label(_('Power house'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pvsystem)\
                .icon('power')\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_house'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)
                
        if pvsystem.points.has_power_wallbox:
            Number(pvsystem.item_ids.power_wallbox)\
                .label(_('Power wallbox'))\
                .power(0)\
                .unit('W')\
                .equipment(pvsystem.item_ids.pv_wallbox)\
                .semantic(PointType.MEASUREMENT, PropertyType.POWER)\
                .channel(pvsystem.points.channel('power_wallbox'))\
                .sensor('pv_power', pvsystem.influxdb_tags)\
                .aisensor(AISensorDataType.NUMERICAL)\
                .append_to(self)