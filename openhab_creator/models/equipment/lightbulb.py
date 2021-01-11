from __future__ import annotations
from typing import TYPE_CHECKING

from openhab_creator.exception import BuildException

from openhab_creator.models.equipment import Equipment


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
