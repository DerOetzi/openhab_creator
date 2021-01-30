from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment
    from openhab_creator.models.configuration.equipment.bridge import Bridge


class Thing(object):
    def __init__(self,
                 equipment_node: Equipment,
                 thingtype: str,
                 thinguid: Optional[str] = None,
                 configuration: Optional[Configuration] = None,
                 secrets_config: Optional[List[str]] = None,
                 nameprefix: Optional[str] = '',
                 properties: Optional[Dict[str, Any]] = None,
                 channels: Optional[Dict[str, Any]] = None,
                 bridge: Optional[str] = None):

        self.__EQUIPMENT_NODE: Final[Equipment] = equipment_node

        self.__THINGTYPE: Final[str] = thingtype
        self.__THINGUID: Final[str] = equipment_node.identifier if thinguid is None else self.replace_secrets(
            thinguid)
        self.__NAMEPREFIX: Final[str] = nameprefix

        self.__init_bridge(bridge)

    def __init_bridge(self,
                      configuration: Optional[Configuration] = None,
                      bridge_key: Optional[str] = None) -> None:

        if configuration is None or bridge_key is None:
            self.__BRIDGE: Final[Bridge] = None
            return

        self.__BRIDGE: Final[Bridge] = configuration.bridge(bridge_key)

    def replace_secrets(self, input: str) -> str:
        return input  # TODO replacement
