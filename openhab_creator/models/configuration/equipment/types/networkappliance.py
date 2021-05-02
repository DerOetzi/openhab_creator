from __future__ import annotations

from typing import Dict, List, Optional

from openhab_creator import _
from openhab_creator.exception import BuildException
from openhab_creator.models.configuration.equipment import (
    Equipment, EquipmentItemIdentifiers, EquipmentType)


class NetworkApplianceItemIdentifiers(EquipmentItemIdentifiers):
    @property
    def equipment_id(self) -> str:
        return self.networkappliance

    @property
    def networkappliance(self) -> str:
        return self._identifier('networkappliance')


@EquipmentType()
class NetworkAppliance(Equipment):
    def __init__(self,
                 tr064: Optional[str] = None,
                 **equipment_configuration: Dict):
        super().__init__(**equipment_configuration)

        self._item_ids = NetworkApplianceItemIdentifiers(self)

        self.tr064: Optional[str] = tr064
        self.macs: Optional[Dict[str, Equipment]] = {}

    @property
    def item_ids(self) -> NetworkApplianceItemIdentifiers:
        return self._item_ids

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

    def register_macs(self, macs: Dict[str, Equipment]) -> None:
        self.macs = macs
        self.thing.properties['macOnline'] = '","'.join(macs.keys())

    def maconline_channel(self, mac: str) -> str:
        if not (self.is_thing and mac in self.macs):
            raise BuildException(
                f'Cannot create channel for mac address "{mac}" for equipment {self.identifier}')

        mac = mac.replace(':', '_3A')

        return f'{self.thing.channelprefix}:macOnline_{mac}'
