from __future__ import annotations
from typing import List

from openhab_creator.exception import BuildException
from openhab_creator.models.equipment import Equipment

from openhab_creator.output.itemcreator import ItemCreator, Grouptypes


class Lightbulb(Equipment):
    def __init__(self, equipment: Equipment):
        if "lightbulb" != equipment.typed():
            raise BuildException(
                "Tried to parse not lightbulb Equipment to lightbulb")

        self._cast(equipment, Lightbulb)

    def has_brightness(self) -> bool:
        for subequipment in self.subequipment():
            if subequipment.has_brightness():
                return True

        return 'brightness' in self.points('controls')

    def has_colortemperature(self) -> bool:
        for subequipment in self.subequipment():
            if subequipment.has_colortemperature():
                return True

        return 'colortemperature' in self.points('controls')

    def has_onoff(self) -> bool:
        for subequipment in self.subequipment():
            if subequipment.has_onoff():
                return True

        return 'onoff' in self.points('controls')

    def is_singlebulb(self) -> bool:
        return self._configuration.get('singlebulb', False) or (self.has_parent() and self.parent()._configuration.get('singlebulb', False))

    def is_nightmode(self) -> bool:
        return self._configuration.get('nightmode', False)

    def lightbulb_id(self):
        return f'lightbulb{self._id}'

    def lightcontrol_id(self):
        return f'lightcontrol{self._id}'

    def nightmode_id(self):
        return f'nightmode{self._id}'

    def brightness_id(self):
        return f'brightness{self._id}'

    def colortemperature_id(self):
        return f'colortemperatuer{self._id}'

    def onoff_id(self):
        return f'onoff{self._id}'


class LightbulbCreator(ItemCreator):
    def build(self, lightbulbs: List[Equipment]) -> None:
        self._create_group(
            'Lightcontrol', 'Lightcontrol items', groups=['Config'])

        self._create_group(
            'Nightmode', 'Nightmode configuration items', groups=['Config'])

        for lightbulb in [Lightbulb(e) for e in lightbulbs]:
            self.__build_parent(lightbulb)

        self._write_file('lightbulb')

    def __build_parent(self, lightbulb: Lightbulb) -> None:
        self._create_group(
            lightbulb.lightbulb_id(),
            f'Lightbulb {lightbulb.blankname()}',
            "light", [lightbulb.location().id()], ['Lightbulb']
        )

        self._create_item(
            'Number',
            lightbulb.lightcontrol_id(),
            'Control',
            'lightcontrol', [lightbulb.lightbulb_id(), 'Lightcontrol'],
            ['Setpoint']
        )

        if (lightbulb.is_nightmode()):
            self._create_item(
                'Number',
                lightbulb.nightmode_id(),
                'Nightmode configuration',
                'nightmode', [lightbulb.lightbulb_id(), 'Nightmode'],
                ['Setpoint']
            )

        if not self.__build_subequipment(lightbulb):
            self.__build_thing(lightbulb)

    def __build_subequipment(self, parent_lightbulb: Lightbulb) -> bool:
        if parent_lightbulb.has_subequipment():
            self.__build_parent_group(parent_lightbulb.has_brightness(),
                                      parent_lightbulb.brightness_id(),
                                      'Brightness', parent_lightbulb.lightbulb_id(), ['Control', 'Light'], 'dimmer_avg')

            self.__build_parent_group(parent_lightbulb.has_colortemperature(),
                                      parent_lightbulb.colortemperature_id(),
                                      'Colortemperature', parent_lightbulb.lightbulb_id(), ['Control', 'ColorTemperature'], 'number_avg')

            self.__build_parent_group(parent_lightbulb.has_onoff(),
                                      parent_lightbulb.onoff_id(),
                                      'On/Off', parent_lightbulb.lightbulb_id(), ['Switch', 'Light'], 'onoff')

            for sublightbulb in parent_lightbulb.subequipment():
                self.__build_thing(sublightbulb)

            return True

        return False

    def __build_parent_group(self, create: bool, group_id: str, name: str, lightbulb_id: str, tags: List[str], typed: Grouptypes) -> None:
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
                f'Lightbulb {lightbulb.name()}', 'light',
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
                              'Brightness', 'light', groups, ['Control', 'Light'],
                              {'channel': lightbulb.channel('controls', 'brightness')})

    def __build_colortemperature_item(self, lightbulb: Lightbulb) -> None:
        if lightbulb.has_colortemperature():
            groups = []

            groups.append(lightbulb.lightbulb_id())

            if lightbulb.has_parent():
                groups.append(lightbulb.parent().colortemperature_id())

            self._create_item('Number',
                              lightbulb.colortemperature_id(),
                              'Colortemperature', 'light', groups, ['Control', 'ColorTemperature'],
                              {'channel': lightbulb.channel('controls', 'colortemperature')})

    def __build_onoff_item(self, lightbulb: Lightbulb) -> None:
        if lightbulb.has_onoff():
            groups = []

            groups.append(lightbulb.lightbulb_id())

            if lightbulb.has_parent():
                groups.append(lightbulb.parent().onoff_id())

            self._create_item('Switch',
                              lightbulb.onoff_id(),
                              'On/Off', 'light', groups, ['Switch', 'Light'],
                              {'channel': lightbulb.channel('controls', 'onoff')})
