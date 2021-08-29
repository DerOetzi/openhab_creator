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

        Switch('wayhome')\
            .label(_('Way home'))\
            .icon('wayhome')\
            .config()\
            .expire('30m', 'OFF')\
            .append_to(self)

        Switch('overridePresence')\
            .label(_('Permanent presence'))\
            .config()\
            .groups('Presences')\
            .expire('24h', 'OFF')\
            .append_to(self)

        self.build_persons(configuration.persons)

        self.write_file('presences')

    def build_general_groups(self) -> None:
        Group('Presences')\
            .typed(GroupType.NUMBER_MAX)\
            .label(_('Presences'))\
            .map(MapTransformation.PRESENCE)\
            .icon('presence')\
            .append_to(self)

        Group('Distances')\
            .typed(GroupType.NUMBER_AVG)\
            .label(_('Distances'))\
            .format('f,.3f km')\
            .append_to(self)

    def build_persons(self, persons: List[Person]) -> None:
        for person in persons:
            if person.has_presence:
                Group(person.presence_id)\
                    .typed(GroupType.NUMBER_MAX)\
                    .label(_('Presence {person}').format(person=person.name))\
                    .map(MapTransformation.PRESENCE)\
                    .icon('presence')\
                    .groups('Presences')\
                    .append_to(self)

                for smartphone in list(filter(
                        lambda x: x.category == 'smartphone', person.equipment)):
                    Group(smartphone.item_ids.smartphone)\
                        .label(_('Smartphone {name}').format(name=smartphone.name))\
                        .semantic(smartphone)\
                        .append_to(self)

                    if smartphone.points.has_distance:
                        self.build_smartphone_geofence(smartphone)

    def build_smartphone_geofence(self, smartphone: Smartphone) -> None:
        Switch(smartphone.item_ids.geofence)\
            .label(_('Geofence'))\
            .map(MapTransformation.PRESENCE)\
            .icon('presence')\
            .semantic(PointType.STATUS)\
            .equipment(smartphone)\
            .groups(smartphone.person.presence_id)\
            .append_to(self)

        Number(smartphone.item_ids.distance)\
            .typed(NumberType.LENGTH)\
            .label(_('Distance'))\
            .format('%,.3f km')\
            .icon('distance')\
            .semantic(PointType.STATUS)\
            .equipment(smartphone)\
            .groups('Distances')\
            .channel(smartphone.points.channel('distance'))\
            .sensor('distance', {'typed': 'distance', **smartphone.influxdb_tags})\
            .scripting({
                'person': smartphone.person.name,
                'geofence': smartphone.item_ids.geofence
            })\
            .append_to(self)

        if smartphone.points.has_accuracy:
            Number(smartphone.item_ids.accuracy)\
                .typed(NumberType.LENGTH)\
                .label(_('Accuracy'))\
                .format('±%,d m')\
                .icon('accuracy')\
                .semantic(PointType.STATUS)\
                .equipment(smartphone)\
                .channel(smartphone.points.channel('accuracy'))\
                .sensor('distance', {'typed': 'accuracy', **smartphone.influxdb_tags})\
                .append_to(self)

        if smartphone.points.has_position:
            Location(smartphone.item_ids.position)\
                .label(_('Position'))\
                .icon('gps')\
                .semantic(PointType.STATUS)\
                .equipment(smartphone)\
                .channel(smartphone.points.channel('position'))\
                .append_to(self)

        if smartphone.points.has_lastseen:
            DateTime(smartphone.item_ids.lastseen)\
                .label(_('Last updated'))\
                .datetime()\
                .icon('update')\
                .semantic(PointType.STATUS, PropertyType.TIMESTAMP)\
                .equipment(smartphone)\
                .channel(smartphone.points.channel('lastseen'))\
                .append_to(self)
