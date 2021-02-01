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

        self.__init_equipment(
            configuration, [] if equipment is None else equipment)

        self.parent = None

    def __init_equipment(self, configuration: Configuration, equipment: List[Dict]) -> None:
        self.__EQUIPMENT: Final[List[Equipment]] = []

        for equipment_definition in equipment:
            self.__EQUIPMENT.append(EquipmentFactory.new(configuration=configuration,
                                                         location=self,
                                                         **equipment_definition))

    @abstractproperty
    def area(self) -> str:
        pass

    @abstractproperty
    def typed(self) -> str:
        pass

    @property
    def equipment(self) -> List[Equipment]:
        return self.__EQUIPMENT

    @property
    def parent(self) -> Optional[Location]:
        return self.__parent

    @parent.setter
    def parent(self, parent: Optional[Location] = None):
        self.__parent = parent

    @property
    def has_parent(self) -> bool:
        return self.__parent is not None

    @property
    def location_tags(self) -> Dict[str, str]:
        tags = {'area': self.area, self.typed: self.name}

        if self.has_parent:
            tags = {**tags, **self.parent.location_tags}

        return tags


class LocationFactory(object):
    REGISTRY: Final[Dict[str, Type['Location']]] = {}

    __initialized: bool = False

    @classmethod
    def __init(cls):
        if not cls.__initialized:
            import_module(
                'openhab_creator.models.configuration.location.indoor')
            import_module(
                'openhab_creator.models.configuration.location.indoor.floors')
            import_module(
                'openhab_creator.models.configuration.location.indoor.rooms')

            cls.__initialized = True

    @classmethod
    def register(cls, location_type: str, location_cls: Type[Location]) -> None:
        cls.REGISTRY[location_type.lower()] = location_cls

    @classmethod
    def new(cls, configuration: Configuration, **args: Dict) -> Location:
        cls.__init()

        location_type = args.pop('typed').lower()
        if location_type in cls.REGISTRY:
            return cls.REGISTRY[location_type.lower()](configuration=configuration, **args)

        raise RegistryException(f'No class for location type: {location_type}')


class LocationType(object):
    def __init__(self, *args):
        self.args = args

    def __call__(self, location_cls: Type[Location]):
        LocationFactory.register(location_cls.__name__, location_cls)
        return location_cls
