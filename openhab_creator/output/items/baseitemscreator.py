from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.items.baseitem import BaseItem


class BaseItemsCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('items', outputdir)

        self.items: List[BaseItem] = []

    def build(self, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build")

    def append_item(self, item: BaseItem) -> None:
        self.items.append(item)

    def write_file(self, filename: str) -> None:
        for item in self.items:
            item.build_item(self)

        super().write_file(filename)

        self.items.clear()
