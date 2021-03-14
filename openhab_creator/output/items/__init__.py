from __future__ import annotations

import os
from importlib import import_module
from typing import TYPE_CHECKING, List, Type, Dict, Union

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
    pipeline: List[Dict[str, Union[int, Type[BaseItemsCreator]]]] = []
    initialized: bool = False

    def __init__(self, order_id: int):
        self.order_id: int = order_id

    def __call__(self, itemscreator_cls: Type[BaseItemsCreator]):
        ItemsCreatorPipeline.pipeline.insert(self.order_id, {
            'order': self.order_id,
            'class': itemscreator_cls
        })

    @classmethod
    def _init(cls):
        if not cls.initialized:
            import_module(
                'openhab_creator.output.items.creators')

            cls.initialized = True

    @classmethod
    def build(cls, outputdir: str, configuration: Configuration) -> None:
        cls._init()

        for creator in sorted(cls.pipeline, key=lambda x: x['order']):
            logger.info(
                f'Item creator: {creator["class"].__name__} ({creator["order"]})')
            c = creator['class'](outputdir)
            c.build(configuration)
