from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.sitemap import Page, Sitemap, Switch, Text
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

        self.build_reminders(sitemap, page, configuration)
        self.build_birthdays(page)
        self.build_configitems(page, configuration)

    @staticmethod
    def build_reminders(sitemap: Sitemap, page: Page, configuration: Configuration) -> None:
        has_reminders, reminders = configuration.equipment.has(
            'reminder', filter_categories=['calendar'])

        if has_reminders:
            frame = page.frame('reminders', _('Reminders'))
            for reminder in reminders:
                Switch(reminder.item_ids.confirm, [('ON', _('Done'))])\
                    .visibility((reminder.item_ids.confirm, '==', 'OFF'))\
                    .append_to(sitemap)

                Text(reminder.item_ids.reminder)\
                    .visibility((reminder.item_ids.confirm, '==', 'ON'))\
                    .append_to(frame)

                Switch(reminder.item_ids.confirm, [('ON', _('Done'))])\
                    .visibility((reminder.item_ids.confirm, '==', 'OFF'))\
                    .append_to(frame)

    @staticmethod
    def build_birthdays(page: Page) -> None:
        frame = page.frame('birthdays', _('Next 10 upcoming birthdays'))
        for i in range(0, 10):
            Text(f'nextBirthday{i}')\
                .visibility((f'nextBirthday{i}', '!=', 'NULL'))\
                .append_to(frame)

    @staticmethod
    def build_configitems(page: Page, configuration: Configuration) -> None:
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

        if configuration.equipment.has('garbagecan'):
            for garbagecan in configuration.equipment.equipment('garbagecan'):
                Text(garbagecan.item_ids.begin)\
                    .visibility((garbagecan.item_ids.begin, '!=', 'NULL'))\
                    .append_to(frame)

    def build_statuspage(self, statuspage: Page, configuration: Configuration) -> None:
        """No statuspage for calendar"""

    def build_configpage(self, configpage: Page, configuration: Configuration) -> None:
        """No configpage for calendar"""
