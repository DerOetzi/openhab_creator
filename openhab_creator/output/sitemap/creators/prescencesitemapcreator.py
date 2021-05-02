from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.configuration.equipment.types.smartphone import \
    Smartphone
from openhab_creator.models.sitemap import Mapview, Page, Sitemap, Text, Switch
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.person import Person
    from openhab_creator.models.grafana import Dashboard


@SitemapCreatorPipeline(statuspage=0)
class PresenceSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        """No mainpage for presence"""

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        page = Page('Presences')\
            .append_to(statuspage)

        for person in configuration.persons:
            self.build_person(page, person)

        Switch('wayhome', {
            ('OFF', _('Away')),
            ('ON', _('On the way'))
        })\
            .visibility(
                ('Presences', '==', '0'),
                ('wayhome', '==', 'ON')
        )\
            .append_to(page)

    def build_person(self, page: Page, person: Person) -> None:
        if person.has_presence:
            subpage = Page(person.presence_id)\
                .append_to(page)

            for equipment in person.equipment:
                if isinstance(equipment, Smartphone):
                    self.build_smartphone(subpage, equipment)

    def build_smartphone(self, personpage: Page, smartphone: Smartphone) -> None:
        if smartphone.points.has_mac:
            Text(smartphone.item_ids.maconline)\
                .append_to(personpage)

        if smartphone.points.has_distance:
            Text(smartphone.item_ids.geofence)\
                .append_to(personpage)

            Text(smartphone.item_ids.position)\
                .append_to(personpage)

            Text(smartphone.item_ids.accuracy)\
                .append_to(personpage)

            Text(smartphone.item_ids.distance)\
                .append_to(personpage)

            Text(smartphone.item_ids.lastseen)\
                .append_to(personpage)

            Mapview(smartphone.item_ids.position, 10)\
                .append_to(personpage)

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for batteries"""
