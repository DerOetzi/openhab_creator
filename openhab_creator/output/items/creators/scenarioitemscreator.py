from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation, Scenario
from openhab_creator.models.items import Group, GroupType, String, Switch
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(1)
class ScenarioItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Switch('autoScenario')\
            .label(_('Time controlled'))\
            .expire('1h', 'ON')\
            .append_to(self)

        String('autoScenarioActive')\
            .label(_('Scenario'))\
            .format('%s')\
            .icon('scenario')\
            .auto()\
            .append_to(self)

        Switch('autoGuestStayed')\
            .label(_('Guest stayed'))\
            .icon('guest')\
            .auto()\
            .append_to(self)

        self.write_file('scenario')
