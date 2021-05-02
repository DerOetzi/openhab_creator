from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
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
    def motiondetectorperiod(self) -> str:
        return self._identifier('motionDetectorPeriod')

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
    def has_brightness(self) -> str:
        return self.has('brightness', True)

    @property
    def has_colortemperature(self) -> str:
        return self.has('colortemperature', True)

    @property
    def has_onoff(self) -> str:
        return self.has('onoff', True)

    @property
    def has_rgb(self) -> str:
        return self.has('rgb', True)


@EquipmentType()
class Lightbulb(Equipment):

    def __init__(self,
                 singlebulb: Optional[bool] = False,
                 nightmode: Optional[bool] = False,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self._item_ids: LightbulbItemIdentifiers = LightbulbItemIdentifiers(
            self)
        self._points = LightbulbPoints(points or {}, self)

        self.singlebulb: bool = singlebulb
        self.nightmode: bool = nightmode

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
    def is_timecontrolled(self) -> bool:
        return True

    @property
    def name_with_type(self) -> str:
        typed = _("Lightbulb")
        return f'{self.name} ({typed})'
