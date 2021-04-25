from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.models.configuration.equipment import (Equipment,
                                                            EquipmentType)


@EquipmentType()
class NetworkAppliance(Equipment):
    def __init__(self,
                 tr064: Optional[str] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self.tr064: Optional[str] = tr064

    @property
    def item_identifiers(self) -> Dict[str, str]:
        return {
            'networkappliance': 'networkappliance'
        }

    @property
    def conditional_points(self) -> List[str]:
        return []

    @property
    def categories(self) -> List[str]:
        categories = super().categories
        categories.append('networkappliance')
        if self.tr064 is not None:
            categories.append(self.tr064.lower())

        return categories

    @property
    def name_with_type(self) -> str:
        typed = _("NetworkAppliance")
        return f'{self.name} ({typed})'

    def macs(self, macs: List[str]) -> None:
        self.thing.properties['macOnline'] = '","'.join(macs)
