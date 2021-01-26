from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from openhab_creator import _
from openhab_creator.models.location.room import Room
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.models.sitemap.selection import Selection
from openhab_creator.models.sitemap.switch import Switch
from openhab_creator.models.sitemap.text import Text
from openhab_creator.models.sitemap.page import Page
from openhab_creator.models.sitemap.setpoint import Setpoint
from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator
from openhab_creator.output.sitemap.sitemapcreatorpipeline import SitemapCreatorPipeline

if TYPE_CHECKING:
    from openhab_creator.models.sitemap.baseelement import BaseElement
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.types.lightbulb import Lightbulb
    from openhab_creator.models.thing.types.wallswitch import WallSwitch
    from openhab_creator.models.thing.types.motiondetector import MotionDetector


@SitemapCreatorPipeline(mainpage=0, configpage=3, equipment_needed=['lightbulb'])
class LightbulbSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, configuration: SmarthomeConfiguration) -> Page:

        page = Page(label=_('Lights'), icon='light')

        for lightbulb in configuration.equipment('lightbulb'):
            location = lightbulb.toplevel_location()
            frame = page.frame(location.identifier(), location.name())

            frame.append(self._create_lightcontrol(lightbulb, True))
            frame.append(self._create_auto(lightbulb, False))

        return page

    def build_configpage(self, configuration: SmarthomeConfiguration) -> Page:
        page = Page(label=_('Lights'), icon='light')

        for lightbulb in configuration.equipment('lightbulb'):
            location = lightbulb.toplevel_location()
            frame = page.frame(location.identifier(), location.name())
            subpage = Page(label=lightbulb.name(), icon='configuration')
            frame.append(subpage)

            subpage.append(self._create_lightcontrol(lightbulb, False))
            subpage.append(self._create_hide(lightbulb))

            subpage.append(self._create_auto(lightbulb, True))
            subpage.append(self._create_autoreactivation(lightbulb))

            subpage.append(self._create_autoabsence(lightbulb))
            subpage.append(self._create_autodarkness(lightbulb))

            subpage.append(self._create_wallswitch_page(
                lightbulb, configuration.equipment('wallswitch')))

            subpage.append(self._create_motion_detector_page(
                lightbulb, configuration.equipment('motiondetector')))

            subpage.append(self._create_switching_cycles_page(lightbulb))

        return page

    def _create_lightcontrol(self, lightbulb: Lightbulb, mainpage: bool) -> Switch:
        config = {
            'item': lightbulb.lightcontrol_id(),
            'mappings': self._create_lightcontrol_mappings(lightbulb)
        }

        if mainpage:
            config['label'] = lightbulb.name()
            config['visibility'] = [(0, lightbulb.hide_id(), '!=', 'ON')]

        return Switch(**config)

    def _create_auto(self, lightbulb: Lightbulb, always: bool) -> Switch:
        config = {
            'item': lightbulb.auto_id(),
            'mappings': [
                (1, 'ON', _('Automation'))
            ]
        }

        if always:
            config['mappings'].append((0, 'OFF', _('Off')))
        else:
            config['visibility'] = [
                (0, lightbulb.autodisplay_id(), '==', 'ON')
            ]

        return Switch(**config)

    def _create_hide(self, lightbulb: Lightbulb) -> Switch:
        return Switch(
            item=lightbulb.hide_id(),
            mappings=[
                (0, 'OFF', _('Display')),
                (1, 'ON', _('Hide'))
            ]
        )

    def _create_autoreactivation(self, lightbulb: Lightbulb) -> Switch:
        return Switch(
            item=lightbulb.autoreactivation_id(),
            mappings=[
                (0, '0', _('Off')),
                (1, '30', '30 M'),
                (2, '60', '1 H')
            ]
        )

    def _create_autoabsence(self, lightbulb: Lightbulb) -> Switch:
        return Switch(
            item=lightbulb.autoabsence_id(),
            mappings=[
                (0, 'OFF', _('Off')),
                (1, 'ON', _('On'))
            ]
        )

    def _create_autodarkness(self, lightbulb: Lightbulb) -> Switch:
        return Switch(
            item=lightbulb.autodarkness_id(),
            mappings=[
                (0, 'OFF', _('Always')),
                (1, 'ON', _('Only'))
            ]
        )

    def _create_wallswitch_page(self, lightbulb: Lightbulb, wallswitches: List[WallSwitch]) -> Page:
        page = Page(label=_('Wallswitch assignments {lightbulb}').format(
            lightbulb=lightbulb.name()), icon='configuration')

        mappings = self._create_lightcontrol_mappings(lightbulb)
        mappings.append((0, 'NULL', _('No assignment')))

        for wallswitch in wallswitches:
            location = wallswitch.toplevel_location()
            frame = page.frame(location.identifier(), location.name())

            subpage = Page(
                label=_('Assignment {wallswitch} to {lightbulb}').format(
                    wallswitch=wallswitch.name(), lightbulb=lightbulb.name()),
                icon="configuration")
            frame.append(subpage)

            for button_key in range(0, wallswitch.buttons_count()):
                subpage.append(
                    Selection(item=wallswitch.buttonassignment_id(button_key, lightbulb), mappings=mappings))

        return page

    def _create_lightcontrol_mappings(self, lightbulb: Lightbulb) -> List[Tuple[int, str, str]]:
        mappings = [
            (1, '"OFF"', _('Off'))
        ]

        order = 3

        if lightbulb.is_singlebulb():
            mappings.append((2, '"ALL"', _('All')))

            for subequipment in lightbulb.subequipment():
                mappings.append(
                    (order, f'"{subequipment.identifier()}"', subequipment.blankname()))
                order += 1
        else:
            mappings.append((2, '"ALL"', _('On')))

        if lightbulb.is_nightmode():
            mappings.append((order, '"NIGHT"', _('Night')))

        return mappings

    def _create_motion_detector_page(self, lightbulb: Lightbulb, motiondetectors: List[MotionDetector]) -> Page:
        page = Page(label=_('Motiondetector {lightbulb}').format(
            lightbulb=lightbulb.name()), icon='motiondetector')

        page.append(Setpoint(item=lightbulb.motiondetectorperiod_id(),
                             step=10, min_value=10, max_value=300))

        for motiondetector in motiondetectors:
            location = motiondetector.toplevel_location()
            frame = page.frame(location.identifier(), location.name())

            frame.append(Switch(item=motiondetector.assignment_id(
                lightbulb), mappings=[(0, 'OFF', _('Off')), (1, 'ON', _('On'))]))

        return page

    def _create_switching_cycles_page(self, lightbulb: Lightbulb) -> BaseElement:
        if lightbulb.has_subequipment():
            element = Page(label=_('Switching cycles {name}').format(
                name=lightbulb.name()), icon='switchingcycles')

            for subequipment in lightbulb.subequipment():
                element.append(
                    self._create_switching_cycles_subpage(subequipment))
        else:
            element = self._create_switching_cycles_subpage(lightbulb)

        return element

    def _create_switching_cycles_subpage(self, lightbulb: Lightbulb) -> Page:
        subpage = Page(item=lightbulb.switchingcycles_id())
        subpage.append(
            Text(item=lightbulb.switchingcycles_id(), label=_('Switching cycles')))
        subpage.append(
            Switch(item=lightbulb.switchingcyclesreset_id(), mappings=[(0, 'ON', _('Reset'))]))

        return subpage
