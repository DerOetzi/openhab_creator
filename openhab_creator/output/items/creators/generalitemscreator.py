from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.output.items.itemscreatorregistry import \
    ItemsCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


@ItemsCreatorRegistry(0)
class GeneralItemsCreator(BaseItemsCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self._create_group('Config', 'Configuration items')
        self._create_group('Sensor', 'Sensor items')

        self._write_file('generals')
