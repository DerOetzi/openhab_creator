from __future__ import annotations
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from openhab_creator.models.bridge import Bridge

class BridgeManager(object):
    __registry: Dict[str, Bridge] = {}

    def register(self, bridgeKey: str, bridge: Bridge):
        self.__registry[bridgeKey] = bridge

    def all(self):
        return self.__registry

    def get(self, bridgeKey: str):
        return self.__registry[bridgeKey]

