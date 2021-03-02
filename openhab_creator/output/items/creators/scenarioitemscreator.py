from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation, Scenario
from openhab_creator.models.items import (Group, GroupType, Number, NumberType, String,
                                          Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(1)
class ScenarioItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Switch('autoScenario')\
            .label(_('Time controlled'))\
            .icon('auto')\
            .expire('1h', 'ON')\
            .append_to(self)

        String(Scenario.scenarioactive_id())\
            .label(_('Scenario'))\
            .icon('scenario')\
            .auto()\
            .append_to(self)

        Switch('autoGuestStayed')\
            .label(_('Guest stayed'))\
            .icon('guest')\
            .auto()\
            .append_to(self)

        for scenario in Scenario:
            Group(scenario.assignment_id)\
                .typed(GroupType.ONOFF)\
                .auto()\
                .append_to(self)

            if scenario.has_time:
                Number(scenario.timeworkingday_id)\
                    .typed(NumberType.TIME)\
                    .label(scenario.label)\
                    .format('%d h')\
                    .icon('clock')\
                    .auto()\
                    .append_to(self)

                Number(scenario.timeweekend_id)\
                    .typed(NumberType.TIME)\
                    .label(scenario.label)\
                    .format('%d h')\
                    .icon('clock')\
                    .auto()\
                    .append_to(self)

        self.write_file('scenario')
