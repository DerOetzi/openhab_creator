from __future__ import annotations

from abc import abstractproperty
from importlib import import_module
from typing import TYPE_CHECKING, Dict, Final, List, Optional, Type

from openhab_creator.exception import RegistryException
from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment import EquipmentFactory

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment import Equipment


class Location(BaseObject):
    def __init__(self,
                 configuration: Configuration,
                 name: str,
                 identifier: Optional[str] = None,
                 equipment: Optional[List[Dict]] = None):
        super().__init__(name, identifier)

        self._init_equipment(
            configuration, [] if equipment is None else equipment)

        self.parent = None

    def _init_equipment(self, configuration: Configuration, equipment: List[Dict]) -> None:
        self.equipment: List[Equipment] = []

        for equipment_definition in equipment:
            self.equipment.append(EquipmentFactory.new(configuration=configuration,
                                                       location=self,
                                                       **equipment_definition))

    @abstractproperty
    def area(self) -> str:
        pass

    @abstractproperty
    def typed(self) -> str:
        pass

    @property
    def has_parent(self) -> bool:
        return self.parent is not None

    @property
    def location_tags(self) -> Dict[str, str]:
        tags = {'area': self.area, self.typed.lower(): self.name}

        if self.has_parent:
            tags = {**tags, **self.parent.location_tags}

        return tags

    @property
    def autoactive_id(self) -> str:
        return f'autoActive{self.identifier}'

    @property
    def autoguest_id(self) -> str:
        return f'autoGuest{self.identifier}'


class LocationFactory(object):
    registry: Dict[str, Type['Location']] = {}

    initialized: bool = False

    @classmethod
    def _init(cls):
        if not cls.initialized:
            import_module(
                'openhab_creator.models.configuration.location.indoor')
            import_module(
                'openhab_creator.models.configuration.location.indoor.floors')
            import_module(
                'openhab_creator.models.configuration.location.indoor.rooms')

            cls.initialized = True

    @classmethod
    def register(cls, location_cls: Type[Location]) -> None:
        cls.registry[location_cls.__name__.lower()] = location_cls

    @classmethod
    def new(cls, configuration: Configuration, **args: Dict) -> Location:
        cls._init()

        location_type = args.pop('typed').lower()
        if location_type in cls.registry:
            return cls.registry[location_type.lower()](configuration=configuration, **args)

        raise RegistryException(f'No class for location type: {location_type}')


class LocationType(object):
    def __init__(self, *args):
        self.args = args

    def __call__(self, location_cls: Type[Location]):
        LocationFactory.register(location_cls)
        return location_cls
