from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import Group, PointType, PropertyType, Switch
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.motiondetector import MotionDetector


@ItemsCreatorPipeline(3)
class MotionDetectorItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('MotionDetectorAssignment')\
            .label(_('Motiondetector assignment items'))\
            .config()\
            .append_to(self)

        for motiondetector in configuration.equipment('motiondetector'):
            self._create_motiondetector_groups(motiondetector)

        self.write_file('motiondetector')

    def _create_motiondetector_groups(self, motiondetector: MotionDetector):
        Group(motiondetector.motiondetector_id)\
            .label(_('Motiondetector {name}').format(name=motiondetector.name))\
            .location(motiondetector.location)\
            .semantic(motiondetector)\
            .append_to(self)

        Switch(motiondetector.presence_id)\
            .label(_('Presence'))\
            .icon(motiondetector.category)\
            .groups(motiondetector.motiondetector_id)\
            .semantic(PointType.STATUS, PropertyType.PRESENCE)\
            .channel(motiondetector.channel('presence'))\
            .append_to(self)

        Group(motiondetector.assignment_id())\
            .label(_('Motiondetector assignment'))\
            .groups(motiondetector.motiondetector_id, 'MotionDetectorAssignment')\
            .append_to(self)

        self._create_battery(motiondetector, motiondetector.motiondetector_id)
