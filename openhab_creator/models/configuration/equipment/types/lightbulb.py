from __future__ import annotations

from typing import Optional, Dict, Final

from openhab_creator.models.configuration.equipment import Equipment, EquipmentType


@EquipmentType
class Lightbulb(Equipment):
    ITEM_IDENTIFIERS: Final[Dict[str, str]] = {
        'lightbulb': 'lightbulb',
        'lightcontrol': 'lightcontrol',
        'auto': 'autoLight',
        'autodisplay': 'autoDisplayLight',
        'autoreactivation': 'autoReactivationLight',
        'autodarkness': 'autoDarkness',
        'autoabsence': 'autoAbsenceLight',
        'motiondetectorperiod': 'motionDetectorPeriod',
        'switchingcycles': 'switchingCycles',
        'switchingcyclesreset': 'switchingCyckesReset',
        'hide': 'hideLight',
        'brightness': 'brightness',
        'colortemperature': 'colortemperatur',
        'onoff': 'onoff',
        'rgb': 'rgb',
        'nightmode': 'nightmode'
    }

    def __init__(self,
                 singlebulb: Optional[bool] = False,
                 nightmode: Optional[bool] = False,
                 **equipment_configuration: Dict):

        super().__init__(**equipment_configuration)

        self.singlebulb: bool = singlebulb
        self.nightmode: bool = nightmode

        self.has_commands = {
            'brightness': False,
            'colortemperature': False,
            'onoff': False,
            'rgb': False
        }

        for command in self.has_commands.keys():
            self.has_commands[command] = self.has_command(command)

    def has_command(self, command: str) -> bool:
        has_command = self.has_point(command)

        for subequipment in self.subequipment:
            has_command or subequipment.has_command(command)

        return has_command

    @property
    def has_brightness(self) -> bool:
        return self.has_commands['brightness']

    @property
    def has_colortemperature(self) -> bool:
        return self.has_commands['colortemperature']

    @property
    def has_onoff(self) -> bool:
        return self.has_commands['onoff']

    @property
    def has_rgb(self) -> bool:
        return self.has_commands['rgb']
