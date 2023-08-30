from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.poweroutlet import (
    PowerOutlet, PowerOutletItemIdentifiers)


class WhiteGoodItemIdentifiers(PowerOutletItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.whitegood

    @property
    def poweroutlet(self) -> str:
        return self._identifier('poweroutlet')

    @property
    def whitegood(self) -> str:
        return self._identifier('')

    @property
    def state(self) -> str:
        return self._identifier('state')

    @property
    def start(self) -> str:
        return self._identifier('start')

    @property
    def done(self) -> str:
        return self._identifier('done')

    @property
    def countdown(self) -> str:
        return self._identifier('countdown')

    def _identifier(self, prefix: str) -> str:
        type_prefix = 'whitegood'
        if isinstance(self.equipment, WashingMachine):
            type_prefix = 'washingmachine'
        elif isinstance(self.equipment, Dryer):
            type_prefix = 'dryer'
        elif isinstance(self.equipment, Dishwasher):
            type_prefix = 'dishwasher'

        return super()._identifier(f'{type_prefix}{prefix}')


@EquipmentType()
class WhiteGood(PowerOutlet):
    def __init__(self,
                 powerlimits: Optional[Dict[str, float]] = None,
                 reminder: Optional[Dict] = None,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self._item_ids: WhiteGoodItemIdentifiers = WhiteGoodItemIdentifiers(
            self)

        self.powerlimits: Dict[str, float] = powerlimits or {}
        self.reminder: Optional[Dict] = reminder

    @property
    def item_ids(self) -> WhiteGoodItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('whitegood')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("WhiteGood")
        return f'{self.name} ({typed})'

    @property
    def has_reminder(self) -> bool:
        return self.reminder is not None

    @property
    def poweroutlet_is_subequipment(self) -> bool:
        return True

    @property
    def group(self) -> str:
        return 'WhiteGood'

    @property
    def scripting(self) -> Dict:
        scripting = {}

        scripting['typed'] = self.semantic.lower()
        scripting['status_item'] = self.item_ids.state
        scripting['start_item'] = self.item_ids.start

        for key, limit in self.powerlimits.items():
            scripting[f'{key}_limit'] = limit

        if self.has_reminder:
            scripting['reminder'] = self.reminder['typed']
            scripting['reminder_cycles'] = self.reminder['cycles']
            scripting['reminder_message'] = self.reminder['message']
            scripting['countdown_item'] = self.item_ids.countdown
            scripting['done_item'] = self.item_ids.done

        return scripting


@EquipmentType()
class WashingMachine(WhiteGood):
    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('washingmachine')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Washingmachine")
        return f'{self.name} ({typed})'

    @property
    def scripting(self) -> Dict:
        scripting = super().scripting
        scripting['washingmachine_message'] = _('Washing machine is ready')
        return scripting


@EquipmentType()
class Dryer(WhiteGood):
    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('dryer')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Dryer")
        return f'{self.name} ({typed})'

    @property
    def scripting(self) -> Dict:
        scripting = super().scripting
        scripting['dryer_message'] = _('Dryer is ready')
        return scripting


@EquipmentType()
class WashingMachineDryer(WashingMachine):
    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('dryer')
        return categories

    @property
    def semantic(self) -> str:
        return 'WashingMachine'

    @property
    def scripting(self) -> Dict:
        scripting = super().scripting
        scripting['typed'] = 'washingmachine_dryer'
        scripting['dryer_message'] = _('Dryer is ready')
        scripting['washingmachine_dryer_message'] = _(
            'Washing machine and dryer are ready')
        return scripting


@EquipmentType()
class Dishwasher(WhiteGood):
    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('dishwasher')
        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("Dishwasher")
        return f'{self.name} ({typed})'

    @property
    def scripting(self) -> Dict:
        scripting = super().scripting
        scripting['dishwasher_message'] = _('Dishwasher is ready')
        return scripting
