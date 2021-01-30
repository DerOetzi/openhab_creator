from __future__ import annotations

from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType()
class Lightbulb(Equipment):
    pass
