from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class SmartMeterItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.smartmeter

    @property
    def smartmeter(self) -> str:
        return self._identifier('smartmeter')

    @property
    def consumed_total(self) -> str:
        return self._identifier('smartMeterConsumedTotal')

    def consumed(self, tariff: int) -> str:
        return self._identifier(f'smartMeterConsumedT{tariff}')

    @property
    def delivered_total(self) -> str:
        return self._identifier('smartMeterDeliveredTotal')

    @property
    def power_total(self) -> str:
        return self._identifier('smartMeterPowerTotal')

    def power(self, phase: int) -> str:
        return self._identifier(f'smartMeterPowerP{phase}')


class SmartMeterPoints(EquipmentPoints):
    @property
    def has_consumed_total(self) -> bool:
        return self.has('consumed_total')

    def has_consumed(self, tariff: int) -> bool:
        return self.has(f'consumed_t{tariff}')

    @property
    def has_consumed_tariff(self) -> bool:
        for tariff in range(1, 3):
            if self.has_consumed(tariff):
                return True

        return False

    @property
    def has_delivered_total(self) -> bool:
        return self.has('delivered_total')

    @property
    def has_power_total(self) -> bool:
        return self.has('power_total')

    def has_power(self, phase: int) -> bool:
        return self.has(f'power_p{phase}')

    @property
    def has_power_phase(self) -> bool:
        for phase in range(1, 3):
            if self.has_power(phase):
                return True

        return False


@EquipmentType()
class SmartMeter(Equipment):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: SmartMeterItemIdentifiers = SmartMeterItemIdentifiers(
            self)

        self._points: SmartMeterPoints = SmartMeterPoints(points or {}, self)

    @property
    def item_ids(self) -> SmartMeterItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> SmartMeterPoints:
        return self._points

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('smartmeter')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Smartmeter")
        return f'{self.name} ({typed})'
