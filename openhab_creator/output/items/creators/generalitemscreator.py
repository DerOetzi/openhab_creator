from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator
from openhab_creator.output.items.itemscreatorregistry import \
    ItemsCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


@ItemsCreatorRegistry(0)
class GeneralItemsCreator(BaseItemsCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self._create_group('Config', _('Configuration items'))
        self._create_group('Sensor', _('Sensor items'))
        self._create_group(
            'Auto', _('Scene controlled configuration items'), groups=['Config'])

        self._write_file('generals')
