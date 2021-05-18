from __future__ import annotations
from typing import TYPE_CHECKING

from openhab_creator.output.content.basecontentcreator import BaseContentCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class BasicConfigCreator(BaseContentCreator):
    def build(self, configuration: Configuration) -> None:
        self._copy_file_with_secrets(
            self._srcdir, 'services/mapdb.cfg', configuration.secrets)
        self._copy_file_with_secrets(
            self._srcdir, 'services/influxdb.cfg', configuration.secrets)
        self._copy_all_files_from_subdir('services')
        self._copy_all_files_from_subdir('persistence')
        self._copy_all_files_from_subdir('transform')
        self._copy_all_files_from_subdir(
            'ephemeris', configdir=configuration.configdir)
        self._copy_all_files_from_subdir(
            'html', configdir=configuration.configdir)
