from __future__ import annotations

from typing import Dict, Final

from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)


@EquipmentType
class MotionDetector(Equipment):
    ITEM_IDENTIFIERS: Final[Dict[str, str]] = {
        'motiondetector': 'motionDetector',
        'presence': 'motionDetectorPresence',
        'assignment': 'motionDetectorAssignment'
    }
