from __future__ import annotations

from typing import Dict

from openhab_creator import CreatorEnum, _


class PollenCountIndex(CreatorEnum):
    NOT_SPECIFIED = 'not_specified', '-1', -1, _('Not specified')
    NO_POLLUTION = 'no_pollen_pollution', '0', 0, _('No pollen pollution')
    NO_TO_LOW = 'no_to_low_pollen_count', '0-1', 5, _('No to low pollen count')
    LOW = 'low_pollen_count', '1', 10, _('Low pollen count')
    LOW_TO_MEDIUM = 'low_to_medium_pollen_count', '1-2', 15, _(
        'Low to medium pollen count')
    MEDIUM = 'medium_pollen_count', '2', 20, _('Medium pollen count')
    MEDIUM_TO_HIGH = 'medium_to_high_pollen_count', '2-3', 25, _(
        'Medium to high pollen count')
    HIGH = 'high_pollen_count', '3', 30, _('High pollen count')

    def __init__(self, identifier: str, api_format: str, internal: int, label: str):
        self.identifier: str = identifier
        self.api_format: str = api_format
        self.internal: int = internal
        self.label: str = label

    @classmethod
    def mappings(cls) -> Dict[str, str]:
        return dict(map(lambda x: (x.internal, x.label), cls))

    @classmethod
    def api_mappings(cls) -> Dict[str, str]:
        return dict(map(lambda x: (x.api_format, x.internal), cls))
