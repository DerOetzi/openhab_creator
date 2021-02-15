from __future__ import annotations

from typing import Dict

from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)


@EquipmentType
class MotionDetector(Equipment):
    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'motiondetector': 'motionDetector',
            'presence': 'motionDetectorPresence',
            'assignment': 'motionDetectorAssignment'
        }
