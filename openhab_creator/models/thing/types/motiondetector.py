from __future__ import annotations

from typing import Dict, List, Tuple, Union, Optional, TYPE_CHECKING

from openhab_creator import _
from openhab_creator.exception import BuildException
from openhab_creator.models.thing.equipment import Equipment
from openhab_creator.models.thing.equipmenttype import EquipmentType

if TYPE_CHECKING:
    from openhab_creator.models.thing.types.lightbulb import Lightbulb


@EquipmentType("motiondetector")
class MotionDetector(Equipment):
    def __init__(self,
                 typed: str,
                 config: Dict[str, Union[str, List['str']]],
                 **equipment_args: Dict):

        self._check_type(typed, 'motiondetector')
        super().__init__(typed=typed, config=config, **equipment_args)

    def motiondetector_id(self) -> str:
        return self.identifier('motionDetector')

    def presence_id(self) -> str:
        return self.identifier('motionDetectorPresence')

    def assignment_id(self, lightbulb: Optional[Lightbulb] = None) -> str:
        if lightbulb is None:
            return self.identifier('MotionDetectorAssignment')
        else:
            return f'MotionDetectorAssignment{self._identifier}_{lightbulb.identifier()}'

    def name_with_type(self):
        typed = _("Motiondetector")
        return f'{self._name} ({typed})'
