from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (Group, GroupType, Number, NumberType,
                                          PointType, PropertyType, String,
                                          Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.heating import \
        Heating


@ItemsCreatorPipeline(4)
class HeatingItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        self.__build_general_groups()

        self.__build_heating(configuration)

        self.__build_pumps(configuration)

        for heating in configuration.equipment.equipment('heating'):
            heating_item = self.__build_parent(heating)

            if not self.__build_subequipment(heating, heating_item):
                self.__build_thing(heating, heating_item)

        self.write_file('heating')

    def __build_general_groups(self) -> None:
        Group('Heatcontrol')\
            .label(_('Heat control items'))\
            .config()\
            .append_to(self)

        Group('HeatTemperature')\
            .config()\
            .append_to(self)

        Group('AutoHeating')\
            .label(_('Scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('AutoReactivationHeating')\
            .label(_('Reactivation scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('AutoAbsenceHeating')\
            .label(_('Absence scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('WarmWaterPumpControl')\
            .label(_('Warm water pump control items'))\
            .config()\
            .append_to(self)

        Group('AutoWarmWaterPump')\
            .label(_('Scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('AutoReactivationWarmWaterPump')\
            .label(_('Reactivation scene controlled configuration items'))\
            .auto()\
            .append_to(self)

    def __build_heating(self, configuration: Configuration) -> None:
        if not configuration.general.has_learninghouse('heating'):
            Switch('heating')\
                .label(_('Heatings'))\
                .icon('heating')\
                .config()\
                .append_to(self)

    def __build_pumps(self, configuration: Configuration) -> None:
        for pump in configuration.equipment.equipment('warmwaterpump'):
            Group(pump.item_ids.warmwaterpump)\
                .label(_('Warm water pump {blankname}').format(blankname=pump.blankname))\
                .icon('pump')\
                .location(pump.location)\
                .semantic(pump)\
                .scripting({
                    'control_item': pump.item_ids.onoff,
                    'auto_item': pump.item_ids.auto
                })\
                .append_to(self)

            Switch(pump.item_ids.auto)\
                .label(_('Scene controlled'))\
                .icon('auto')\
                .equipment(pump)\
                .groups('AutoWarmWaterPump', pump.location.autoequipment)\
                .semantic(PointType.CONTROL)\
                .scripting({
                    'pump_item': pump.item_ids.warmwaterpump,
                    'control_item': pump.item_ids.onoff,
                    'reactivation_item': pump.item_ids.autoreactivation
                })\
                .append_to(self)

            Number(pump.item_ids.autoreactivation)\
                .typed(NumberType.TIME)\
                .label(_('Reactivate scene controlled'))\
                .format('%d m')\
                .icon('reactivation')\
                .equipment(pump)\
                .groups('AutoReactivationWarmWaterPump')\
                .semantic(PointType.SETPOINT)\
                .append_to(self)

    def __build_parent(self, heating: Heating) -> Group:
        heating_item = Group(heating.item_ids.heating)\
            .label(_('Heating {blankname}').format(blankname=heating.blankname))\
            .icon('heating')\
            .location(heating.location)\
            .semantic(heating)\
            .scripting({
                'control_item': heating.item_ids.heatcontrol,
                'auto_item': heating.item_ids.auto,
                'presences_item': heating.item_ids.autoabsence,
                'comfort_item': heating.item_ids.comforttemperature,
                'eco_item': heating.item_ids.ecotemperature
            })\
            .append_to(self)

        String(heating.item_ids.heatcontrol)\
            .label(_('Heatcontrol'))\
            .icon('heatcontrol')\
            .equipment(heating)\
            .groups('Heatcontrol')\
            .semantic(PointType.CONTROL)\
            .scripting({
                'heating_item': heating.item_ids.heating
            })\
            .append_to(self)

        Switch(heating.item_ids.hide)\
            .label(_('Hide on temperature page'))\
            .icon('hide')\
            .config()\
            .equipment(heating)\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(heating.item_ids.auto)\
            .label(_('Scene controlled'))\
            .icon('auto')\
            .equipment(heating)\
            .groups('AutoHeating', heating.location.autoequipment)\
            .semantic(PointType.CONTROL)\
            .scripting({
                'heating_item': heating.item_ids.heating,
                'control_item': heating.item_ids.heatcontrol,
                'reactivation_item': heating.item_ids.autoreactivation,
                'display_item': heating.item_ids.autodisplay,
                'hide_item': heating.item_ids.hide
            })\
            .append_to(self)

        Switch(heating.item_ids.autodisplay)\
            .label(_('Display scene controlled'))\
            .equipment(heating)\
            .semantic(PointType.STATUS)\
            .append_to(self)

        Number(heating.item_ids.autoreactivation)\
            .typed(NumberType.TIME)\
            .label(_('Reactivate scene controlled'))\
            .format('%d m')\
            .icon('reactivation')\
            .equipment(heating)\
            .groups('AutoReactivationHeating')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Switch(heating.item_ids.autoabsence)\
            .label(_('Even in absence'))\
            .icon('absence')\
            .equipment(heating)\
            .groups('AutoAbsenceHeating')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Number(heating.item_ids.ecotemperature)\
            .label(_('ECO temperature'))\
            .temperature()\
            .icon('temperature')\
            .equipment(heating)\
            .groups('HeatTemperature')\
            .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
            .scripting({
                'heating_item': heating.item_ids.heating,
                'control_item': heating.item_ids.heatcontrol
            })\
            .append_to(self)

        Number(heating.item_ids.comforttemperature)\
            .label(_('Comfort temperature'))\
            .temperature()\
            .icon('temperature')\
            .equipment(heating)\
            .groups('HeatTemperature')\
            .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
            .scripting({
                'heating_item': heating.item_ids.heating,
                'control_item': heating.item_ids.heatcontrol
            })\
            .append_to(self)

        return heating_item

    def __build_subequipment(self, parent_heating: Heating, parent_heating_item: Group) -> bool:
        if parent_heating.has_subequipment:
            Group(parent_heating.item_ids.heatsetpoint)\
                .typed(GroupType.NUMBER_AVG)\
                .label(_('Target temperature'))\
                .format('%.1f °C')\
                .icon('heatsetpoint')\
                .equipment(parent_heating)\
                .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
                .append_to(self)

            subheatings = []

            for subheating in parent_heating.subequipment:
                subheatings.append(subheating.item_ids.heating)
                self.__build_thing(subheating, parent_heating_item)

            parent_heating_item.scripting({
                'is_thing': False,
                'subequipment': ','.join(subheatings)

            })

        return parent_heating.has_subequipment

    def __build_thing(self, heating: Heating, heating_item: Group) -> None:
        if heating.is_child:
            heating_item = Group(heating.item_ids.heating)\
                .label(_('Heating {name}').format(name=heating.name))\
                .icon('heating')\
                .equipment(heating.parent)\
                .semantic(heating)\
                .scripting({
                    'comfort_item': heating.parent.item_ids.comforttemperature,
                    'eco_item': heating.parent.item_ids.ecotemperature
                })\
                .append_to(self)

        heating_item.scripting({
            'is_thing': True,
            'setpoint_item': heating.item_ids.heatsetpoint,
            'heatmode_item': heating.item_ids.heatmode,
            'boost_temp': heating.boost_temp
        })

        heatsetpoint = Number(heating.item_ids.heatsetpoint)\
            .label(_('Target temperature'))\
            .temperature()\
            .icon('heating')\
            .equipment(heating)\
            .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
            .scripting({
                'boost_temp': heating.boost_temp
            })\
            .channel(heating.points.channel('heatsetpoint'))\
            .append_to(self)

        if heating.is_child:
            heatsetpoint.groups(heating.parent.item_ids.heatsetpoint)

        scripting = dict(
            map(lambda x: (f'heatmode_{x[0]}', x[1]), heating.heatmode.items()))

        String(heating.item_ids.heatmode)\
            .label(_('Heat mode'))\
            .equipment(heating)\
            .semantic(PointType.SETPOINT)\
            .scripting(scripting)\
            .channel(heating.points.channel('heatmode'))\
            .append_to(self)

        if heating.points.has_valveposition:
            Number(heating.item_ids.valveposition)\
                .percentage()\
                .label(_('Valve position'))\
                .equipment(heating)\
                .semantic(PointType.MEASUREMENT)\
                .channel(heating.points.channel('valveposition'))\
                .append_to(self)
