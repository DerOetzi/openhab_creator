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
    DAY = 'd', _('Today'), _('Yesterday'),Retention.MONTHLY, AggregateWindow.HOUR
    WEEK = 'w', _('Week'), _('Last week'), Retention.MONTHLY, AggregateWindow.DAY
    MONTH = 'M', _('Month'), _('Last month'), Retention.MONTHLY, AggregateWindow.DAY
    YEAR = 'y', _('Year'), _('Last year'), Retention.YEARLY, AggregateWindow.MONTH
    
    def __init__(self, period: str, label: str, last_label:str, retention: Retention, aggregation: AggregateWindow):
        self._period = period
        self.label: str = label
        self.last_label: str = last_label
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

                url = self.url_for_period(aggregations, panel_config, period, f'now/{period}')
                url_last = self.url_for_period(aggregations, panel_config, period, f'now-1{period}/{period}')

                urls[period] = (url, url_last)
        else:
            logger.warning('No panel %s on dashboard', identifier)
            urls = None

        return urls

    def url_for_period(self, aggregations, panel_config, period, time: str):
        url = f'{self.host}/render/d-solo/openhab3?'
        url += f'from={time}&to={time}&'
        url += f'var-rp={period.retention}&'

        if aggregations and period in aggregations:
            url += f'var-agg={aggregations[period].every}&'
        else:
            url += f'var-agg={period.aggregation.every}&'

        url += f'panelId={panel_config["id"]}&'
        url += f'width=700&height={panel_config["height"]}'
        return url
