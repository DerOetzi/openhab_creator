from __future__ import annotations

from typing import Optional, Tuple

from openhab_creator import _, CreatorEnum


class Scenario(CreatorEnum):
    NIGHT = 'Night', _('Night'), 'normal', (0, 1)
    MORNING = 'Morning', _('Morning'), 'normal', (5, 10)
    FORENOON = 'Forenoon', _('Forenoon'), 'normal', (8, 12)
    LUNCH = 'Lunch', _('Lunch'), 'eating', (11, 14)
    AFTERNOON = 'Afternoon', _('Afternoon'), 'normal', (13, 15)
    DINNER = 'Dinner', _('Dinner'), 'eating', (17, 19)
    EVENING = 'Evening', _('Evening'), 'normal', (18, 21)

    ABSENCE = 'Absence', _('Absence'), 'special'
    PARTY = 'Party', _('Party'), 'special'

    def __init__(self, identifier: str, label: str,
                 category: str,
                 time_limits: Optional[Tuple[int, int]] = None):
        self.identifier: str = identifier
        self.label: str = label
        self.category: str = category

        self.begin: Optional[int] = None
        self.end: Optional[int] = None

        if time_limits is not None:
            self.begin: int = time_limits[0]
            self.end: int = time_limits[1]

    @property
    def has_time(self) -> bool:
        return self.begin is not None

    @property
    def icon(self) -> str:
        return self.identifier.lower()

    @property
    def assignment_id(self) -> str:
        return f'scenarioAssignment{self.identifier}'

    @property
    def timeworkingday_id(self) -> str:
        return f'scenarioTimeWorkingDay{self.identifier}'

    @property
    def timeweekend_id(self) -> str:
        return f'scenarioTimeWeekend{self.identifier}'

    @staticmethod
    def scenarioactive_id() -> str:
        return 'autoScenarioActive'
