from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from openhab_creator import _
from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class BaseItemsCreator(BaseCreator):
    def __init__(self, outputdir: str):
        super().__init__('items', outputdir)

    def build(self, configuration: Configuration) -> None:
        raise NotImplementedError("Must override build")
