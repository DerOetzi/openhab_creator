from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from openhab_creator import _
from openhab_creator.models.common import Heatcontrol, MapTransformation
from openhab_creator.models.configuration import Configuration
from openhab_creator.models.sitemap import (AutomationSwitch, Page, Setpoint, Sitemap, Switch,
                                            Text)
from openhab_creator.output.color import Color
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.sensor import \
        Sensor
    from openhab_creator.models.configuration.equipment.types.window import \
        Window
    from openhab_creator.models.configuration.equipment.types.heating import Heating
    from openhab_creator.models.configuration.location import Location


@SitemapCreatorPipeline(mainpage=50, configpage=40)
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

        windows = dict((x.location, x)
                       for x in configuration.equipment.equipment('window'))

        if len(sensors) > 0:
            page = Page('temperatureIndoor')\
                .label(_('Temperatures'))\
                .valuecolor(*TemperatureSitemapCreator.valuecolor('temperatureIndoor'))\
                .append_to(sitemap)

            for sensor in sensors:
                subpage = self.subpage(page, sensor, heatings, windows)

                if sensor.points.has('temperature'):
                    Text(f'temperature{sensor.item_ids.merged_sensor}')\
                        .label(sensor.name)\
                        .valuecolor(*TemperatureSitemapCreator
                                    .valuecolor(f'temperature{sensor.item_ids.merged_sensor}'))\
                        .append_to(subpage)

            self._add_grafana(configuration.dashboard, page,
                              self.toplevel_locations.keys(), _('Temperatures') + ' ')

    def subpage(self, page: Page, sensor: Sensor, heatings: Dict, windows: Dict) -> Page:
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
            self.build_window(subpage, location, windows)

            subpage.append_to(frame)

        return subpage

    @staticmethod
    def build_heating(page: Page, location: Location,  heatings: Dict) -> None:
        if location in heatings:
            heating = heatings[location]
            mappings = Heatcontrol.switch_mappings(heating.boost)

            page.labelcolor(*Heatcontrol.colors(heating.item_ids.heatcontrol))

            Switch(heating.item_ids.heatcontrol, mappings)\
                .visibility((heating.item_ids.hide, '!=', 'ON'))\
                .append_to(page)

            AutomationSwitch(heating.item_ids.auto)\
                .visibility((heating.item_ids.autodisplay, '==', 'ON'))\
                .append_to(page)

            Text(heating.item_ids.heatsetpoint)\
                .valuecolor(*TemperatureSitemapCreator.valuecolor(heating.item_ids.heatsetpoint))\
                .visibility(
                    (heating.item_ids.heatcontrol, '==', 'COMFORT'),
                    (heating.item_ids.heatcontrol, '==', 'ECO'))\
                .append_to(page)

    @staticmethod
    def build_window(page: Page, location: Location,  windows: Dict) -> None:
        if location in windows:
            window = windows[location]
            Text(window.item_ids.windowopen)\
                .append_to(page)

    @staticmethod
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
        """No statuspage for scene items"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        has_heating, heatings = configuration.equipment.has('heating')
        has_warmwaterpump, warmwaterpumps = configuration.equipment.has(
            'warmwaterpump')

        windows_location = self.get_windows(configuration)

        if has_heating or has_warmwaterpump:
            page = Page('heating')\
                .label(_('Heatings'))\
                .map(MapTransformation.ACTIVE)\
                .valuecolor(('==OFF', Color.RED), ('==ON', Color.GREEN))\
                .append_to(configpage)

            self.build_heating_main(configuration, page)

            self.build_pumps(warmwaterpumps, page)

            for heating in heatings:
                toplevel_location = heating.location.toplevel
                frame = page.frame(
                    toplevel_location.identifier, toplevel_location.name)

                colors = Heatcontrol.colors(heating.item_ids.heatcontrol)

                subpage = Page(heating.item_ids.heatcontrol)\
                    .label(heating.name)\
                    .map(MapTransformation.HEATCONTROL)\
                    .valuecolor(*colors)\
                    .append_to(frame)

                Switch(heating.item_ids.heatcontrol, Heatcontrol.switch_mappings(heating.boost))\
                    .labelcolor(*colors)\
                    .append_to(subpage)

                Switch(heating.item_ids.hide, [('OFF', _('Display')), ('ON', _('Hide'))])\
                    .append_to(subpage)

                Text(heating.item_ids.heatsetpoint)\
                    .valuecolor(*TemperatureSitemapCreator.valuecolor(heating.item_ids.heatsetpoint))\
                    .append_to(subpage)

                AutomationSwitch(heating.item_ids.auto, True)\
                    .append_to(subpage)

                Setpoint(heating.item_ids.autoreactivation, 0, 240, 10)\
                    .append_to(subpage)

                Switch(heating.item_ids.autoabsence, [
                    ('OFF', _('Off')), ('ON', _('On'))])\
                    .append_to(subpage)

                Setpoint(heating.item_ids.ecotemperature, 16, 20, 0.5)\
                    .append_to(subpage)

                Setpoint(heating.item_ids.comforttemperature, 20, 24, 0.5)\
                    .append_to(subpage)

                self.build_window_remindertime(
                    heating, windows_location, subpage)

    def get_windows(self, configuration: Configuration) -> Dict[Location, Window]:
        has_windows, windows = configuration.equipment.has('window')
        windows_location = {}
        if has_windows:
            windows_location = dict((x.location, x) for x in windows)
        return windows_location

    def build_heating_main(self, configuration: Configuration, page: Page) -> None:
        if configuration.general.has_learninghouse('heating'):
            Text('heating')\
                .valuecolor(('==OFF', Color.RED), ('==ON', Color.GREEN))\
                .append_to(page)
        else:
            Switch('heating', [
                ('OFF', _('Inactive')), ('ON', _('Active'))])\
                .labelcolor(('==OFF', Color.RED), ('==ON', Color.GREEN))\
                .append_to(page)

    def build_pumps(self, warmwaterpumps, page: Page) -> None:
        for pump in warmwaterpumps:
            frame = page.frame(pump.identifier, pump.blankname)
            Switch(pump.item_ids.onoff, [('OFF', _('Off')), ('ON', _('On'))])\
                .append_to(frame)

            AutomationSwitch(pump.item_ids.auto, True)\
                .append_to(frame)

            Setpoint(pump.item_ids.autoreactivation, 0, 240, 10)\
                .append_to(frame)

            Switch(pump.item_ids.autoabsence, [
                   ('OFF', _('Off')), ('ON', _('On'))])\
                .append_to(frame)

    def build_window_remindertime(self,
                                  heating: Heating,
                                  windows_location: Dict[Location, Window],
                                  subpage: Page) -> None:
        if heating.location in windows_location:
            window = windows_location[heating.location]

            if window.remindertime:
                Setpoint(window.item_ids.remindertime, 0, 15)\
                    .append_to(subpage)
