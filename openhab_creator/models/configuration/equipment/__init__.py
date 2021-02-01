from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional, Tuple, Type

from openhab_creator import logger
from openhab_creator.exception import BuildException, ConfigurationException, RegistryException
from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment.thing import Thing

if TYPE_CHECKING:
    from openhab_creator.models.configuration.location import Location
    from openhab_creator.models.configuration import Configuration


class Equipment(BaseObject):

    def __init__(self,
                 configuration: Configuration,
                 location: Optional[Location] = None,
                 name: Optional[str] = '',
                 identifier: Optional[str] = None,
                 thing: Optional[Dict] = None,
                 subequipment: Optional[List[Dict]] = None,
                 parent: Optional[Equipment] = None,
                 secrets: Optional[List[str]] = None,
                 points: Optional[Dict[str, str]] = None):

        self.__BLANKNAME: Final[str] = name

        self.__LOCATION: Final[Optional[Location]] = location

        super().__init__(*self.__init_name_and_identifier(identifier))

        self.__THING: Final[Optional[Thing]] = None if thing is None else Thing(
            equipment_node=self, configuration=configuration, secrets_config=secrets, **thing)

        self.__PARENT: Final[Optional[Equipment]] = parent

        self.__POINTS: Final[Dict[str, str]] = {} if points is None else points

        self.__init_subequipment(
            configuration, [] if subequipment is None else subequipment)

    def __init_name_and_identifier(self, identifier: Optional[str] = None) -> Tuple[str, Optional[str]]:

        if self.location is not None:
            name = f'{self.location.name} {self.blankname}'.strip()

            if identifier is None:
                identifier = f'{self.location.identifier}{self.blankname}'
        else:
            name = self.blankname

        return name, identifier

    def __init_subequipment(self, configuration: Configuration, subequipment: List[Dict]) -> None:
        self.__SUBEQUIPMENT: Final[List[Equipment]] = []

        for subequipment_definition in subequipment:
            name = f'{self.blankname} {subequipment_definition["name"]}'
            subequipment_definition['name'] = name.strip()
            self.__SUBEQUIPMENT.append(EquipmentFactory.new(configuration=configuration,
                                                            location=self.location,
                                                            parent=self,
                                                            **subequipment_definition))

        logger.debug(self.__SUBEQUIPMENT)

    @property
    def blankname(self) -> str:
        return self.__BLANKNAME

    @property
    def location(self) -> Optional[Location]:
        return self.__LOCATION

    @property
    def thing(self) -> Optional[Thing]:
        return self.__THING

    @property
    def is_thing(self):
        return self.thing is not None

    @property
    def parent(self) -> Optional[Equipment]:
        return self.__PARENT

    @property
    def is_child(self) -> bool:
        return self.__PARENT is not None

    @property
    def points(self) -> Dict[str, str]:
        return self.__POINTS

    @property
    def subequipment(self) -> List[Equipment]:
        return self.__SUBEQUIPMENT

    def has_point(self, point: str) -> bool:
        return point in self.points

    def channel(self, point: str) -> str:
        if not (self.is_thing and self.has_point(point)):
            raise BuildException(
                f'Cannot create channel for point "{point}" for equipment {self.identifier}')

        return f'{self.thing.channelprefix}:{self.points[point]}'

    @property
    def has_battery(self) -> bool:
        return 'battery_level' in self.points or 'battery_low' in self.points


class EquipmentFactory(object):
    REGISTRY: Final[Dict[str, Type['Equipment']]] = {}

    __initialized: bool = False

    @classmethod
    def __init(cls):
        if not cls.__initialized:
            import_module(
                'openhab_creator.models.configuration.equipment.types')

            cls.__initialized = True

    @classmethod
    def register(cls, equipment_type: str, equipment_cls: Type[Equipment]) -> None:
        cls.REGISTRY[equipment_type.lower()] = equipment_cls

    @classmethod
    def new(cls,
            configuration: Configuration,
            **equipment_configuration: Dict) -> Equipment:
        cls.__init()

        equipment_configuration = cls.__merge_template(
            configuration, equipment_configuration)

        equipment_type = equipment_configuration.pop('typed').lower()

        if equipment_type not in cls.REGISTRY:
            raise RegistryException(
                f'No class for equipment type: {equipment_type}')

        equipment = cls.REGISTRY[equipment_type.lower()](configuration=configuration,
                                                         **equipment_configuration)

        if not equipment.is_child:
            configuration.add_equipment(equipment)

        return equipment

    @classmethod
    def __merge_template(cls, configuration: Configuration, equipment_configuration: Dict) -> Dict:
        template = equipment_configuration.pop('template', None)
        if template is not None:
            equipment_configuration = {
                **configuration.template(template), **equipment_configuration}

        return equipment_configuration


class EquipmentType(object):
    def __init__(self, *args):
        self.args = args

    def __call__(self, equipment_cls: Type[Location]):
        EquipmentFactory.register(equipment_cls.__name__, equipment_cls)
        return equipment_cls
