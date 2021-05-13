from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from openhab_creator import _
from openhab_creator.models.configuration import Configuration
from openhab_creator.models.sitemap import Page, Sitemap, Switch, Text
from openhab_creator.output.color import Color
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.sensor import \
        Sensor
    from openhab_creator.models.configuration.location import Location


@SitemapCreatorPipeline(mainpage=4)
class TemperatureSitemapCreator(BaseSitemapCreator):
    def __init__(self):
        self.toplevel_locations = {}
        self.locations = {}

    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('temperature')

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        sensors = list(filter(lambda x: x.location.area in ['Indoor', 'Building'],
                              configuration.equipment.equipment('temperature', False)))
        heatings = dict((x.location, x)
                        for x in configuration.equipment.equipment('heating'))

        if len(sensors) > 0:
            page = Page('temperatureIndoor')\
                .label(_('Temperatures'))\
                .valuecolor(*TemperatureSitemapCreator.valuecolor('temperatureIndoor'))\
                .append_to(sitemap)

            for sensor in sensors:
                subpage = self.subpage(page, sensor, heatings)

                if sensor.points.has_temperature:
                    Text(f'temperature{sensor.item_ids.sensor}')\
                        .label(sensor.name)\
                        .valuecolor(*TemperatureSitemapCreator
                                    .valuecolor(f'temperature{sensor.item_ids.sensor}'))\
                        .append_to(subpage)

            self._add_grafana(configuration.dashboard, page,
                              self.toplevel_locations.keys(), _('Temperatures') + ' ')

    def subpage(self, page: Page, sensor: Sensor, heatings: Dict) -> Page:
        location = sensor.location
        if location in self.locations:
            subpage = self.locations[location]
        else:
            toplevel_location = sensor.location.toplevel
            self.toplevel_locations[toplevel_location.identifier] = toplevel_location
            frame = page.frame(
                toplevel_location.identifier, toplevel_location.name)
            subpage = Page(f'temperature{location}')\
                .label(location.name)\
                .valuecolor(*TemperatureSitemapCreator.valuecolor(f'temperature{location}'))
            self.locations[location] = subpage
            self.build_heating(subpage, location, heatings)

            subpage.append_to(frame)

        return subpage

    def build_heating(self, page: Page, location: Location,  heatings: Dict) -> None:
        if location in heatings:
            heating = heatings[location]
            mappings = [
                ('"COMFORT"', _('Comfort')),
                ('"ECO"', _('ECO')),
                ('"CLOSED"', _('Closed'))
            ]

            page.labelcolor(
                (f'{heating.item_ids.heatcontrol}=="BOOST"', Color.RED),
                (f'{heating.item_ids.heatcontrol}=="COMFORT"', Color.YELLOW),
                (f'{heating.item_ids.heatcontrol}=="ECO"', Color.GREEN),
                (f'{heating.item_ids.heatcontrol}=="CLOSED"', Color.LIGHTGREY)
            )

            if heating.boost:
                mappings.insert(0, ('"BOOST"', _('Boost')))

            Switch(heating.item_ids.heatcontrol, mappings)\
                .append_to(page)

            Switch(heating.item_ids.auto, [('ON', _('Automation'))])\
                .visibility((heating.item_ids.auto, '!=', 'ON'))\
                .append_to(page)

            Text(heating.item_ids.heatsetpoint)\
                .valuecolor(*TemperatureSitemapCreator.valuecolor(heating.item_ids.heatsetpoint))\
                .visibility(
                    (heating.item_ids.heatcontrol, '==', 'COMFORT'),
                    (heating.item_ids.heatcontrol, '==', 'ECO'))\
                .append_to(page)

    @ staticmethod
    def valuecolor(item: str) -> List[Tuple[str, Color]]:
        return [
            (f'{item}>=28', Color.RED),
            (f'{item}>=24', Color.ORANGE),
            (f'{item}>=20', Color.YELLOW),
            (f'{item}>=16', Color.GREEN),
            (f'{item}>=8', Color.BLUE),
            (f'{item}>=0', Color.GREY)
        ]

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for temperatures"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for temperatures"""
