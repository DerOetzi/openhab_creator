from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import Group, GroupType, Switch
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.person import Person
    from openhab_creator.models.configuration.equipment.types.smartphone import Smartphone


@ItemsCreatorPipeline(3)
class PresenceItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('Presences')\
            .typed(GroupType.NUMBER_MAX)\
            .label(_('Presences'))\
            .map(MapTransformation.PRESENCE)\
            .append_to(self)

        self.build_persons(configuration.persons)

        self.write_file('presences')

    def build_persons(self, persons: List[Person]) -> None:
        for person in persons:
            Group(f'presence{person.identifier}')\
                .typed(GroupType.NUMBER_MAX)\
                .label(_('Presence {person}').format(person=person.name))\
                .map(MapTransformation.PRESENCE)\
                .groups('Presences')\
                .append_to(self)

            for smartphone in list(filter(
                    lambda x: x.category == 'smartphone', person.equipment)):
                if smartphone.has_distance:
                    self.build_smartphone(smartphone)

    def build_smartphone(self, smartphone: Smartphone) -> None:
        Switch(smartphone.geofence_id)\
            .label(_('Geofence'))\
            .map(MapTransformation.PRESENCE)\
            .append_to(self)
