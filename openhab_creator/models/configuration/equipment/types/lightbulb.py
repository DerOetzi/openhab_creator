from __future__ import annotations

from typing import Optional, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType()
class Lightbulb(Equipment):

    def __init__(self,
                 singlebulb: Optional[bool] = False,
                 nightmode: Optional[bool] = False,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self.singlebulb: bool = singlebulb
        self.nightmode: bool = nightmode

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'lightbulb': 'lightbulb',
            'lightcontrol': 'lightcontrol',
            'auto': 'autoLight',
            'autodisplay': 'autoDisplayLight',
            'autoreactivation': 'autoReactivationLight',
            'autodarkness': 'autoDarkness',
            'autoabsence': 'autoAbsenceLight',
            'motiondetectorperiod': 'motionDetectorPeriod',
            'switchingcycles': 'switchingCycles',
            'switchingcyclesreset': 'switchingCyclesReset',
            'hide': 'hideLight',
            'brightness': 'brightness',
            'colortemperature': 'colortemperatur',
            'onoff': 'onoff',
            'rgb': 'rgb',
            'nightmode': 'nightmode'
        }

    @property
    def conditional_points(self) -> List[str]:
        return ['brightness', 'colortemperature', 'onoff', 'rgb']

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('lightbulb')
        for point in self.conditional_points:
            if self.has_point_recursive(point):
                categories.append(point)

        return categories

    @property
    def is_timecontrolled(self) -> bool:
        return True

    @property
    def name_with_type(self) -> str:
        typed = _("Lightbulb")
        return f'{self.name} ({typed})'
