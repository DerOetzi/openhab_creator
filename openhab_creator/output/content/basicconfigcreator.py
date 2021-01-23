from __future__ import annotations
from typing import TYPE_CHECKING

import os
from pathlib import Path
import shutil

from openhab_creator.output.content.basecontentcreator import BaseContentCreator


class BasicConfigCreator(BaseContentCreator):
    def build(self) -> None:
        self._copy_services()
        self._copy_persistence()

    def _copy_services(self) -> None:
        self._copy_all_files_from_subdir('services')

    def _copy_persistence(self) -> None:
        self._copy_all_files_from_subdir('persistence')
