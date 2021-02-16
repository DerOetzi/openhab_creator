from __future__ import annotations

from abc import abstractproperty
from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

from openhab_creator import logger
from openhab_creator.exception import (BuildException, ConfigurationException,
                                       RegistryException)
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

        self.blankname: str = name

        self.location: Optional[Location] = location

        super().__init__(*self._name_and_identifier(identifier))

        self.thing: Optional[Thing] = None if thing is None else Thing(
            equipment_node=self, configuration=configuration, secrets_config=secrets, **thing)

        self.parent: Optional[Equipment] = parent

        self.points: Dict[str, str] = {} if points is None else points

        self._init_subequipment(
            configuration, [] if subequipment is None else subequipment)

    def _name_and_identifier(self, identifier: Optional[str] = None) -> Tuple[str, Optional[str]]:

        if self.location is not None:
            name = f'{self.location.name} {self.blankname}'.strip()

            if identifier is None:
                identifier = f'{self.location.identifier}{self.blankname}'
        else:
            name = self.blankname

        return name, identifier

    def _init_subequipment(self, configuration: Configuration, subequipment: List[Dict]) -> None:
        self._subequipment: List[Equipment] = []

        for subequipment_definition in subequipment:
            name = f'{self.blankname} {subequipment_definition["name"]}'
            subequipment_definition['name'] = name.strip()
            self.subequipment.append(EquipmentFactory.new(configuration=configuration,
                                                          location=self.location,
                                                          parent=self,
                                                          **subequipment_definition))

        logger.debug(self.subequipment)

    @abstractproperty
    def item_identifiers(self) -> Dict[str, str]:
        pass

    @abstractproperty
    def name_with_type(self) -> str:
        pass

    @property
    def is_thing(self) -> bool:
        return self.thing is not None

    @property
    def is_child(self) -> bool:
        return self.parent is not None

    @property
    def has_subequipment(self) -> bool:
        return len(self.subequipment) > 0

    @property
    def subequipment(self) -> List[Equipment]:
        return self._subequipment

    def has_point(self, point: str) -> bool:
        return point in self.points

    def channel(self, point: str) -> str:
        if not (self.is_thing and self.has_point(point)):
            raise BuildException(
                f'Cannot create channel for point "{point}" for equipment {self.identifier}')

        return f'{self.thing.channelprefix}:{self.points[point]}'

    @property
    def has_battery(self) -> bool:
        return self.has_battery_level or self.has_battery_low

    @property
    def has_battery_level(self) -> bool:
        return 'battery_level' in self.points

    @property
    def has_battery_low(self) -> bool:
        return 'battery_low' in self.points

    @property
    def battery_id(self) -> str:
        return f'battery{self.semantic}{self.identifier}'

    @property
    def lowbattery_id(self) -> str:
        return f'batteryLow{self.semantic}{self.identifier}'

    @property
    def levelbattery_id(self) -> str:
        return f'batteryLevel{self.semantic}{self.identifier}'

    @property
    def influxdb_tags(self) -> Dict[str, str]:
        tags = {
            'label': self.name_with_type
        }

        return {**tags, **self.location.location_tags}


class EquipmentFactory(object):
    registry: Dict[str, Type['Equipment']] = {}

    initialized: bool = False

    @classmethod
    def _init(cls):
        if not cls.initialized:
            import_module(
                'openhab_creator.models.configuration.equipment.types')

            cls.initialized = True

    @classmethod
    def register(cls, equipment_cls: Type[Equipment]) -> None:
        cls.registry[equipment_cls.__name__.lower()] = equipment_cls

    @classmethod
    def new(cls,
            configuration: Configuration,
            **equipment_configuration: Dict) -> Equipment:
        cls._init()

        equipment_configuration = cls._merge_template(
            configuration, equipment_configuration)

        equipment_type = equipment_configuration.pop('typed').lower()

        if equipment_type not in cls.registry:
            raise RegistryException(
                f'No class for equipment type: {equipment_type}')

        equipment = cls.registry[equipment_type.lower()](configuration=configuration,
                                                         **equipment_configuration)

        if not equipment.is_child:
            configuration.add_equipment(equipment)

        return equipment

    @classmethod
    def _merge_template(cls, configuration: Configuration, equipment_configuration: Dict) -> Dict:
        template = equipment_configuration.pop('template', None)
        if template is not None:
            equipment_configuration = {
                **configuration.template(template), **equipment_configuration}

        return equipment_configuration


class EquipmentType(object):
    def __init__(self, equipment_cls: Type[Equipment]):
        def init(self, *arg, **kwargs):
            equipment_cls.__init__(self, *arg, **kwargs)

            for key, value in self.item_identifiers.items():
                self.__dict__[f'{key}_id'] = f'{value}{self.identifier}'

        wrappedclass = type(equipment_cls.__name__,
                            (equipment_cls, Equipment), {'__init__': init})

        EquipmentFactory.register(wrappedclass)
