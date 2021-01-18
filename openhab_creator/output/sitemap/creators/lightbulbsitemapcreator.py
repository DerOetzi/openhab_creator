from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.location.room import Room
from openhab_creator.models.sitemap.frame import Frame
from openhab_creator.models.sitemap.switch import Switch
from openhab_creator.models.sitemap.text import Text
from openhab_creator.output.sitemap.basesitemapcreator import BaseSitemapCreator
from openhab_creator.output.sitemap.sitemapcreatorregistry import SitemapCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.types.lightbulb import Lightbulb


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
            page.append(frame)

        return page

    def _create_lightcontrol(self, lightbulb: Lightbulb, mainpage: bool) -> Switch:
        config = {
            'item': lightbulb.lightcontrol_id(),
            'mappings': {
                'OFF': _('Off')
            }
        }

        if mainpage:
            config['label'] = lightbulb.name()
            config['visibility'] = [(0, lightbulb.hide_id(), '!=', 'ON')]

        if lightbulb.is_singlebulb():
            config['mappings']['ALL'] = _('All')
            for subequipment in lightbulb.subequipment():
                config['mappings'][f'{subequipment.identifier()}'] = subequipment.blankname(
                )
        else:
            config['mappings']['ALL'] = _('On')

        if lightbulb.is_nightmode():
            config['mappings']['NIGHT'] = _('Night')

        return Switch(**config)

    def _create_auto(self, lightbulb: Lightbulb, always: bool) -> Switch:
        config = {
            'item': lightbulb.auto_id(),
            'mappings': {
                'ON': _('Automation')
            }
        }

        if always:
            config['mappings']['OFF'] = _('Off')
        else:
            config['visibility'] = [
                (0, lightbulb.autodisplay_id(), '==', 'ON')
            ]

        return Switch(**config)

    def _create_hide(self, lightbulb: Lightbulb) -> Switch:
        return Switch(
            item=lightbulb.hide_id(),
            mappings={
                'OFF': _('Display'),
                'ON': _('Hide')
            }
        )

    def _create_autoreactivation(self, lightbulb: Lightbulb) -> Switch:
        return Switch(
            item=lightbulb.autoreactivation_id(),
            mappings={
                '0': _('OFF'),
                '30': '30 M',
                '60': '1 H'
            }
        )
