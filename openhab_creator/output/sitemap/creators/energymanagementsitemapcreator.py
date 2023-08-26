from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.grafana import AggregateWindow, Period
from openhab_creator.models.sitemap import Frame, Page, Sitemap, Text
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.smartmeter import \
        SmartMeter


@SitemapCreatorPipeline(mainpage=0, configpage=0)
class EnergyManagementSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        page = Page(label=_('Energy management'))\
            .icon('energy')\
            .append_to(sitemap.second_frame)

        self.build_smartmeters(page, configuration)

    def build_smartmeters(self, page: Page, configuration: Configuration) -> None:
        has_smartmeters, smartmeters = configuration.equipment.has(
            'smartmeter')
        if has_smartmeters:
            frame = page.frame('smartmeter_frame', _('Smart meters'))

            for smartmeter in smartmeters:
                self._build_smartmeter(configuration, frame, smartmeter)

    def _build_smartmeter(
            self,
            configuration: Configuration,
            frame: Frame,
            smartmeter: SmartMeter) -> None:
        page = Page(label=smartmeter.blankname)\
            .append_to(frame)

        if smartmeter.points.has_power_total:
            page.item(smartmeter.item_ids.power_total)

        if smartmeter.points.has_consumed_total:
            self._build_consumed_total(page, smartmeter)

        if smartmeter.points.has_delivered_total:
            Text(smartmeter.item_ids.delivered_total)\
                .append_to(page)

        if smartmeter.points.has_power_total:
            self._build_power_total(page, smartmeter)

        self._add_grafana(configuration.dashboard,
                          page, ['', _('Average per hour'),
                                 _('Average per weekday')],
                          smartmeter.blankname + ' ',
                          {Period.DAY: AggregateWindow.HOUR,
                           Period.WEEK: AggregateWindow.DAY,
                           Period.MONTH: AggregateWindow.DAY,
                           Period.YEAR: AggregateWindow.MONTH,
                           Period.YEARS: AggregateWindow.MONTH})

    def _build_consumed_total(self, page: Page, smartmeter: SmartMeter) -> None:
        if smartmeter.points.has_consumed_tariff:
            subpage = Page(smartmeter.item_ids.consumed_total)\
                .append_to(page)

            Text(smartmeter.item_ids.consumed_total)\
                .append_to(subpage)

            for tariff in range(1, 3):
                if smartmeter.points.has_consumed(tariff):
                    Text(smartmeter.item_ids.consumed(tariff))\
                        .append_to(subpage)
        else:
            Text(smartmeter.item_ids.consumed_total)\
                .append_to(page)

    def _build_power_total(self, page: Page, smartmeter: SmartMeter) -> None:
        if smartmeter.points.has_power_phase:
            subpage = Page(smartmeter.item_ids.power_total)\
                .append_to(page)

            Text(smartmeter.item_ids.power_total)\
                .append_to(subpage)

            for phase in range(1, 4):
                if smartmeter.points.has_power(phase):
                    Text(smartmeter.item_ids.power(phase))\
                        .append_to(subpage)
        else:
            Text(smartmeter.item_ids.power_total)\
                .append_to(page)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for energy management"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for energy management"""
