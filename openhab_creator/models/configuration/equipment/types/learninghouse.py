from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class LearningHouseItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.learninghouse

    @property
    def learninghouse(self) -> str:
        return self._identifier('learningHouse')

    @property
    def dependent(self) -> str:
        return self.equipment.identifier.lower()

    @property
    def score(self) -> str:
        return self._identifier('learningHouseScore')

    @property
    def train(self) -> str:
        return self._identifier('learningHouseTrain')


@EquipmentType()
class LearningHouse(Equipment):
    def __init__(self,
                 model_name: str,
                 configuration: Configuration,
                 icon: Optional[str] = 'learninghouse',
                 **equipment_configuration: Dict):
        super().__init__(configuration=configuration, **equipment_configuration)

        self._item_ids: LearningHouseItemIdentifiers = LearningHouseItemIdentifiers(
            self)

        self.model_name: str = model_name
        self.base_url: str = configuration.secrets.secret(
            'learninghouse', model_name, 'baseurl')
        self.icon = icon

    @property
    def map_transformation(self) -> Dict:
        map_key = self.identifier.upper()

        return MapTransformation.__members__[map_key]

    @property
    def item_ids(self) -> LearningHouseItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('learninghouse')
        return categories

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def name_with_type(self) -> str:
        typed = _("Learning House")
        return f'{self.name} ({typed})'
