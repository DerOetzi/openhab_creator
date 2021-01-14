from __future__ import annotations

from typing import Dict, List

import json

from openhab_creator.models.location import Location
from openhab_creator.models.location.floor import Floor
from openhab_creator.models.thing.bridge import Bridge
from openhab_creator.models.thing.equipment import Equipment

from openhab_creator.models.thing.equipment.lightbulb import Lightbulb


class SmarthomeConfiguration(object):
    EQUIPMENT_CLASSES = {
        'lightbulb': Lightbulb,
        'sensor': Equipment
    }

    def __init__(self, bridges: Dict, templates: Dict, locations: Dict):
        self.__bridges: Dict[str, Bridge] = {}
        self.__templates: Dict[str, Dict] = templates
        self.__locations: Dict[str, List[Location]] = {}
        self.__equipment: Dict[str, List[Equipment]] = {}

        self.__init_bridges(bridges)
        self.__init_locations(locations)

    def __init_bridges(self, bridges: Dict) -> None:
        for bridge_key, bridge_configuration in bridges.items():
            self.__bridges[bridge_key] = Bridge(**bridge_configuration)

    def __init_locations(self, locations: Dict) -> None:
        if 'indoor' in locations:
            self.__locations['floors'] = []
            for floor in locations['indoor']['floors']:
                self.__locations['floors'].append(
                    Floor(configuration=self, **floor))

    def bridges(self) -> Dict[str, Bridge]:
        return self.__bridges

    def bridge(self, bridge_key: str) -> Bridge:
        return self.__bridges[bridge_key]

    def floors(self) -> List[Floor]:
        return self.__locations['floors']

    def lightbulbs(self) -> List[Lightbulb]:
        return self.__equipment['lightbulb']

    def equipment_factory(self, equipment_configuration: Dict, location: Location) -> Equipment:
        equipment_configuration = self.__merge_template(
            equipment_configuration)
        typed = equipment_configuration['typed']

        equipment = SmarthomeConfiguration.EQUIPMENT_CLASSES[typed](configuration=self,
                                                                    location=location,
                                                                    **equipment_configuration)

        if typed not in self.__equipment:
            self.__equipment[typed] = []

        self.__equipment[typed].append(equipment)

        return equipment

    def __merge_template(self, equipment: Dict) -> Dict:
        template = equipment.pop('template', None)
        if template is not None:
            equipment = {**self.__templates[template], **equipment}

        if 'equipment' in equipment:
            subequipment_new = []
            for subequipment in equipment['equipment']:
                subequipment_new.append(self.__merge_template(subequipment))
            equipment['equipment'] = subequipment_new

        return equipment
