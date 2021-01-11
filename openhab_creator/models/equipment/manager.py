from __future__ import annotations
from typing import Dict, List

from openhab_creator.models.equipment import Equipment
from openhab_creator.models.equipment.lightbulb import Lightbulb
from openhab_creator.models.equipment.sensor import Sensor


class EquipmentManager(object):
    TYPE_CASTS = {
        'lightbulb': Lightbulb,
        'sensor': Sensor
    }

    def __init__(self):
        self.__registry: Dict[str, List[Equipment]] = {}

    def register(self, equipment: Equipment) -> None:
        typed = equipment.typed()
        if typed not in self.__registry:
            self.__registry[typed] = []

        new_obj = EquipmentManager.TYPE_CASTS[typed](equipment)

        self.__registry[typed].append(new_obj)

    def all(self) -> Dict[str, List[Equipment]]:
        return self.__registry

    def lightbulbs(self) -> List[Lightbulb]:
        return self.__registry['lightbulb']
