from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from openhab_creator import _
from openhab_creator.models.location.room import Room
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.models.sitemap.selection import Selection
from openhab_creator.models.sitemap.switch import Switch
from openhab_creator.models.sitemap.text import Text
from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator
from openhab_creator.output.sitemap.sitemapcreatorregistry import SitemapCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.types.lightbulb import Lightbulb
    from openhab_creator.models.thing.types.wallswitch import WallSwitch


@SitemapCreatorRegistry(mainpage=0, configpage=3)
class LightbulbSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, configuration: SmarthomeConfiguration) -> Text:
        frames = {}

        page = Text(label=_('Lights'), icon='light')

        for lightbulb in configuration.equipment('lightbulb'):
            location = lightbulb.location()

            if isinstance(location, Room):
                location = location.floor()

            if location.identifier() in frames:
                frame = frames[location.identifier()]
            else:
                frame = Frame(location.name())
                frames[location.identifier()] = frame
                page.append(frame)

            frame.append(self._create_lightcontrol(lightbulb, True))
            frame.append(self._create_auto(lightbulb, False))

        return page

    def build_configpage(self, configuration: SmarthomeConfiguration) -> Text:
        page = Text(label=_('Lights'), icon='light')

        for lightbulb in configuration.equipment('lightbulb'):
            frame = Frame(lightbulb.name())

            frame.append(self._create_lightcontrol(lightbulb, False))
            frame.append(self._create_hide(lightbulb))

            frame.append(self._create_auto(lightbulb, True))
            frame.append(self._create_autoreactivation(lightbulb))

            frame.append(self._create_autoabsence(lightbulb))
            frame.append(self._create_autodarkness(lightbulb))

            frame.append(self._create_wallswitch_page(
                lightbulb, configuration.equipment('wallswitch')))

            page.append(frame)

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

    def _create_wallswitch_page(self, lightbulb: Lightbulb, wallswitches: List[WallSwitch]) -> Text:
        page = Text(label=_('Wallswitch assignments {lightbulb}').format(
            lightbulb=lightbulb.name()), icon='config')

        mappings = self._create_lightcontrol_mappings(lightbulb)
        mappings.append((0, 'NULL', _('No assignment')))

        for wallswitch in wallswitches:
            subpage = Text(
                label=_('Assignment {wallswitch} to {lightbulb}').format(
                    wallswitch=wallswitch.name(), lightbulb=lightbulb.name()),
                icon="config")
            page.append(subpage)

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
