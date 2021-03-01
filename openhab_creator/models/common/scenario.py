from __future__ import annotations

from typing import Optional

from openhab_creator import _, CreatorEnum


class Scenario(CreatorEnum):
    NIGHT = 'Night', _('Night'), 0, 1
    MORNING = 'Morning', _('Morning'), 5, 10
    FORENOON = 'Forenoon', _('Forenoon'), 8, 12
    LUNCH = 'Lunch', _('Lunch'), 11, 14
    AFTERNOON = 'Afternoon', _('Afternoon'), 13, 15
    DINNER = 'Dinner', _('Dinner'), 17, 19
    EVENING = 'Evening', _('Evening'), 18, 21

    ABSENCE = 'Absence', _('Absence')
    PARTY = 'Party', _('Party')

    def __init__(self, identifier: str, label: str,
                 begin: Optional[int] = -1, end: Optional[int] = -1):
        self.identifier: str = identifier
        self.label: str = label
        self.begin: int = -1
        self.end: int = -1

    @property
    def has_time(self) -> bool:
        return self.begin > -1 and self.end > -1
