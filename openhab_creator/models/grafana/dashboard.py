from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict

import requests
import json

from openhab_creator import _, logger, CreatorEnum

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class Retention(CreatorEnum):
    MONTHLY = 'm'
    YEARLY = 'y'


class Period(CreatorEnum):
    DAY = '24h', _('Day'), Retention.MONTHLY
    WEEK = '7d', _('Week'), Retention.MONTHLY
    MONTH = '31d', _('Month'), Retention.MONTHLY
    YEAR = '1y', _('Year'), Retention.YEARLY

    def __init__(self, value: str, label: str, retention: Retention):
        self._label: str = label
        self._retention: Retention = retention

    @property
    def label(self) -> str:
        return self._label

    @property
    def retention(self) -> Retention:
        return self._retention


class Dashboard(object):
    def __init__(self, configuration: Configuration):
        self.host: Optional[str] = configuration.secrets.secret_optional(
            'grafana', 'host')

        if self.__init_from_grafana():
            self._save_dashboard_to_configdir(configuration.configdir)

    def __init_from_grafana(self) -> bool:
        success = False
        if self.host is not None:
            try:
                response = requests.get(
                    f'{self.host}/api/dashboards/uid/openhab3')
                if response.status_code == 200:
                    self.online = response.json()['dashboard']
                    success = True
                    self.__init_panels()
                else:
                    logger.error(response.json()['message'])
            except requests.exceptions.ConnectionError:
                logger.error(f'Could not connect to grafana on {self.host}')

        return success

    def __init_panels(self) -> None:
        self.panels = {}

        for panel in self.online['panels']:
            if 'title' in panel and panel['title'] != '':
                self.panels[panel['title']] = {
                    'id': panel['id'],
                    'height': panel['gridPos']['h'] * 35
                }
                logger.debug(self.panels[panel['title']])

    def _save_dashboard_to_configdir(self, configdir: str) -> None:
        with open(f'{configdir}/grafana_dashboard.json', 'w') as fp:
            json.dump(self.online, fp, indent=4)

    def panel_urls(self, identifier: str) -> Optional[Dict[str, str]]:
        urls = {}

        if identifier in self.panels:
            panel_config = self.panels[identifier]

            for period in Period:

                url = f'{self.host}/render/d-solo/openhab3?'
                url += f'from=now-{period}&to=now&'
                url += f'var-rp={period.retention}&'
                url += f'panelId={panel_config["id"]}&'
                url += f'width=700&height={panel_config["height"]}'

                urls[period] = url
        else:
            logger.warn(f'No panel {identifier} on dashboard')
            urls = None

        return urls