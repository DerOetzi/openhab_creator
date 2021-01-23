from __future__ import annotations

import os
import re
import shutil

from openhab_creator.models.secretsregistry import SecretsRegistry
from openhab_creator.output.content.basecontentcreator import \
    BaseContentCreator


class RulesCreator(BaseContentCreator):

    def build(self, configdir: str):
        self._copy_all_files_from_subdir(
            '/automation/lib', '/automation/lib/python/personal')

        self._copy_all_files_from_subdir(
            '/automation/scripts', '/automation/jsr223/personal')

        self.__prepare_and_copy_configuration(configdir)

    def __prepare_and_copy_configuration(self, configdir) -> None:
        srcfile = f'{configdir}/configuration.py'
        if os.path.exists(srcfile):
            with open(srcfile, 'r') as f:
                content = f.read()
                content = self.__replace_secrets(content)

                if SecretsRegistry.has_missing():
                    SecretsRegistry.handle_missing()
                    return

                self.__write_configuration(content)

    def __replace_secrets(self, content: str) -> str:
        secrets = re.findall('__([A-Z1-9_]*)__', content, re.MULTILINE)
        for secret in secrets:
            replace = SecretsRegistry.secret(secret)
            content = content.replace(f'__{secret}__', replace)

        return content

    def __write_configuration(self, content: str) -> None:
        with open(f'{self._outputdir}/automation/lib/python/configuration.py', 'w') as f:
            f.write(content)
