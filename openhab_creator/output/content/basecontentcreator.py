from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from pathlib import Path
import os
import re

import shutil

from openhab_creator import logger
from openhab_creator.exception import BuildException

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SecretsStorage


class BaseContentCreator():
    def __init__(self, outputdir: str):
        self._outputdir: Path = Path(outputdir)

        pwd = Path(__file__).resolve().parent.parent.parent
        self._srcdir: str = pwd / 'content'

    def _copy_all_files_from_subdir(self,
                                    subdir: str, destination: Optional[str] = None,
                                    configdir: Optional[str] = None,
                                    only_updated: Optional[bool] = True) -> None:
        if destination is None:
            dest_dir = self._create_outputdir_if_not_exists(subdir)
        else:
            dest_dir = self._create_outputdir_if_not_exists(destination)

        srcdir = Path(configdir or self._srcdir)

        self.copytree(str(srcdir / subdir), str(dest_dir), only_updated)

    @classmethod
    def copytree(cls, srcdir: str, destdir: str, only_updated: bool) -> None:
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        for item in os.listdir(srcdir):
            src = os.path.join(srcdir, item)
            dest = os.path.join(destdir, item)
            if os.path.isdir(src):
                cls.copytree(src, dest, only_updated)
            else:
                if not only_updated\
                        or not os.path.exists(dest)\
                        or os.stat(src).st_mtime - os.stat(dest).st_mtime > 1:
                    logger.info('Copy %s -> %s', src, dest)
                    shutil.copy2(src, dest)

    def _create_outputdir_if_not_exists(self, subdir: str) -> Path:
        destination = self._outputdir / subdir
        if not os.path.exists(destination):
            os.makedirs(destination)

        return destination

    def _copy_file_with_secrets(self,
                                configdir: str,
                                input_file: str,
                                secrets: SecretsStorage,
                                output_file: Optional[str] = None) -> None:
        srcfile = Path(configdir) / input_file
        if output_file is None:
            output_file = input_file

        if os.path.exists(srcfile):
            with open(srcfile, 'r', encoding='utf-8') as fobj:
                content = fobj.read()
                content = self.__replace_secrets(content, secrets)

                if secrets.handle_missing():
                    raise BuildException('Missing secrets')

                self.__write_configuration(output_file, content)

    @staticmethod
    def __replace_secrets(content: str, secrets_storage: SecretsStorage) -> str:
        secrets = re.findall('__([A-Z0-9_]*)__', content, re.MULTILINE)
        for secret in secrets:
            replace = secrets_storage.secret(*secret.split('_'))
            content = content.replace(f'__{secret}__', replace)

        return content

    def __write_configuration(self, output_file: str, content: str) -> None:
        destfile = self._outputdir / output_file

        os.makedirs(os.path.dirname(os.path.abspath(destfile)), exist_ok=True)

        with open(destfile, 'w') as fobj:
            logger.info('Write %s/%s', self._outputdir, output_file)
            fobj.write(content)
