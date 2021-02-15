import os
from typing import List, Optional


class BaseCreator(object):

    def __init__(self, typed: str, outputdir: str, subdir: Optional[str] = None):
        self.typed: str = typed
        self.outputdir: str = outputdir

        self.subdir: str = subdir
        if self.subdir is None:
            self.subdir = self.typed

        self.lines: List[str] = []

    def append(self, lines: str) -> None:
        self.lines.append(lines)

    def write_file(self, filename: str) -> None:
        self._create_outputdir_if_not_exists()

        with open(f'{self.outputdir}/{self.subdir}/{filename}.{self.typed}', 'w') as f:
            f.writelines("\n".join(self.lines))

        self.lines.clear()

    def _create_outputdir_if_not_exists(self) -> None:
        if not os.path.exists(f'{self.outputdir}/{self.subdir}'):
            os.makedirs(f'{self.outputdir}/{self.subdir}')
