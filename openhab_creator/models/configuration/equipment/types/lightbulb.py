from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.exception import ConfigurationException
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class LightbulbItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.lightbulb

    @property
    def lightbulb(self) -> str:
        return self._identifier('lightbulb')

    @property
    def lightcontrol(self) -> str:
        return self._identifier('lightcontrol')

    @property
    def auto(self) -> str:
        return self._identifier('autoLight')

    @property
    def autodisplay(self) -> str:
        return self._identifier('autoDisplayLight')

    @property
    def autoreactivation(self) -> str:
        return self._identifier('autoReactivationLight')

    @property
    def autodarkness(self) -> str:
        return self._identifier('autoDarkness')

    @property
    def autoabsence(self) -> str:
        return self._identifier('autoAbsenceLight')

    @property
    def motiondetectors(self) -> str:
        return self._identifier('motiondetectors')

    @property
    def motiondetectorperiod(self) -> str:
        return self._identifier('motionDetectorPeriod')

    @property
    def motiondetectorblocked(self) -> str:
        return self._identifier('motionDetectorBlocked')

    @property
    def switchingcycles(self) -> str:
        return self._identifier('switchingCycles')

    @property
    def switchingcyclesreset(self) -> str:
        return self._identifier('switchingCyclesReset')

    @property
    def hide(self) -> str:
        return self._identifier('hideLight')

    @property
    def brightness(self) -> str:
        return self._identifier('brightness')

    @property
    def brightnessgroup(self) -> str:
        return self._identifier('brightnessgroup')

    @property
    def colortemperature(self) -> str:
        return self._identifier('colortemperature')

    @property
    def onoff(self) -> str:
        return self._identifier('onoff')

    @property
    def rgb(self) -> str:
        return self._identifier('rgb')

    @property
    def nightmode(self) -> str:
        return self._identifier('nightmode')


class LightbulbPoints(EquipmentPoints):
    @property
    def has_brightness(self) -> bool:
        return self.has('brightness', True)

    @property
    def has_colortemperature(self) -> bool:
        return self.has('colortemperature', True)

    @property
    def has_onoff(self) -> bool:
        return self.has('onoff', True)

    @property
    def has_rgb(self) -> bool:
        return self.has('rgb', True)


@EquipmentType()
class Lightbulb(Equipment):

    def __init__(self,
                 singlebulb: Optional[bool] = False,
                 nightmode: Optional[bool] = False,
                 min_colortemp: Optional[int] = None,
                 max_colortemp: Optional[int] = None,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self._item_ids: LightbulbItemIdentifiers = LightbulbItemIdentifiers(
            self)
        self._points = LightbulbPoints(points or {}, self)

        self.singlebulb: bool = singlebulb
        self.nightmode: bool = nightmode

        if (self.is_child or not self.has_subequipment) and self.points.has_colortemperature:
            if not min_colortemp:
                raise ConfigurationException(
                    'Colortemperature lightbulb needs a minimum value', self.name)

            if not max_colortemp:
                raise ConfigurationException(
                    'Colortemperature lightbulb needs a maximum value', self.name)

        self._min_colortemp: Optional[int] = min_colortemp
        self._max_colortemp: Optional[int] = max_colortemp

    @property
    def item_ids(self) -> LightbulbItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> LightbulbPoints:
        return self._points

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('lightbulb')

        if self.points.has_brightness:
            categories.append('brightness')

        if self.points.has_colortemperature:
            categories.append('colortemperature')

        if self.points.has_onoff:
            categories.append('onoff')

        if self.points.has_rgb:
            categories.append('rgb')

        return categories

    @property
    def min_colortemp(self) -> Union[int | None]:
        min_colortemp = self._min_colortemp
        for subequipment in self.subequipment:
            if not min_colortemp:
                min_colortemp = 0

            min_colortemp = max(
                min_colortemp, subequipment.min_colortemp)

        return min_colortemp

    @property
    def max_colortemp(self) -> Union[int | None]:
        max_colortemp = self._max_colortemp
        for subequipment in self.subequipment:
            if not max_colortemp:
                max_colortemp = 99999

            max_colortemp = min(
                max_colortemp, subequipment.max_colortemp)

        return max_colortemp

    @property
    def is_timecontrolled(self) -> bool:
        return True

    @property
    def name_with_type(self) -> str:
        typed = _("Lightbulb")
        return f'{self.name} ({typed})'
