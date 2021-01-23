from __future__ import annotations

import os
from typing import TYPE_CHECKING

import openhab_creator.output.items.creators
from openhab_creator.output.basecreator import BaseCreator
from openhab_creator.output.items.itemscreatorregistry import ItemsCreatorRegistry

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration


class ItemsCreator(object):
    def __init__(self, outputdir: str):
        self._outputdir: str = outputdir

    def build(self, configuration: SmarthomeConfiguration) -> None:
        ItemsCreatorRegistry.pipeline(self._outputdir, configuration)
