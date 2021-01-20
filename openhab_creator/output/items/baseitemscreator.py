from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from openhab_creator import _
from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.thing.equipment import Equipment
    from openhab_creator.models.configuration import SmarthomeConfiguration


class BaseItemsCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('items', outputdir)

    def build(self, configuration: SmarthomeConfiguration) -> None:
        raise NotImplementedError("Must override build")

    def _create_group(self,
                      identifier: str,
                      name: str,
                      icon: Optional[str] = None,
                      groups: List[str] = [],
                      tags: List[str] = [],
                      typed: Optional[str] = None) -> None:
        groupstring = f"Group{self.__grouptype(typed)} {identifier}\n  \"{name}\""
        groupstring += self.__iconstring(icon)
        groupstring += self.__groupsstring(groups)
        groupstring += self.__tagsstring(tags)
        groupstring += "\n"

        self._append(groupstring)

    def __grouptype(self, typed: Optional[str] = None):
        if typed == 'onoff':
            return ':Switch:OR(ON,OFF)'
        elif typed == 'dimmer_avg':
            return ':Dimmer:AVG'
        elif typed == 'number_avg':
            return ':Number:AVG'
        elif typed == 'number_max':
            return ':Number:MAX'
        else:
            return ''

    def _create_item(self,
                     typed: str,
                     identifier: str,
                     name: str,
                     icon: Optional[str] = None,
                     groups: List[str] = [],
                     tags: List[str] = [],
                     metadata: Dict[str, Any] = {}) -> None:
        itemstring = f"{typed} {identifier}\n  \"{name}\""
        itemstring += self.__iconstring(icon)
        itemstring += self.__groupsstring(groups)
        itemstring += self.__tagsstring(tags)
        itemstring += self.__metadatastring(metadata)
        itemstring += "\n"

        self._append(itemstring)

    def __iconstring(self, icon: Optional[str] = None) -> str:
        if icon is None:
            return ''

        return f"\n  <{icon}>"

    def __groupsstring(self, groups: List[str]) -> str:
        if len(groups) == 0:
            return ''

        return "\n  (" + ",".join(groups) + ')'

    def __tagsstring(self, tags: List[str]) -> str:
        if len(tags) == 0:
            return ''

        return "\n  [" + ",".join(['"' + tag + '"' for tag in tags]) + ']'

    def __metadatastring(self, metadata: Dict[str, Any] = {}):
        if len(metadata) == 0:
            return ''

        return "\n  {" + ",".join([key + '="' + value + '"' for key, value in metadata.items()]) + '}'

    def _create_battery(self, equipment: Equipment, parent_equipment: str) -> None:
        if equipment.has_battery():
            self._create_group(equipment.battery_id(), _(
                'Battery'), groups=[parent_equipment], tags=['Battery'])

            self._create_item(typed='Switch',
                              identifier=equipment.lowbattery_id(),
                              name=_('Battery low'),
                              icon='lowbattery',
                              groups=['LowBattery', equipment.battery_id()],
                              tags=['LowBattery'],
                              metadata={'channel': equipment.channel('battery', 'low')})

            self._create_item(typed='Number:Dimensionless',
                              identifier=equipment.levelbattery_id(),
                              name=_('Battery level [%d %%]'),
                              icon='battery',
                              groups=['Sensor', equipment.battery_id()],
                              tags=['Status'],
                              metadata={'channel': equipment.channel('battery', 'level')})
