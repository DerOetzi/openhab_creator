from typing import List

from openhab_creator.output.basecreator import BaseCreator


class ItemCreator(BaseCreator):

    def __init__(self, outputdir: str, check_only: bool):
        super().__init__('items', outputdir, check_only)

    def _create_group(self, id: str, name: str, icon: str = None, groups: List[str] = [], tags: List[str] = []) -> str:
        return f"Group {id}\n  \"{name}\"{self.__iconstring(icon)}{self.__groupsstring(groups)}{self.__tagsstring(tags)}\n"

    def __iconstring(self, icon: str = None) -> str:
        if icon is None:
            return ''

        return f"\n  <{icon}>"

    def __groupsstring(self, groups: List[str]) -> str:
        if len(groups) == 0:
            return ''

        return "\n  (" + ",".join(groups) +')'

    def __tagsstring(self, tags: List[str]) -> str:
        if len(tags) == 0:
            return ''

        return "\n  [" + ",".join(['"' + tag + '"' for tag in tags]) + ']'

