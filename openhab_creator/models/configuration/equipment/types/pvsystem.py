from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentPoints, EquipmentType)


class PVSystemItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.pvsystem

    @property
    def pvsystem(self) -> str:
        return self._identifier('pvsystem')
    
    @property
    def inverter(self) -> str:
        return self._identifier('inverter')
    
    @property
    def energy_produced(self) -> str:
        return self._identifier('energyProduced')
    
    @property
    def power_inverter_consumption(self) -> str:
        return self._identifier('powerInverterConsumption')
    
    @property
    def power_inverter_production(self) -> str:
        return self._identifier('powerInverterProduction')

    @property
    def pv_panels(self) -> str:
        return self._identifier('pvPanels')
    
    @property
    def energy_pv_today(self) -> str:
        return self._identifier('energyPvToday')
    
    @property
    def power_pv(self) -> str:
        return self._identifier('powerPv')
    
    @property
    def pv_grid(self) -> str:
        return self._identifier('pvGrid')
    
    @property
    def pv_battery(self) -> str:
        return self._identifier('pvBattery')


class PVSystemPoints(EquipmentPoints):
    @property
    def has_power_pv(self) -> bool:
        return self.has('power_pv')
    
    @property
    def has_energy_pv_today(self) -> bool:
        return self.has('energy_pv_today')
    
    @property
    def has_energy_produced(self) -> bool:
        return self.has('energy_produced')
    
    @property
    def has_power_inverter_consumption(self) -> bool:
        return self.has('power_inverter_consumption')
    
    @property
    def has_power_inverter_production(self) -> bool:
        return self.has('power_inverter_production')
    
    @property
    def has_battery_soc(self) -> bool:
        return self.has('battery_soc')


@EquipmentType()
class PVSystem(Equipment):
    def __init__(self,
                 points: Optional[Dict[str, str]] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids: PVSystemItemIdentifiers = PVSystemItemIdentifiers(
            self)

        self._points: PVSystemPoints = PVSystemPoints(points or {}, self)

    @property
    def item_ids(self) -> PVSystemItemIdentifiers:
        return self._item_ids

    @property
    def points(self) -> PVSystemPoints:
        return self._points

    @property
    def semantic(self) -> str:
        return 'Equipment'

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('pvsystem')

        if self.points.has_battery_soc:
            categories.append('pvbattery')

        return categories
    
    @property
    def has_battery(self) -> bool:
        return self.points.has_battery_soc

    @property
    def name_with_type(self) -> str:
        typed = _("PV System")
        return f'{self.name} ({typed})'
