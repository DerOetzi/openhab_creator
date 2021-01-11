from __future__ import annotations
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from openhab_creator.models.thing.bridge import Bridge


class BridgeManager(object):
    __registry: Dict[str, Bridge]

    def __init__(self):
        self.__registry = {}

    def register(self, bridge_key: str, bridge: Bridge) -> None:
        self.__registry[bridge_key] = bridge

    def all(self) -> Dict[str, Bridge]:
        return self.__registry

    def get(self, bridge_key: str) -> Bridge:
        return self.__registry[bridge_key]
