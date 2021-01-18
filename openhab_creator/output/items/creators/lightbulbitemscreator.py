from __future__ import annotations

from typing import List

from openhab_creator import _
from openhab_creator.exception import BuildException
from openhab_creator.models.configuration import SmarthomeConfiguration
from openhab_creator.models.thing.equipment import Equipment
from openhab_creator.models.thing.types.lightbulb import Lightbulb
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.output.items.itemscreatorregistry import ItemsCreatorRegistry


@ItemsCreatorRegistry(3)
class LightbulbItemsCreator(BaseItemsCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self._create_group(
            'Lightcontrol', _('Lightcontrol items'), groups=['Config'])

        self._create_group(
            'Nightmode', _('Nightmode configuration items'), groups=['Config'])

        self._create_group(
            'AutoLight', _('Scene controlled configuration items'), groups=['Auto']
        )

        self._create_group(
            'AutoReactivationLight', ('Reactivation scene controlled configuration items'), groups=['Config']
        )

        for lightbulb in configuration.equipment('lightbulb'):
            self.__build_parent(lightbulb)

        self._write_file('lightbulb')

    def __build_parent(self, lightbulb: Lightbulb) -> None:
        self._create_group(
            lightbulb.lightbulb_id(),
            _('Lightbulb {blankname}').format(blankname=lightbulb.blankname()),
            "light", [lightbulb.location().identifier()], ['Lightbulb']
        )

        self._create_item(
            'String',
            lightbulb.lightcontrol_id(),
            _('Lightcontrol'),
            'lightcontrol', [lightbulb.lightbulb_id(), 'Lightcontrol'],
            ['Control']
        )

        self._create_item(
            'Switch',
            lightbulb.hide_id(),
            _('Hide on lights page'),
            'hide', [lightbulb.lightbulb_id(), 'Config'],
            ['Control']
        )

        self._create_item(
            'Switch',
            lightbulb.auto_id(),
            _('Scene controlled'),
            'auto', [lightbulb.lightbulb_id(), 'AutoLight'],
            ['Control']
        )

        self._create_item(
            'Switch',
            lightbulb.autodisplay_id(),
            _('Display scene controlled'),
            groups=[lightbulb.lightbulb_id()],
            tags=['Status']
        )

        self._create_item(
            'Number',
            lightbulb.autoreactivation_id(),
            _('Reactivate scene controlled'),
            icon='reactivation',
            groups=[lightbulb.lightbulb_id(), 'AutoReactivationLight'],
            tags=['Setpoint']
        )

        if (lightbulb.is_nightmode()):
            self._create_item(
                'Number',
                lightbulb.nightmode_id(),
                _('Nightmode configuration'),
                'nightmode', [lightbulb.lightbulb_id(), 'Nightmode'],
                ['Setpoint']
            )

        if not self.__build_subequipment(lightbulb):
            self.__build_thing(lightbulb)

    def __build_subequipment(self, parent_lightbulb: Lightbulb) -> bool:
        if parent_lightbulb.has_subequipment():
            self.__build_parent_group(parent_lightbulb.has_brightness(),
                                      parent_lightbulb.brightness_id(),
                                      _('Brightness'), parent_lightbulb.lightbulb_id(),
                                      ['Control', 'Light'], 'dimmer_avg')

            self.__build_parent_group(parent_lightbulb.has_colortemperature(),
                                      parent_lightbulb.colortemperature_id(),
                                      _('Colortemperature'), parent_lightbulb.lightbulb_id(),
                                      ['Control', 'ColorTemperature'], 'number_avg')

            self.__build_parent_group(parent_lightbulb.has_onoff(),
                                      parent_lightbulb.onoff_id(),
                                      _('On/Off'), parent_lightbulb.lightbulb_id(),
                                      ['Switch', 'Light'], 'onoff')

            for sublightbulb in parent_lightbulb.subequipment():
                self.__build_thing(sublightbulb)

            return True

        return False

    def __build_parent_group(self,
                             create: bool,
                             group_id: str,
                             name: str,
                             lightbulb_id: str,
                             tags: List[str],
                             typed: str) -> None:
        if create:
            self._create_group(
                group_id, name,
                'light', [lightbulb_id],
                tags, typed
            )

    def __build_thing(self, lightbulb: Lightbulb) -> None:
        if lightbulb.has_parent():
            self._create_group(
                lightbulb.lightbulb_id(),
                _('Lightbulb {name}').format(name=lightbulb.name()), 'light',
                [lightbulb.parent().lightbulb_id()],
                ['Lightbulb']
            )

        self.__build_brightness_item(lightbulb)
        self.__build_colortemperature_item(lightbulb)
        self.__build_onoff_item(lightbulb)

    def __build_brightness_item(self, lightbulb: Lightbulb) -> None:
        if lightbulb.has_brightness():
            groups = []

            groups.append(lightbulb.lightbulb_id())

            if lightbulb.has_parent():
                groups.append(lightbulb.parent().brightness_id())

            self._create_item('Dimmer',
                              lightbulb.brightness_id(),
                              _('Brightness'), 'light', groups, [
                                  'Control', 'Light'],
                              {'channel': lightbulb.channel('controls', 'brightness')})

    def __build_colortemperature_item(self, lightbulb: Lightbulb) -> None:
        if lightbulb.has_colortemperature():
            groups = []

            groups.append(lightbulb.lightbulb_id())

            if lightbulb.has_parent():
                groups.append(lightbulb.parent().colortemperature_id())

            self._create_item('Number',
                              lightbulb.colortemperature_id(),
                              _('Colortemperature'), 'light', groups, [
                                  'Control', 'ColorTemperature'],
                              {'channel': lightbulb.channel('controls', 'colortemperature')})

    def __build_onoff_item(self, lightbulb: Lightbulb) -> None:
        if lightbulb.has_onoff():
            groups = []

            groups.append(lightbulb.lightbulb_id())

            if lightbulb.has_parent():
                groups.append(lightbulb.parent().onoff_id())

            self._create_item('Switch',
                              lightbulb.onoff_id(),
                              _('On/Off'), 'light', groups, [
                                  'Switch', 'Light'],
                              {'channel': lightbulb.channel('controls', 'onoff')})
