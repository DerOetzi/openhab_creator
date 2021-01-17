from __future__ import annotations
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.output.items.baseitemscreator import BaseItemsCreator


class ItemsCreatorRegistry(object):
    CREATORS_REGISTRY = []

    def __init__(self, order: int):
        self._order: int = order

    def __call__(self, cls: Type[BaseItemsCreator]) -> Type[BaseItemsCreator]:
        ItemsCreatorRegistry.CREATORS_REGISTRY.append((self._order, cls))
        return cls

    @staticmethod
    def pipeline(outputdir, configuration: SmarthomeConfiguration) -> None:
        creators = sorted(ItemsCreatorRegistry.CREATORS_REGISTRY,
                          key=lambda tup: tup[0])

        for order, creator in creators:
            print(f'Items creator {order} {creator.__name__}')
            c = creator(outputdir)
            c.build(configuration)
