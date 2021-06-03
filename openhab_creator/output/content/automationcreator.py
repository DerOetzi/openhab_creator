from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator.output.content.basecontentcreator import \
    BaseContentCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration, SecretsStorage


class AutomationCreator(BaseContentCreator):
    BASESRCPATH = 'automation/helper/Core/automation/'

    def build(self, configdir: str, configuration: Configuration):
        self._copy_all_files_from_subdir('scripts')

        self._copy_all_files_from_subdir(
            f'{self.BASESRCPATH}lib/python/core', 'automation/lib/python/core')

        self._copy_all_files_from_subdir(
            f'{self.BASESRCPATH}jsr223/python/core', 'automation/jsr223/core')

        self._copy_all_files_from_subdir(
            'automation/libraries', 'automation/lib/python/personal')

        self._copy_all_files_from_subdir(
            'automation/rules', 'automation/jsr223/personal', update=False)

        self.prepare_and_copy_configuration(configdir, configuration.secrets)

    def prepare_and_copy_configuration(self,
                                       configdir: str,
                                       secrets: SecretsStorage) -> None:
        self._copy_file_with_secrets(
            configdir, 'configuration.py',
            secrets, 'automation/lib/python/configuration.py')
