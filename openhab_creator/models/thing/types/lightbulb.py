from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from openhab_creator.exception import BuildException
from openhab_creator.models.thing.equipmenttype import EquipmentType
from openhab_creator.models.thing.equipment import Equipment


@EquipmentType('lightbulb')
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

        self.__singlebulb: bool = config.pop('singlebulb', False)
        self.__nightmode: bool = config.pop('nightmode', False)

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

    def has_rgb(self) -> bool:
        for subequipment in self.subequipment():
            if subequipment.has_rgb():
                return True

        return 'rgb' in self.points('controls')

    def is_singlebulb(self) -> bool:
        return self.__singlebulb or (self.has_parent() and self.parent().__singlebulb)

    def is_nightmode(self) -> bool:
        return self.__nightmode

    def lightbulb_id(self) -> str:
        return f'lightbulb{self._identifier}'

    def lightcontrol_id(self) -> str:
        return f'lightcontrol{self._identifier}'

    def nightmode_id(self) -> str:
        return f'nightmode{self._identifier}'

    def auto_id(self) -> str:
        return f'autoLight{self._identifier}'

    def autodisplay_id(self) -> str:
        return f'autoDisplayLight{self._identifier}'

    def autoreactivation_id(self) -> str:
        return f'autoReactivationLight{self._identifier}'

    def autoabsence_id(self) -> str:
        return f'autoAbscenceLight{self._identifier}'

    def hide_id(self) -> str:
        return f'hideLight{self._identifier}'

    def brightness_id(self) -> str:
        return f'brightness{self._identifier}'

    def colortemperature_id(self) -> str:
        return f'colortemperatuer{self._identifier}'

    def onoff_id(self) -> str:
        return f'onoff{self._identifier}'

    def rgb_id(self) -> str:
        return f'rgb{self._identifier}'

    def __str__(self) -> str:
        return f'{self._name} ({self._identifier}, {self.__singlebulb}, {self.__nightmode})'