from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from openhab_creator.exception import BuildException
from openhab_creator.models.thing.equipment.equipment import Equipment


class Lightbulb(Equipment):
    def __init__(self,
                 typed: str,
                 config: Optional[Dict[str, Union[str, bool]]] = None,
                 **equipment_args):
        if "lightbulb" != typed:
            raise BuildException(
                "Tried to parse not lightbulb Equipment to lightbulb")

        if config is None:
            config = {}

        self.__singlebulb = config.pop('singlebulb', False)
        self.__nightmode = config.pop('singlebulb', False)

        super().__init__(typed=typed, config=config, **equipment_args)

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
        return self.__singlebulb or (self.has_parent() and self.parent().__singlebulb)

    def is_nightmode(self) -> bool:
        return self.__nightmode

    def lightbulb_id(self):
        return f'lightbulb{self._identifier}'

    def lightcontrol_id(self):
        return f'lightcontrol{self._identifier}'

    def nightmode_id(self):
        return f'nightmode{self._identifier}'

    def brightness_id(self):
        return f'brightness{self._identifier}'

    def colortemperature_id(self):
        return f'colortemperatuer{self._identifier}'

    def onoff_id(self):
        return f'onoff{self._identifier}'