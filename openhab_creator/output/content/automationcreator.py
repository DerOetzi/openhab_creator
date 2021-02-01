from __future__ import annotations

from typing import TYPE_CHECKING

import os
import re
import shutil

from openhab_creator.output.content.basecontentcreator import \
    BaseContentCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration, SecretsStorage


class AutomationCreator(BaseContentCreator):
    BASESRCPATH = 'automation/helper/Core/automation/'

    def build(self, configdir: str, configuration: Configuration):
        self._copy_all_files_from_subdir('scripts')

        self._copy_all_files_from_subdir(
            f'{self.BASESRCPATH}lib/python/core', '/automation/lib/python/core')

        self._copy_all_files_from_subdir(
            f'{self.BASESRCPATH}jsr223/python/core', '/automation/jsr223/core')

        self._copy_all_files_from_subdir(
            '/automation/libraries', '/automation/lib/python/personal')

        self._copy_all_files_from_subdir(
            '/automation/rules', '/automation/jsr223/personal')

        self.__prepare_and_copy_configuration(configdir, configuration.secrets)

    def __prepare_and_copy_configuration(self, configdir: str, secrets: SecretsStorage) -> None:
        srcfile = f'{configdir}/configuration.py'
        if os.path.exists(srcfile):
            with open(srcfile, 'r') as f:
                content = f.read()
                content = self.__replace_secrets(content, secrets)

                if secrets.handle_missing():
                    return

                self.__write_configuration(content)

    def __replace_secrets(self, content: str, secrets_storage: SecretsStorage) -> str:
        secrets = re.findall('__([A-Z1-9_]*)__', content, re.MULTILINE)
        for secret in secrets:
            replace = secrets_storage.secret(secret)
            content = content.replace(f'__{secret}__', replace)

        return content

    def __write_configuration(self, content: str) -> None:
        with open(f'{self._outputdir}/automation/lib/python/configuration.py', 'w') as f:
            f.write(content)
