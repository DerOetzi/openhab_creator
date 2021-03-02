from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation, Scenario
from openhab_creator.models.items import Group, Switch, PointType
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location import Location
    from openhab_creator.models.configuration.location.indoor.floors import Floor
    from openhab_creator.models.configuration.location.indoor import Indoor


@ItemsCreatorPipeline(2)
class LocationItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration):
        for floor in configuration.floors:
            self._create_floor(floor)
            for room in floor.rooms:
                self._create_room(room)

        self.write_file('locations')

    def _create_floor(self, floor: Floor) -> None:
        Group(floor.identifier)\
            .label(floor.name)\
            .icon(floor.category)\
            .semantic(floor)\
            .append_to(self)

    def _create_room(self, room: Indoor) -> None:
        Group(room.identifier)\
            .label(room.name)\
            .icon(room.category)\
            .groups(room.parent.identifier)\
            .semantic(room)\
            .append_to(self)

        self._create_automation(room)

    def _create_automation(self, location: Location) -> None:
        Switch(location.autoactive_id)\
            .label(_('Automation'))\
            .map(MapTransformation.ACTIVE)\
            .auto()\
            .location(location)\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Switch(location.autoguest_id)\
            .label(_('Guest stayed'))\
            .auto()\
            .location(location)\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        for scenario in Scenario:
            Switch(location.scenarioassignment_id(scenario))\
                .label(scenario.label)\
                .icon(f'scenario-{scenario.icon}')\
                .groups(scenario.assignment_id)\
                .location(location)\
                .semantic(PointType.SETPOINT)\
                .append_to(self)
