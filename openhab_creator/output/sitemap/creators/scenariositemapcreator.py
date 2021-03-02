from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import Scenario, MapTransformation
from openhab_creator.models.sitemap import (Page, Selection, Setpoint, Sitemap,
                                            Switch)
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@SitemapCreatorPipeline(mainpage=0, configpage=0)
class ScenarioSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        frame = sitemap.frame('second')
        page = Page(Scenario.scenarioactive_id())\
            .append_to(frame)

        mappings = {
            "normal": [],
            "eating": [],
            "special": []
        }

        for scenario in Scenario:
            mappings[scenario.category].append(
                (scenario.identifier, scenario.label))

        Selection(Scenario.scenarioactive_id(), mappings['normal'])\
            .label(_('Scenarios'))\
            .append_to(page)

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        page = Page(Scenario.scenarioactive_id())\
            .append_to(configpage)

        workingday_frame = page.frame('workingday', _('Working day'))
        weekend_frame = page.frame('weekend', _('Weekend and holiday'))

        for scenario in Scenario:
            if scenario.has_time:
                Setpoint(scenario.timeworkingday_id,
                         scenario.begin, scenario.end)\
                    .append_to(workingday_frame)

                Setpoint(scenario.timeweekend_id,
                         scenario.begin, scenario.end)\
                    .append_to(weekend_frame)
