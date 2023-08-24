from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)

if TYPE_CHECKING:
    from openhab_creator.models.configuration.equipment.types.lightbulb import \
        Lightbulb


class SmartMeterItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.smartmeter

    @property
    def smartmeter(self) -> str:
        return self._identifier('smartmeter')


@EquipmentType()
class SmartMeter(Equipment):
    def __init__(self,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: SmartMeterItemIdentifiers = SmartMeterItemIdentifiers(
            self)

    @property
    def item_ids(self) -> SmartMeterItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('smartmeter')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Smartmeter")
        return f'{self.name} ({typed})'
