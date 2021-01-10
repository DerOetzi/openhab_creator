from typing import Any, List, Dict, Literal

from openhab_creator.output.basecreator import BaseCreator

Grouptypes = Literal['onoff', 'dimmer_avg', 'number_avg']
Itemtypes = Literal['Number', 'Switch']


class ItemCreator(BaseCreator):
    def __init__(self, outputdir: str, check_only: bool):
        super().__init__('items', outputdir, check_only)

    def _create_group(self, id: str, name: str, icon: str = None, groups: List[str] = [], tags: List[str] = [], typed: Grouptypes = None) -> None:
        groupstring = f"Group{self.__grouptype(typed)} {id}\n  \"{name}\""
        groupstring += self.__iconstring(icon)
        groupstring += self.__groupsstring(groups)
        groupstring += self.__tagsstring(tags)
        groupstring += "\n"

        self._append(groupstring)

    def __grouptype(self, typed: Grouptypes = None):
        if typed == 'onoff':
            return ':Switch:OR(ON,OFF)'
        elif typed == 'dimmer_avg':
            return ':Dimmer:AVG'
        elif typed == 'number_avg':
            return ':Number:AVG'
        else:
            return ''

    def _create_item(self, typed: Itemtypes, id: str, name: str, icon: str = None, groups: List[str] = [], tags: List[str] = [], metadata: Dict[str, Any] = {}) -> None:
        itemstring = f"{typed} {id}\n  \"{name}\""
        itemstring += self.__iconstring(icon)
        itemstring += self.__groupsstring(groups)
        itemstring += self.__tagsstring(tags)
        itemstring += self.__metadatastring(metadata)
        itemstring += "\n"

        self._append(itemstring)

    def __iconstring(self, icon: str = None) -> str:
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