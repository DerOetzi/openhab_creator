from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType, EquipmentItemIdentifiers)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import Lightbulb


class MotionDetectorItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.motiondetector

    @property
    def motiondetector(self) -> str:
        return self._identifier('motionDetector')

    @property
    def presence(self) -> str:
        return self._identifier('presence')

    def assignment(self, lightbulb: Optional[Lightbulb] = None) -> str:
        assignment = self._identifier('MotionDetectorAssignment')
        if lightbulb is not None:
            assignment += f'_{lightbulb.identifier}'

        return assignment


@EquipmentType()
class MotionDetector(Equipment):
    def __init__(self, **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: MotionDetectorItemIdentifiers = MotionDetectorItemIdentifiers(
            self)

    @property
    def item_ids(self) -> MotionDetectorItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('motiondetector')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Motiondetector")
        return f'{self.name} ({typed})'
