from __future__ import annotations

from typing import Dict, List

from openhab_creator import _
from openhab_creator.models.configuration.equipment import EquipmentType
from openhab_creator.models.configuration.equipment.types.poweroutlet import (
    PowerOutlet, PowerOutletItemIdentifiers)


class MachineItemIdentifiers(PowerOutletItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.machine

    @property
    def poweroutlet(self) -> str:
        return self._identifier('poweroutlet')

    @property
    def machine(self) -> str:
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
        type_prefix = 'machine'
        if self.equipment.is_washingmachine:
            type_prefix = Machine.WASHINGMACHINE
        elif self.equipment.is_dryer:
            type_prefix = Machine.DRYER
        elif self.equipment.is_dishwasher:
            type_prefix = Machine.DISHWASHER

        return super()._identifier(f'{type_prefix}{prefix}')


@EquipmentType()
class Machine(PowerOutlet):
    WASHINGMACHINE = 'washingmachine'
    DRYER = 'dryer'
    DISHWASHER = 'dishwasher'

    def __init__(self,
                 machine: Dict[str, bool],
                 powerlimits: Dict[str, float],
                 reminder: Dict,
                 **equipment_configuration: Dict):

        self.machine: Dict[str, bool] = machine
        super().__init__(**equipment_configuration)

        self._item_ids: MachineItemIdentifiers = MachineItemIdentifiers(
            self)
        self.powerlimits: Dict[str, float] = powerlimits
        self.reminder: Dict = reminder

    @property
    def item_ids(self) -> MachineItemIdentifiers:
        return self._item_ids

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('machine')
        if self.is_washingmachine:
            categories.append(self.WASHINGMACHINE)
        elif self.is_dryer:
            categories.append(self.DRYER)
        elif self.is_dishwasher:
            categories.append(self.DISHWASHER)
        return categories

    @property
    def semantic(self) -> str:
        semantic = 'Equipment'
        if self.is_washingmachine:
            semantic = 'WashingMachine'
        elif self.is_dryer:
            semantic = 'Dryer'
        elif self.is_dishwasher:
            semantic = 'DishWasher'

        return semantic

    @property
    def name_with_type(self) -> str:
        typed = _("Machine")
        if self.is_washingmachine:
            typed = _('Washingmachine')
        elif self.is_dryer:
            typed = _('Dryer')
        elif self.is_dishwasher:
            typed = _('Dishwasher')
        return f'{self.name} ({typed})'

    @property
    def is_washingmachine(self) -> bool:
        return self.WASHINGMACHINE in self.machine and self.machine[self.WASHINGMACHINE]

    @property
    def is_dryer(self) -> bool:
        return self.DRYER in self.machine and self.machine[self.DRYER]

    @property
    def is_dishwasher(self) -> bool:
        return self.DISHWASHER in self.machine and self.machine[self.DISHWASHER]

    @property
    def has_reminder(self) -> bool:
        return self.reminder is not None

    @property
    def poweroutlet_is_subequipment(self) -> bool:
        return True
