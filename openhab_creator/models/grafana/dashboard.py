from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict
from enum import Enum

import requests

from openhab_creator import _, logger

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class Retention(Enum):
    MONTHLY = 'm'
    YEARLY = 'y'


class Period(Enum):
    DAY = {
        'period': '24h',
        'name': _('Day'),
        'retention': Retention.MONTHLY
    }

    WEEK = {
        'period': '7d',
        'name': _('Week'),
        'retention': Retention.MONTHLY
    }

    MONTH = {
        'period': '31d',
        'name': _('Month'),
        'retention': Retention.MONTHLY
    }

    YEAR = {
        'period': '1y',
        'name': _('Year'),
        'retention': Retention.YEARLY
    }


class Dashboard(object):
    def __init__(self, configuration: Configuration):
        self.host: Optional[str] = configuration.secrets.secret_optional(
            'grafana', 'host')

        self.__init_from_grafana()

    def __init_from_grafana(self) -> None:
        if self.host is not None:
            try:
                response = requests.get(
                    f'{self.host}/api/dashboards/uid/openhab3')
                if response.status_code == 200:
                    self.online = response.json()['dashboard']
                    self.__init_panels()
                else:
                    logger.error(response.json()['message'])
            except requests.exceptions.ConnectionError:
                logger.error(f'Could not connect to grafana on {self.host}')

    def __init_panels(self) -> None:
        self.panels = {}

        for panel in self.online['panels']:
            if 'description' in panel and panel['description'] != '':
                self.panels[panel['description']] = {
                    'description': panel['description'],
                    'id': panel['id'],
                    'height': panel['gridPos']['h'] * 35
                }
                logger.debug(self.panels[panel['description']])

    def panel_urls(self, identifier: str) -> Optional[Dict[str, str]]:
        urls = {}

        if identifier in self.panels:
            panel_config = self.panels[identifier]

            for period_config in Period:
                period = period_config.value['period']
                retention = period_config.value['retention'].value

                url = f'{self.host}/render/d-solo/openhab3?'
                url += f'from=now-{period}&to=now&'
                url += f'var-rp={retention}&'
                url += f'panelId={panel_config["id"]}&'
                url += f'width=700&height={panel_config["height"]}'

                urls[period] = url
        else:
            logger.warn(f'No panel {identifier} on dashboard')
            urls = None

        return urls
