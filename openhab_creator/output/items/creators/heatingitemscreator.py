from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (Group, GroupType, Number, PointType,
                                          PropertyType, String, Switch)
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

        for heating in configuration.equipment('heating'):
            self.__build_parent(heating)

            if not self.__build_subequipment(heating):
                self.__build_thing(heating)

        self.write_file('heating')

    def __build_general_groups(self) -> None:
        Group('Heatcontrol')\
            .label(_('Heat control items'))\
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

    def __build_parent(self, heating: Heating) -> None:
        Group(heating.heating_id)\
            .label(_('Heating {blankname}').format(blankname=heating.blankname))\
            .icon('heating')\
            .location(heating.location)\
            .semantic(heating)\
            .append_to(self)

        String(heating.heatcontrol_id)\
            .label(_('Heatcontrol'))\
            .icon('heatcontrol')\
            .groups(heating.heating_id, 'Heatcontrol')\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(heating.auto_id)\
            .label(_('Scene controlled'))\
            .icon('auto')\
            .groups('AutoHeating', heating.heating_id)\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(heating.autodisplay_id)\
            .label(_('Display scene controlled'))\
            .groups(heating.heating_id)\
            .semantic(PointType.STATUS)\
            .append_to(self)

        Number(heating.autoreactivation_id)\
            .label(_('Reactivate scene controlled'))\
            .icon('reactivation')\
            .groups('AutoReactivationHeating', heating.heating_id)\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Number(heating.ecotemperature_id)\
            .label(_('ECO temperature'))\
            .temperature()\
            .icon('temperature')\
            .groups(heating.heating_id)\
            .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
            .auto()\
            .append_to(self)

        Number(heating.comforttemperature_id)\
            .label(_('Comfort temperature'))\
            .temperature()\
            .icon('temperature')\
            .groups(heating.heating_id)\
            .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
            .auto()\
            .append_to(self)

    def __build_subequipment(self, parent_heating: Heating) -> bool:
        if parent_heating.has_subequipment:
            Group(parent_heating.heatsetpoint_id)\
                .typed(GroupType.NUMBER_AVG)\
                .label(_('Target temperature'))\
                .icon('heating')\
                .groups(parent_heating.heating_id)\
                .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
                .append_to(self)

            for subheating in parent_heating.subequipment:
                self.__build_thing(subheating)

        return parent_heating.has_subequipment

    def __build_thing(self, heating: Heating) -> None:
        if heating.is_child:
            Group(heating.heating_id)\
                .label(_('Heating {name}').format(name=heating.name))\
                .icon('heating')\
                .groups(heating.parent.heating_id)\
                .semantic(heating)\
                .append_to(self)

        heatsetpoint = Number(heating.heatsetpoint_id)\
            .label(_('Target temperature'))\
            .temperature()\
            .icon('heating')\
            .groups(heating.heating_id)\
            .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
            .scripting({
                'off_temp': heating.off_temp,
                'boost_temp': heating.boost_temp
            })\
            .channel(heating.channel('heatsetpoint'))

        if heating.is_child:
            heatsetpoint.groups(heating.parent.heatsetpoint_id)

        heatsetpoint.append_to(self)
