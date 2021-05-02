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
        Group(motiondetector.item_ids.motiondetector)\
            .label(_('Motiondetector {name}').format(name=motiondetector.name))\
            .location(motiondetector.location)\
            .semantic(motiondetector)\
            .append_to(self)

        Switch(motiondetector.item_ids.presence)\
            .label(_('Presence'))\
            .icon(motiondetector.category)\
            .equipment(motiondetector)\
            .semantic(PointType.STATUS, PropertyType.PRESENCE)\
            .channel(motiondetector.points.channel('presence'))\
            .append_to(self)

        Group(motiondetector.item_ids.assignment())\
            .label(_('Motiondetector assignment'))\
            .equipment(motiondetector)\
            .groups('MotionDetectorAssignment')\
            .append_to(self)
