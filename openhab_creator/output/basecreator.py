import os
from typing import List, Optional


class BaseCreator(object):

    def __init__(self, typed: str, outputdir: str, check_only: Optional[bool] = False, subdir: Optional[str] = None):
        self._typed: str = typed
        self._outputdir: str = outputdir
        self._check_only: bool = check_only

        self._subdir: str = subdir
        if self._subdir is None:
            self._subdir = self._typed

        self.__lines: List[str] = []

    def _append(self, lines: str) -> None:
        self.__lines.append(lines)

    def _write_file(self, filename: str) -> None:
        if self._check_only:
            self.__lines.clear()
            return

        self.__create_outputdir_if_not_exists()

        with open(f'{self._outputdir}/{self._subdir}/{filename}.{self._typed}', 'w') as f:
            f.writelines("\n".join(self.__lines))

        self.__lines.clear()

    def __create_outputdir_if_not_exists(self) -> None:
        if not os.path.exists(f'{self._outputdir}/{self._subdir}'):
            os.makedirs(f'{self._outputdir}/{self._subdir}')
