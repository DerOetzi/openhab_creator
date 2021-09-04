from __future__ import annotations

import json
from typing import TYPE_CHECKING

from openhab_creator.models.items.baseitem import BaseItem
from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.grafana import Dashboard


class DocumentationCreator(BaseCreator):
    def __init__(self, configdir: str):
        super().__init__('json', configdir, 'documentation')

    def build(self, configuration: Configuration) -> None:
        self._build_influxdb_series()
        self._build_aisensors()
        self._save_grafana_dashboard(configuration.dashboard)

    def _build_influxdb_series(self) -> None:
        self._write_json(BaseItem.influxdb_series, 'influxdb_series')

    def _build_aisensors(self) -> None:
        self._write_json(BaseItem.aisensors, 'aisensors')

    def _save_grafana_dashboard(self, dashboard: Dashboard) -> None:
        if dashboard.success:
            self._write_json(dashboard.online, 'grafana_dashboard')

    def _write_json(self, raw_object, filename: str) -> None:
        self.append(json.dumps(raw_object, indent=4))
        self.write_file(filename)
