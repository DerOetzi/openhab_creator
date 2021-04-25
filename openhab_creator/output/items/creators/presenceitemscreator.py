from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (DateTime, Group, GroupType, Location, Number,
                                          NumberType, PointType, PropertyType,
                                          Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.smartphone import \
        Smartphone
    from openhab_creator.models.configuration.person import Person


@ItemsCreatorPipeline(3)
class PresenceItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        self.build_general_groups()

        self.build_persons(configuration.persons)

        self.write_file('presences')

    def build_general_groups(self) -> None:
        Group('Presences')\
            .typed(GroupType.NUMBER_MAX)\
            .label(_('Presences'))\
            .map(MapTransformation.PRESENCE)\
            .append_to(self)

        Group('Distances')\
            .typed(GroupType.NUMBER_AVG)\
            .label(_('Distances'))\
            .format('f,.3f km')\
            .append_to(self)

    def build_persons(self, persons: List[Person]) -> None:
        for person in persons:
            Group(person.presence_id)\
                .typed(GroupType.NUMBER_MAX)\
                .label(_('Presence {person}').format(person=person.name))\
                .map(MapTransformation.PRESENCE)\
                .groups('Presences')\
                .append_to(self)

            for smartphone in list(filter(
                    lambda x: x.category == 'smartphone', person.equipment)):
                Group(smartphone.smartphone_id)\
                    .label(_('Smartphone {name}').format(name=smartphone.name))\
                    .semantic(smartphone)\
                    .append_to(self)

                if smartphone.has_distance:
                    self.build_smartphone_geofence(smartphone)

    def build_smartphone_geofence(self, smartphone: Smartphone) -> None:
        Switch(smartphone.geofence_id)\
            .label(_('Geofence'))\
            .map(MapTransformation.PRESENCE)\
            .semantic(PointType.STATUS)\
            .equipment(smartphone)\
            .groups(smartphone.person.presence_id)\
            .append_to(self)

        Number(smartphone.distance_id)\
            .typed(NumberType.LENGTH)\
            .label(_('Distance'))\
            .format('%,.3f km')\
            .semantic(PointType.STATUS)\
            .equipment(smartphone)\
            .groups('Distances')\
            .channel(smartphone.channel('distance'))\
            .sensor('distance', {'typed': 'distance', **smartphone.influxdb_tags})\
            .append_to(self)

        if smartphone.has_accuracy:
            Number(smartphone.accuracy_id)\
                .typed(NumberType.LENGTH)\
                .label(_('Accuracy'))\
                .format('%,d m')\
                .semantic(PointType.STATUS)\
                .equipment(smartphone)\
                .channel(smartphone.channel('accuracy'))\
                .sensor('distance', {'typed': 'accuracy', **smartphone.influxdb_tags})\
                .append_to(self)

        if smartphone.has_position:
            Location(smartphone.position_id)\
                .label(_('Position'))\
                .semantic(PointType.STATUS)\
                .equipment(smartphone)\
                .channel(smartphone.channel('position'))\
                .append_to(self)

        if smartphone.has_lastseen:
            DateTime(smartphone.lastseen_id)\
                .label(_('Last updated'))\
                .datetime()\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .equipment(smartphone)\
                .channel(smartphone.channel('lastseen'))\
                .append_to(self)
