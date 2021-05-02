from __future__ import annotations

from abc import ABC, abstractproperty
from copy import deepcopy
from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

from openhab_creator import logger
from openhab_creator.exception import (BuildException, ConfigurationException,
                                       RegistryException)
from openhab_creator.models.configuration.baseobject import BaseObject
from openhab_creator.models.configuration.equipment.thing import Thing

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.location import Location
    from openhab_creator.models.configuration.person import Person


class EquipmentItemIdentifiers(ABC):
    def __init__(self, equipment: Equipment):
        self.equipment: Equipment = equipment

    @abstractproperty
    def equipment_id(self) -> str:
        pass

    @property
    def battery(self) -> str:
        return self._identifier(f'battery{self.equipment.semantic}')

    @property
    def lowbattery(self) -> str:
        return self._identifier(f'batteryLow{self.equipment.semantic}')

    @property
    def levelbattery(self) -> str:
        return self._identifier(f'batteryLevel{self.equipment.semantic}')

    @property
    def maconline(self) -> str:
        return self._identifier(f'maconline{self.equipment.semantic}')

    def _identifier(self, prefix: str) -> str:
        return f'{prefix}{self.equipment.identifier}'


class EquipmentPoints():
    def __init__(self, points: Dict[str, str], equipment: Equipment):
        self.points: Dict[str, str] = points
        self.equipment: Equipment = equipment

    @property
    def has_battery(self) -> bool:
        return self.has_battery_level or self.has_battery_low

    @property
    def has_battery_level(self) -> bool:
        return self.has('battery_level')

    @property
    def has_battery_low(self) -> bool:
        return self.has('battery_low')

    @property
    def has_mac(self) -> bool:
        return self.equipment.thing.has_mac

    def has(self, point: str, recursive: Optional[bool] = False) -> bool:
        has_point = point in self.points

        if recursive:
            for subequipment in self.equipment.subequipment:
                has_point = has_point or subequipment.points.has(
                    point, recursive)

        return has_point

    def channel(self, point: str) -> str:
        if not (self.equipment.is_thing and self.has(point)):
            raise BuildException(
                f'Cannot create channel for point "{point}" '
                'for equipment {self.equipment.identifier}')

        return f'{self.equipment.thing.channelprefix}:{self.points[point]}'


class Equipment(BaseObject):
    def __init__(self,
                 configuration: Configuration,
                 location: Optional[Location] = None,
                 person: Optional[Person] = None,
                 name: Optional[str] = '',
                 identifier: Optional[str] = None,
                 thing: Optional[Dict] = None,
                 subequipment: Optional[List[Dict]] = None,
                 parent: Optional[Equipment] = None,
                 secrets: Optional[List[str]] = None,
                 points: Optional[Dict[str, str]] = None):

        self.blankname: str = name

        self.location: Optional[Location] = location
        self.person: Optional[Person] = person

        super().__init__(*self._name_and_identifier(identifier))

        self.thing: Optional[Thing] = None if thing is None else Thing(
            equipment_node=self, configuration=configuration, secrets_config=secrets, **thing)

        self.parent: Optional[Equipment] = parent

        self._init_subequipment(
            configuration, [] if subequipment is None else subequipment)

        self._points: EquipmentPoints = EquipmentPoints(points or {}, self)

    def _name_and_identifier(self, identifier: Optional[str] = None) -> Tuple[str, Optional[str]]:

        if self.location is not None:
            name = f'{self.location.name} {self.blankname}'.strip()

            if identifier is None:
                identifier = f'{self.location.identifier}{self.blankname}'
        elif self.person is not None:
            name = f'{self.person.name} {self.blankname}'.strip()

            if identifier is None:
                identifier = f'{self.person.identifier}{self.blankname}'
        else:
            name = self.blankname

        return name, identifier

    def _init_subequipment(self, configuration: Configuration, subequipment: List[Dict]) -> None:
        self.subequipment: List[Equipment] = []

        for subequipment_definition in subequipment:
            name = f'{self.blankname} {subequipment_definition["name"]}'
            subequipment_definition['name'] = name.strip()
            self.subequipment.append(EquipmentType.new(configuration=configuration,
                                                       location=self.location,
                                                       parent=self,
                                                       **subequipment_definition))

        logger.debug(self.subequipment)

    @abstractproperty
    def item_ids(self) -> EquipmentItemIdentifiers:
        pass

    @property
    def points(self) -> EquipmentPoints:
        return self._points

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
    def has_location(self) -> bool:
        return self.location is not None

    @property
    def toplevel_location(self) -> Location:
        location = self.location
        while location.has_parent:
            location = location.parent

        return location

    @property
    def has_person(self) -> bool:
        return self.person is not None

    @property
    def categories(self) -> List['str']:
        categories = []
        if self.points.has_battery:
            categories.append('battery')

        return categories

    @property
    def is_timecontrolled(self) -> bool:
        return False

    @property
    def influxdb_tags(self) -> Dict[str, str]:
        tags = {
            'label': self.name_with_type
        }

        if self.has_location:
            tags = {**tags, **self.location.location_tags}

        if self.has_person:
            tags = {**tags, **self.person.person_tags}

        return tags


class EquipmentType():
    registry: Dict[str, Type['Equipment']] = {}
    templates: Dict[str, Dict] = {}

    @classmethod
    def init(cls, templates: Dict[str, Dict]):
        import_module('openhab_creator.models.configuration.equipment.types')
        cls.templates = templates

    def __call__(self, equipment_cls: Type[Equipment]):
        EquipmentType._register(equipment_cls)
        return equipment_cls

    @classmethod
    def _register(cls, equipment_cls: Type[Equipment]) -> None:
        cls.registry[equipment_cls.__name__.lower()] = equipment_cls

    @classmethod
    def new(cls,
            configuration: Configuration,
            **equipment_configuration: Dict) -> Equipment:

        equipment_configuration = cls._merge_template(equipment_configuration)

        equipment_type = equipment_configuration.pop('typed').lower()

        if equipment_type not in cls.registry:
            raise RegistryException(
                f'No class for equipment type: {equipment_type}')

        equipment = cls.registry[equipment_type.lower()](configuration=configuration,
                                                         **equipment_configuration)

        configuration.add_equipment(equipment)

        return equipment

    @classmethod
    def _merge_template(cls, equipment_configuration: Dict) -> Dict:
        template = equipment_configuration.pop('template', None)
        if template is not None:
            equipment_configuration = {
                **cls._template(template), **equipment_configuration}

        return equipment_configuration

    @classmethod
    def _template(cls, template_key: str) -> Dict:
        template_key = template_key.lower()
        if template_key not in cls.templates:
            raise ConfigurationException(
                f'No template "{template_key}" in configuration')

        return deepcopy(cls.templates[template_key])
