from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Text, Sitemap
from openhab_creator.output.sitemap import SitemapCreatorPipeline
from openhab_creator.output.sitemap.basesitemapcreator import \
    BaseSitemapCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@SitemapCreatorPipeline(mainpage=0)
class CalendarSitemapCreator(BaseSitemapCreator):
    def build_mainpage(self, sitemap: Sitemap, configuration: Configuration) -> None:
        Text('todaySpecialDay')\
            .visibility(('todaySpecialDay', '!=', 'NULL'))\
            .append_to(sitemap)

        page = Page(label=_('Calendar'))\
            .icon('calendar')\
            .append_to(sitemap.second_frame)

        self.build_birthdays(page)
        self.build_configitems(page)

    def build_birthdays(self, page: Page) -> None:
        frame = page.frame('birthdays', _('Next 10 upcoming birthdays'))
        for i in range(0, 10):
            Text(f'nextBirthday{i}')\
                .visibility((f'nextBirthday{i}', '!=', 'NULL'))\
                .append_to(frame)

    def build_configitems(self, page: Page) -> None:
        frame = page.frame('config', _('Configuration'))

        Text('nextSpecialDay')\
            .visibility(('nextSpecialDay', '!=', 'NULL'))\
            .append_to(frame)

        Text('holidayName')\
            .visibility(('holiday', '==', 'ON'))\
            .append_to(frame)

        Text('holiday')\
            .visibility(('holiday', '==', 'OFF'))\
            .append_to(frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for calendar"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for calendar"""
