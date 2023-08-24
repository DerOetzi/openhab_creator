from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.configuration.equipment.types.car import \
    CarMapTransformations
from openhab_creator.models.items import (DateTime, Group, Number, NumberType,
                                          PointType, PropertyType, String,
                                          Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.car import Car


@ItemsCreatorPipeline(5)
class CarItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        for car in configuration.equipment.equipment('car'):
            self.build_car(car)

        self.write_file('cars')

    def build_car(self, car: Car):
        Group(car.item_ids.car)\
            .label(car.blankname)\
            .location(car.location)\
            .icon('car')\
            .semantic(car)\
            .append_to(self)

        self.build_status(car)
        self.build_climate(car)
        self.build_charger(car)

    def build_status(self, car: Car):
        if car.points.has_last_update:
            DateTime(car.item_ids.last_update)\
                .label(_('Last update'))\
                .datetime()\
                .icon('datetime')\
                .equipment(car)\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .channel(car.points.channel('lastUpdate'))\
                .append_to(self)

        if car.points.has_vehicle_locked:
            Switch(car.item_ids.vehicle_locked)\
                .label(_('Vehicle locked'))\
                .map(CarMapTransformations.VEHICLE_LOCKED)\
                .icon('lock')\
                .equipment(car)\
                .semantic(PointType.STATUS)\
                .channel(car.points.channel('vehicleLocked'))\
                .append_to(self)

        if car.points.has_doors_closed:
            Switch(car.item_ids.doors_closed)\
                .label(_('Doors'))\
                .map(CarMapTransformations.DOORS_CLOSED)\
                .icon('cardoor')\
                .equipment(car)\
                .semantic(PointType.STATUS, PropertyType.OPENING)\
                .channel(car.points.channel('doorsClosed'))\
                .append_to(self)

        if car.points.has_windows_closed:
            Switch(car.item_ids.windows_closed)\
                .label(_('Windows'))\
                .map(CarMapTransformations.WINDOWS_CLOSED)\
                .icon('carwindow')\
                .equipment(car)\
                .semantic(PointType.STATUS, PropertyType.OPENING)\
                .channel(car.points.channel('windowsClosed'))\
                .append_to(self)

    def build_climate(self, car: Car):
        if car.has_climater:
            Group(car.item_ids.climater)\
                .label(_('Climate'))\
                .icon('climate')\
                .equipment(car)\
                .semantic('HVAC')\
                .append_to(self)

            if car.points.has_climater_control:
                Switch(car.item_ids.climater_control)\
                    .label(_('Control'))\
                    .icon('climate')\
                    .equipment(car.item_ids.climater)\
                    .semantic(PointType.CONTROL)\
                    .channel(car.points.channel('climaterControl'))\
                    .append_to(self)

            if car.points.has_climater_target_temperature:
                Number(car.item_ids.climater_target_temperature)\
                    .typed(NumberType.TEMPERATURE)\
                    .label(_('Target temperature'))\
                    .format('%.1f %unit%')\
                    .icon('temperature')\
                    .equipment(car.item_ids.climater)\
                    .semantic(PointType.SETPOINT, PropertyType.TEMPERATURE)\
                    .channel(car.points.channel('climaterTargetTemperature'))\
                    .append_to(self)

            if car.points.has_climater_state:
                Switch(car.item_ids.climater_state)\
                    .label(_('State'))\
                    .icon('climaterstate')\
                    .equipment(car.item_ids.climater)\
                    .semantic(PointType.STATUS)\
                    .channel(car.points.channel('climaterState'))\
                    .append_to(self)

            if car.points.has_climater_remaining_time:
                Number(car.item_ids.climater_remaining_time)\
                    .typed(NumberType.TIME)\
                    .label(_('Remaining time'))\
                    .format('%d %unit%')\
                    .icon('time')\
                    .equipment(car.item_ids.climater)\
                    .semantic(PointType.STATUS, PropertyType.DURATION)\
                    .channel(car.points.channel('climaterRemainingTime'))\
                    .append_to(self)

            if car.points.has_climater_window_heating:
                Switch(car.item_ids.climater_window_heating)\
                    .label(_('Window heating'))\
                    .icon('windowheating')\
                    .equipment(car.item_ids.climater)\
                    .semantic(PointType.CONTROL)\
                    .channel(car.points.channel('climaterWindowHeating'))\
                    .append_to(self)

    def build_charger(self, car: Car):
        if car.points.has_charger_control:
            Switch(car.item_ids.charger_control)\
                .label(_('Charger control'))\
                .icon('charger')\
                .equipment(car)\
                .semantic(PointType.CONTROL)\
                .channel(car.points.channel('chargerControl'))\
                .append_to(self)
