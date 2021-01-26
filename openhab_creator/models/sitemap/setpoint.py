from __future__ import annotations
from typing import Dict

from openhab_creator.models.sitemap.baseelement import BaseElement


class Setpoint(BaseElement):
    def __init__(self, **args: Dict):
        self.__min_value = args.pop('min_value', 0)
        self.__max_value = args.pop('max_value', 1000)
        self.__step = args.pop('step', 1)

        super().__init__(**args)

    def dump(self) -> str:
        additional = {
            "minValue": self.__min_value,
            "maxValue": self.__max_value,
            "step": self.__step
        }

        return super().dump('Setpoint', additional)

    def append(self, element: BaseElement) -> None:
        return
