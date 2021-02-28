from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from pathlib import Path
import os
import re

import distutils.log
import distutils.dir_util

from openhab_creator import logger
from openhab_creator.exception import BuildException

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SecretsStorage


class BaseContentCreator(object):
    def __init__(self, outputdir: str):
        self._outputdir: str = outputdir

        pwd = Path(__file__).resolve().parent.parent.parent
        self._srcdir: str = f'{pwd}/content/'

    def _copy_all_files_from_subdir(self, subdir: str, destination: Optional[str] = None) -> None:
        if destination is None:
            dest_dir = self._create_outputdir_if_not_exists(subdir)
        else:
            dest_dir = self._create_outputdir_if_not_exists(destination)

        distutils.log.set_verbosity(distutils.log.DEBUG)
        distutils.dir_util.copy_tree(
            f'{self._srcdir}{subdir}',
            dest_dir,
            update=1,
            verbose=1,
        )

    def _create_outputdir_if_not_exists(self, subdir: str) -> str:
        destination = f'{self._outputdir}/{subdir}/'
        if not os.path.exists(destination):
            os.makedirs(destination)

        return destination

    def _copy_file_with_secrets(self,
                                configdir: str,
                                input_file: str,
                                secrets: SecretsStorage,
                                output_file: Optional[str] = None) -> None:
        srcfile = f'{configdir}/{input_file}'
        if output_file is None:
            output_file = input_file

        if os.path.exists(srcfile):
            with open(srcfile, 'r') as f:
                content = f.read()
                content = self.__replace_secrets(content, secrets)

                if secrets.handle_missing():
                    raise BuildException('Missing secrets')

                self.__write_configuration(output_file, content)

    def __replace_secrets(self, content: str, secrets_storage: SecretsStorage) -> str:
        secrets = re.findall('__([A-Z1-9_]*)__', content, re.MULTILINE)
        for secret in secrets:
            replace = secrets_storage.secret(secret)
            content = content.replace(f'__{secret}__', replace)

        return content

    def __write_configuration(self, output_file: str, content: str) -> None:
        with open(f'{self._outputdir}/{output_file}', 'w') as f:
            logger.info(f'Write {self._outputdir}/{output_file}')
            f.write(content)
