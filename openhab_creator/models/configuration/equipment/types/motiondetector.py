from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import Lightbulb


@EquipmentType
class MotionDetector(Equipment):
    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'motiondetector': 'motionDetector',
            'presence': 'motionDetectorPresence'
        }

    def assignment_id(self, lightbulb: Optional[Lightbulb] = None) -> str:
        if lightbulb is None:
            return f'MotionDetectorAssignment{self.identifier}'
        else:
            return f'MotionDetectorAssignment{self.identifier}_{lightbulb.identifier}'

    @property
    def name_with_type(self) -> str:
        typed = _("Motiondetector")
        return f'{self.name} ({typed})'
