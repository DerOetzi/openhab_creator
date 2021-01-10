import os
from typing import List


class BaseCreator(object):

    def __init__(self, typed: str, outputdir: str, check_only: bool = False):
        self._typed: str = typed
        self._outputdir: str = outputdir
        self._check_only: bool = check_only

        self.__lines: List[str] = []

    def _append(self, lines: str) -> None:
        self.__lines.append(lines)

    def _write_file(self, filename: str) -> None:
        if self._check_only:
            return

        self.__create_outputdir_if_not_exists()

        with open(f'{self._outputdir}/{self._typed}/{filename}.{self._typed}', 'w') as f:
            f.writelines("\n".join(self.__lines))

    def __create_outputdir_if_not_exists(self) -> None:
        if not os.path.exists(f'{self._outputdir}/{self._typed}'):
            os.makedirs(f'{self._outputdir}/{self._typed}')
