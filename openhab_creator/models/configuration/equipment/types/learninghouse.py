from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _
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


@EquipmentType()
class LearningHouse(Equipment):
    def __init__(self,
                 model_name: str,
                 configuration: Configuration,
                 **equipment_configuration: Dict):
        super().__init__(configuration=configuration, **equipment_configuration)

        self._item_ids: LearningHouseItemIdentifiers = LearningHouseItemIdentifiers(
            self)

        self.model_name: str = model_name
        self.base_url: str = configuration.secrets.secret(
            'learninghouse', model_name, 'baseurl')

    @property
    def item_ids(self) -> LearningHouseItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('learninghouse')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Learning House")
        return f'{self.name} ({typed})'
