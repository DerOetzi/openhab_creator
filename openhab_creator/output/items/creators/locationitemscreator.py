from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation, Scene
from openhab_creator.models.items import Group, PointType, String, Switch
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location import Location, Cars, Christmas, EnergyManagement
    from openhab_creator.models.configuration.location.indoor import Indoor
    from openhab_creator.models.configuration.location.indoor.floors import \
        Floor
    from openhab_creator.models.configuration.location.outdoors import Outdoor


@ItemsCreatorPipeline(2)
class LocationItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration):
        for floor in configuration.locations.floors:
            self._create_floor(floor)
            for room in floor.rooms:
                self._create_room(room)

        for building in configuration.locations.buildings:
            self._create_building(building)

        for christmas in configuration.locations.christmas:
            self._create_christmas(christmas)

        for cars in configuration.locations.cars:
            self._create_cars(cars)

        for energymanagement in configuration.locations.energymanagement:
            self._create_energymanagement(energymanagement)

        for outdoor in configuration.locations.outdoors:
            self._create_outdoor(outdoor)

        for location in configuration.locations.timecontrolled.values():
            self._create_automation(location)

        self.write_file('locations')

    def _create_floor(self, floor: Floor) -> None:
        Group(floor.identifier)\
            .label(floor.name)\
            .icon(floor.category)\
            .semantic(floor)\
            .scripting(floor.location_items)\
            .append_to(self)

    def _create_room(self, room: Indoor) -> None:
        Group(room.identifier)\
            .label(room.name)\
            .icon(room.category)\
            .groups(room.parent.identifier)\
            .semantic(room)\
            .scripting(room.location_items)\
            .append_to(self)

    def _create_building(self, building: Indoor) -> None:
        Group(building.identifier)\
            .label(building.name)\
            .icon(building.category)\
            .semantic(building)\
            .scripting(building.location_items)\
            .append_to(self)

    def _create_christmas(self, christmas: Christmas) -> None:
        Group(christmas.identifier)\
            .label(christmas.name)\
            .icon(christmas.category)\
            .semantic(christmas)\
            .scripting(christmas.location_items)\
            .append_to(self)

    def _create_cars(self, cars: Cars) -> None:
        Group(cars.identifier)\
            .label(cars.name)\
            .icon(cars.category)\
            .semantic(cars)\
            .scripting(cars.location_items)\
            .append_to(self)

    def _create_energymanagement(self, energymanagement: EnergyManagement) -> None:
        Group(energymanagement.identifier)\
            .label(energymanagement.name)\
            .icon(energymanagement.category)\
            .semantic(energymanagement)\
            .scripting(energymanagement.location_items)\
            .append_to(self)

    def _create_outdoor(self, outdoor: Outdoor) -> None:
        Group(outdoor.identifier)\
            .label(outdoor.name)\
            .icon(outdoor.category)\
            .semantic(outdoor)\
            .scripting(outdoor.location_items)\
            .append_to(self)

    def _create_automation(self, location: Location) -> None:
        Switch(location.autoactive_id)\
            .label(_('Automation'))\
            .map(MapTransformation.ACTIVE)\
            .auto()\
            .location(location)\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Group(location.autoequipment)\
            .append_to(self)

        for scene in Scene:
            String(location.sceneassignment_id(scene))\
                .label(scene.label)\
                .icon(f'scene{scene.icon}')\
                .groups(scene.assignment_id)\
                .location(location)\
                .semantic(PointType.SETPOINT)\
                .scripting({
                    'active_item': location.autoactive_id,
                    'equipment_group': location.autoequipment
                })\
                .append_to(self)
