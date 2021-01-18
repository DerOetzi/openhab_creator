from __future__ import annotations
from typing import Type

from openhab_creator.models.thing.equipment import Equipment


class EquipmentType(object):
    FACTORY_REGISTRY = {}

    def __init__(self, typed: str):
        self._typed = typed

    def __call__(self, cls: Type[Equipment]):
        EquipmentType.FACTORY_REGISTRY[self._typed] = cls
        return cls

    @staticmethod
    def new(**args) -> Type[Equipment]:
        typed = args['typed']
        if typed in EquipmentType.FACTORY_REGISTRY:
            return EquipmentType.FACTORY_REGISTRY[typed](**args)

        return Equipment(**args)
