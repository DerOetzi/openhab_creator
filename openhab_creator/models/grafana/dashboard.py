from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict

import requests

from openhab_creator import _, logger, CreatorEnum

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class Retention(CreatorEnum):
    MONTHLY = 'm'
    YEARLY = 'y'


class AggregateWindow(CreatorEnum):
    HOUR = '1h'
    DAY = '1d'
    WEEK = '1w'
    MONTH = '1mo'

    def __init__(self, every: str) -> None:
        self.every = every


class Period(CreatorEnum):
    DAY = '24h', _('Day'), Retention.MONTHLY, AggregateWindow.HOUR
    WEEK = '7d', _('Week'), Retention.MONTHLY, AggregateWindow.HOUR
    MONTH = '31d', _('Month'), Retention.MONTHLY, AggregateWindow.HOUR
    YEAR = '1y', _('Year'), Retention.YEARLY, AggregateWindow.DAY
    YEARS = '2y', _('2 years'), Retention.YEARLY, AggregateWindow.DAY

    def __init__(self, period: str, label: str, retention: Retention, aggregation: AggregateWindow):
        self._period = period
        self.label: str = label
        self.retention: Retention = retention
        self.aggregation: AggregateWindow = aggregation


class Dashboard():
    def __init__(self, configuration: Configuration):
        self.host: Optional[str] = configuration.secrets.secret_optional(
            'grafana', 'host')

        self.panels = {}

        self.success: bool = self.init_from_grafana()

    def init_from_grafana(self) -> bool:
        success = False
        if self.host is not None:
            try:
                response = requests.get(
                    f'{self.host}/api/dashboards/uid/openhab3', timeout=2)
                if response.status_code == 200:
                    self.online = response.json()['dashboard']
                    success = True
                    self.__init_panels()
                else:
                    logger.error(response.json()['message'])
            except requests.exceptions.ConnectionError:
                logger.error('Could not connect to grafana on %s', self.host)

        return success

    def __init_panels(self) -> None:
        for row in self.online['panels']:
            if 'panels' in row:
                for panel in row['panels']:
                    self.__init_panel(panel)
            else:
                self.__init_panel(row)

    def __init_panel(self, panel) -> None:
        if 'title' in panel and panel['title'] != '':
            self.panels[panel['title']] = {
                'id': panel['id'],
                'height': panel['gridPos']['h'] * 35
            }
            logger.debug('%s: %s', panel['title'],
                         self.panels[panel['title']])

    def panel_urls(self,
                   identifier: str,
                   aggregations: Optional[Dict[Period, AggregateWindow]] = None) \
            -> Optional[Dict[str, str]]:
        urls = {}

        if identifier in self.panels:
            panel_config = self.panels[identifier]

            for period in Period:

                url = f'{self.host}/render/d-solo/openhab3?'
                url += f'from=now-{period}&to=now&'
                url += f'var-rp={period.retention}&'

                if aggregations and period in aggregations:
                    url += f'var-agg={aggregations[period].every}&'
                else:
                    url += f'var-agg={period.aggregation.every}&'

                url += f'panelId={panel_config["id"]}&'
                url += f'width=700&height={panel_config["height"]}'

                urls[period] = url
        else:
            logger.warning('No panel %s on dashboard', identifier)
            urls = None

        return urls
