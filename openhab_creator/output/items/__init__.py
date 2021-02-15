from __future__ import annotations

import os
from importlib import import_module
from typing import TYPE_CHECKING, List, Type

from openhab_creator import logger

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.output.items.baseitemscreator import BaseItemsCreator


class ItemsCreator(object):
    def __init__(self, outputdir: str):
        self.outputdir: str = outputdir

    def build(self, configuration: Configuration) -> None:
        ItemsCreatorPipeline.build(self.outputdir, configuration)


class ItemsCreatorPipeline(object):
    pipeline: List[BaseItemsCreator] = []
    initialized: bool = False

    def __init__(self, order_id: int):
        self.order_id = order_id

    def __call__(self, itemscreator_cls: Type[BaseItemsCreator]):
        print(itemscreator_cls)
        ItemsCreatorPipeline.pipeline.insert(self.order_id, itemscreator_cls)

    @classmethod
    def _init(cls):
        if not cls.initialized:
            import_module(
                'openhab_creator.output.items.creators')

            cls.initialized = True

    @classmethod
    def build(cls, outputdir: str, configuration: Configuration) -> None:
        cls._init()

        for creator in cls.pipeline:
            logger.info(f'Item creator: {creator.__name__}')
            c = creator(outputdir)
            c.build(configuration)
