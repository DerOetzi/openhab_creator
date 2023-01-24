from __future__ import annotations

from typing import Optional, Tuple, Dict, List

from openhab_creator import _, CreatorEnum, classproperty


class Scene(CreatorEnum):
    NIGHT = 'Night', _('Night'), 'special', (0, 1)
    BREAKFAST = 'Breakfast', _('Breakfast'), 'food', (5, 10)
    FORENOON = 'Forenoon', _('Forenoon'), 'normal', (8, 12)
    LUNCH = 'Lunch', _('Lunch'), 'food', (11, 14)
    AFTERNOON = 'Afternoon', _('Afternoon'), 'normal', (13, 15)
    DINNER = 'Dinner', _('Dinner'), 'food', (17, 19)
    EVENING = 'Evening', _('Evening'), 'normal', (18, 21)

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
        return f'sceneAssignment{self.identifier}'

    @property
    def timeworkingday_id(self) -> str:
        return f'sceneTimeWorkingDay{self.identifier}'

    @property
    def timeweekend_id(self) -> str:
        return f'sceneTimeWeekend{self.identifier}'

    @classproperty
    def sceneactive_id(cls) -> str:
        #pylint: disable=no-self-argument,no-self-use
        return 'autoSceneActive'

    @classproperty
    def mappings(cls) -> Dict[str, str]:
        #pylint: disable=no-self-argument
        return dict(map(lambda scene: (scene.identifier, scene.label), cls))

    @classmethod
    def switch_mappings(cls, category: str) -> List[Tuple[str, str]]:
        return map(lambda scene: (f'"{scene.identifier}"', scene.label), filter(
            lambda scene: scene.category == category, Scene))
