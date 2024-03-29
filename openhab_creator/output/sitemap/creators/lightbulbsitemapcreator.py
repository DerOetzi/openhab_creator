from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from openhab_creator import _
from openhab_creator.models.sitemap import (AutomationSwitch, Page, Selection,
                                            Setpoint, Sitemap, Slider, Switch,
                                            Text)
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

from openhab_creator.models.grafana import AggregateWindow, Period

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.lightbulb import \
        Lightbulb
    from openhab_creator.models.configuration.equipment.types.wallswitch import \
        WallSwitch


@SitemapCreatorPipeline(mainpage=40, statuspage=50, configpage=10)
class LightbulbSitemapCreator(BaseSitemapCreator):
    @classmethod
    def has_needed_equipment(cls, configuration: Configuration) -> bool:
        return configuration.equipment.has('lightbulb')

    def _build_mainpage_light(self, lightbulb, page):
        location = lightbulb.location.toplevel
        frame = page.frame(location.identifier, location.name)

        Switch(lightbulb.item_ids.lightcontrol, self._create_lightcontrol_mappings(
            lightbulb))\
            .label(lightbulb.name)\
            .visibility((lightbulb.item_ids.hide, '!=', 'ON'))\
            .append_to(frame)

        AutomationSwitch(lightbulb.item_ids.auto)\
            .visibility((lightbulb.item_ids.autodisplay, '==', 'ON'))\
            .append_to(frame)
        return frame

    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        page = Page(label=_('Lights'))\
            .icon('light')\
            .append_to(sitemap)

        for lightbulb in configuration.equipment.equipment('lightbulb'):
            self._build_mainpage_light(lightbulb, page)

    def _build_mainpage_light(self, lightbulb: Lightbulb, page: Page) -> None:
        location = lightbulb.location.toplevel
        frame = page.frame(location.identifier, location.name)

        Switch(lightbulb.item_ids.lightcontrol, self._create_lightcontrol_mappings(
            lightbulb))\
            .label(lightbulb.name)\
            .visibility((lightbulb.item_ids.hide, '!=', 'ON'))\
            .append_to(frame)

        AutomationSwitch(lightbulb.item_ids.auto)\
            .visibility((lightbulb.item_ids.autodisplay, '==', 'ON'))\
            .append_to(frame)

        Switch(lightbulb.item_ids.motiondetectorblocked, [('OFF', _('Unblock'))])\
            .label(lightbulb.name)\
            .visibility((lightbulb.item_ids.motiondetectorblocked, '==', 'ON'))\
            .append_to(frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        page = Page('SwitchingCycles')\
            .append_to(statuspage)

        locations = {}

        for lightbulb in configuration.equipment.equipment('lightbulb', False):
            location = lightbulb.location

            if lightbulb.is_thing and not lightbulb.has_subequipment:
                frame = page.frame(location.identifier, location.name)
                locations[location] = frame

                subpage = Page(lightbulb.item_ids.switchingcycles)\
                    .label(lightbulb.name)\
                    .append_to(frame)

                Text(lightbulb.item_ids.switchingcycles)\
                    .append_to(subpage)

                Switch(lightbulb.item_ids.switchingcyclesreset, [('ON', 'Reset')])\
                    .append_to(subpage)

        self._add_grafana_to_location_frames(configuration.dashboard,
                                             page,
                                             locations,
                                             _('Switching cycles') + ' ',
                                             {Period.DAY: AggregateWindow.HOUR,
                                                 Period.WEEK: AggregateWindow.DAY,
                                                 Period.MONTH: AggregateWindow.DAY,
                                                 Period.YEAR: AggregateWindow.MONTH})

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        page = Page(label=_('Lights'))\
            .icon('light')\
            .append_to(configpage)

        for lightbulb in configuration.equipment.equipment('lightbulb'):
            location = lightbulb.location.toplevel

            frame = page.frame(location.identifier, location.name)
            lightpage = Page(label=lightbulb.name)\
                .icon('configuration')\
                .append_to(frame)

            Switch(lightbulb.item_ids.lightcontrol, self._create_lightcontrol_mappings(
                lightbulb))\
                .append_to(lightpage)

            self.build_colortemperature(lightbulb, lightpage)

            Switch(lightbulb.item_ids.hide, [('OFF', _('Display')), ('ON', _('Hide'))])\
                .append_to(lightpage)

            AutomationSwitch(lightbulb.item_ids.auto, True)\
                .append_to(lightpage)

            Setpoint(lightbulb.item_ids.autoreactivation, 0, 240, 10)\
                .append_to(lightpage)

            Switch(lightbulb.item_ids.autoabsence, [
                   ('OFF', _('Off')), ('ON', _('On'))])\
                .append_to(lightpage)

            Switch(lightbulb.item_ids.autodarkness, [
                   ('OFF', _('Always')), ('ON', _('Only'))])\
                .append_to(lightpage)

            self._create_wallswitches_page(lightbulb, configuration, lightpage)

            self._create_motiondetector_page(
                lightbulb, configuration, lightpage)

            if lightbulb.nightmode:
                mappings = [('RANDOM', _('Random'))]
                for subequipment in lightbulb.subequipment:
                    mappings.append(
                        (subequipment.item_ids.lightbulb, subequipment.blankname))

                Selection(lightbulb.item_ids.nightmode, mappings)\
                    .append_to(lightpage)

    def build_colortemperature(self, lightbulb: Lightbulb, lightpage: Page) -> None:
        if lightbulb.points.has_colortemperature:
            if lightbulb.singlebulb:
                for subequipment in lightbulb.subequipment:
                    if subequipment.points.has_colortemperature:
                        Slider(subequipment.item_ids.colortemperature,
                               subequipment.min_colortemp,
                               subequipment.max_colortemp,
                               100)\
                            .label(_('Colortemperature {name}').format(name=subequipment.blankname))\
                            .append_to(lightpage)
            else:
                Slider(lightbulb.item_ids.colortemperature,
                       lightbulb.min_colortemp,
                       lightbulb.max_colortemp,
                       100)\
                    .append_to(lightpage)

    def _create_wallswitches_page(self,
                                  lightbulb: Lightbulb,
                                  configuration: Configuration,
                                  lightpage: Page) -> None:
        if configuration.equipment.has('wallswitch'):
            page = Page(label=_('Wallswitch assignments {lightbulb}').format(
                lightbulb=lightbulb.name))\
                .icon('configuration')\
                .append_to(lightpage)

            mappings = self._create_lightcontrol_mappings(lightbulb)
            mappings.insert(0, ('NULL', _('No assignment')))
            mappings.append(('UNBLOCK', _('Unblock')))
            mappings.append(('OFFUNBLOCK', _('Off & unblock')))
            mappings.append(('TRIGGERMOTION', _('Trigger motion')))

            for wallswitch in configuration.equipment.equipment('wallswitch'):
                self._create_wallswitch_page(
                    page, lightbulb, wallswitch, mappings)

    @staticmethod
    def _create_wallswitch_page(page: Page,
                                lightbulb: Lightbulb,
                                wallswitch: WallSwitch,
                                mappings: List[Tuple[str, str]]) -> None:
        location = wallswitch.location.toplevel
        frame = page.frame(location.identifier, location.name)

        subpage = Page(
            label=_('Assignment {wallswitch} to {lightbulb}').format(
                wallswitch=wallswitch.name, lightbulb=lightbulb.name))\
            .icon('configuration')\
            .append_to(frame)

        for button_key in range(0, wallswitch.buttons_count):
            Selection(wallswitch.item_ids.buttonassignment(
                button_key, lightbulb), mappings)\
                .append_to(subpage)

    @staticmethod
    def _create_lightcontrol_mappings(lightbulb: Lightbulb) -> List[Tuple[str, str]]:
        mappings = [
            ('"OFF"', _('Off'))
        ]

        if lightbulb.singlebulb:
            mappings.append(('"ALL"', _('All')))

            for subequipment in lightbulb.subequipment:
                mappings.append(
                    (f'"{subequipment.identifier}"', subequipment.blankname))
        else:
            mappings.append(('"ALL"', _('On')))

        if lightbulb.nightmode:
            mappings.append(('"NIGHT"', _('Night')))

        return mappings

    @staticmethod
    def _create_motiondetector_page(lightbulb: Lightbulb,
                                    configuration: Configuration,
                                    lightpage: Page) -> None:
        if configuration.equipment.has('motiondetector'):
            page = Page(lightbulb.item_ids.motiondetectors)\
                .append_to(lightpage)

            Setpoint(lightbulb.item_ids.motiondetectorperiod, 0, 300, 10)\
                .append_to(page)

            Switch(lightbulb.item_ids.motiondetectorblocked, [('OFF', _('Unblock'))])\
                .visibility((lightbulb.item_ids.motiondetectorblocked, '==', 'ON'))\
                .append_to(page)

            for motiondetector in configuration.equipment.equipment('motiondetector'):
                location = motiondetector.location.toplevel
                frame = page.frame(location.identifier, location.name)

                Switch(motiondetector.item_ids.assignment(lightbulb),
                       [('OFF', _('Off')), ('ON', _('On'))])\
                    .append_to(frame)
