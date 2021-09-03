from __future__ import annotations

from typing import Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.poweroutlet import (
    PowerOutlet, PowerOutletItemIdentifiers)


class WarmWaterPumpItemIdentifiers(PowerOutletItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.warmwaterpump

    @property
    def poweroutlet(self) -> str:
        return self._identifier('poweroutlet')

    @property
    def warmwaterpump(self) -> str:
        return self._identifier('warmwaterpump')

    @property
    def auto(self) -> str:
        return self._identifier('autoWarmWaterPump')

    @property
    def autoreactivation(self) -> str:
        return self._identifier('autoReactivationWarmWaterPump')


@EquipmentType()
class WarmWaterPump(PowerOutlet):
    def __init__(self, **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self._item_ids: WarmWaterPumpItemIdentifiers = WarmWaterPumpItemIdentifiers(
            self)

    @property
    def item_ids(self) -> WarmWaterPumpItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('pump')
        categories.append('warmwaterpump')
        return categories

    @property
    def is_timecontrolled(self) -> bool:
        return True

    @property
    def name_with_type(self) -> str:
        typed = _("Pump")
        return f'{self.name} ({typed})'

    @property
    def semantic(self) -> str:
        return 'Pump'

    @property
    def poweroutlet_is_subequipment(self) -> bool:
        return True

    @property
    def group(self) -> str:
        return 'WarmWaterPumpControl'

    @property
    def onoff_group(self) -> str | None:
        return 'WarmWaterPumpControl'

    @property
    def scripting(self) -> Dict:
        return {
            'pump_item': self.item_ids.warmwaterpump,
            'auto_item': self.item_ids.auto
        }
