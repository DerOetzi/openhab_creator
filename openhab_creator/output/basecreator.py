import os
from typing import List, Optional

from pathlib import Path

from openhab_creator import logger


class BaseCreator():
    def __init__(self, typed: str, outputdir: str, subdir: Optional[str] = None):
        self.typed: str = typed
        self.outputdir: Path = Path(outputdir)

        self.subdir: str = subdir
        if self.subdir is None:
            self.subdir = self.typed

        self.lines: List[str] = []

    def append(self, lines: str) -> None:
        self.lines.append(lines)

    def write_file(self, filename: str) -> None:
        self._create_outputdir_if_not_exists()

        with open(self.outputdir / self.subdir / f'{filename}.{self.typed}', 'w', encoding='utf-8') as f:
            f.writelines("\n".join(self.lines))

        logger.info('File %s/%s.%s written',
                    self.subdir, filename, self.typed)

        self.lines.clear()

    def _create_outputdir_if_not_exists(self) -> None:
        os.makedirs(self.outputdir / self.subdir, exist_ok=True)
