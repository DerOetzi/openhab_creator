from __future__ import annotations

from openhab_creator.exception import BuildException

from openhab_creator.models.equipment import Equipment


class Sensor(Equipment):
    def __init__(self, equipment: Equipment):
        if "sensor" != equipment.typed():
            raise BuildException(
                "Tried to parse not sensor Equipment to sensor")

        self._cast(equipment, Sensor)
