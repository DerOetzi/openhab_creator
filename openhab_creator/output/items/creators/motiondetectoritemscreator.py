from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.output.items.itemscreatorregistry import ItemsCreatorRegistry
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import SmarthomeConfiguration
    from openhab_creator.models.thing.types.motiondetector import MotionDetector


@ItemsCreatorRegistry(3)
class MotionDetectorItemsCreator(BaseItemsCreator):
    def build(self, configuration: SmarthomeConfiguration) -> None:
        self._create_group('MotionDetectorAssignment', _(
            'Motiondetector assignment items'), groups=['Config'])

        for motiondetector in configuration.equipment('motiondetector'):
            self._create_motiondetector_groups(motiondetector)

        self._write_file('motiondetector')

    def _create_motiondetector_groups(self, motiondetector: MotionDetector):
        self._create_group(motiondetector.motiondetector_id(),
                           _('Motiondetector {name}').format(
                               name=motiondetector.name()),
                           groups=[motiondetector.location().identifier()],
                           tags=['MotionDetector'])

        self._create_item('Switch',
                          motiondetector.presence_id(),
                          _('Presence'),
                          icon='motiondetector',
                          groups=[motiondetector.motiondetector_id()],
                          tags=['Presence'],
                          metadata={"channel": motiondetector.channel('status', 'presence')})

        self._create_group(motiondetector.assignment_id(),
                           _('Motiondetector assignment'),
                           groups=[
                               motiondetector.motiondetector_id(),
                               'MotionDetectorAssignment'])

        self._create_battery(
            motiondetector, motiondetector.motiondetector_id())
