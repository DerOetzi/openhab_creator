from __future__ import annotations

from typing import Dict

from openhab_creator import _, CreatorEnum, classproperty


class Presence(CreatorEnum):
    AT_HOME = 'ON', '1', 'CLOSED', _('At home')
    NOT_AT_HOME = 'OFF', '0', 'OPEN', _('Not at home')

    def __init__(self, switch: str, numbered: str, contact: str, label: str):
        self.switch: str = switch
        self.numbered: str = numbered
        self.contact: str = contact
        self.label: str = label

    @classproperty
    def mappings(self) -> Dict[str, str]:
        return {**Presence.switch_mappings, **Presence.numbered_mappings, **Presence.contact_mappings}

    @classproperty
    def switch_mappings(self) -> Dict[str, str]:
        return dict(map(lambda presence: (presence.switch, presence.label), Presence))

    @classproperty
    def numbered_mappings(self) -> Dict[str, str]:
        return dict(map(lambda presence: (presence.numbered, presence.label), Presence))

    @ classproperty
    def contact_mappings(self) -> Dict[str, str]:
        return dict(map(lambda presence: (presence.contact, presence.label), Presence))
