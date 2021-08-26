from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import Scene
from openhab_creator.models.items import (Group, GroupType, Number, NumberType, String,
                                          Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(1)
class SceneItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('sceneTimeConfiguration')\
            .append_to(self)

        Switch('autoScene')\
            .label(_('Time controlled'))\
            .icon('auto')\
            .expire('1h', 'ON')\
            .append_to(self)

        String(Scene.sceneactive_id)\
            .label(_('Scene'))\
            .icon('scene')\
            .auto()\
            .append_to(self)

        Switch('autoGuestStayed')\
            .label(_('Guest stayed'))\
            .icon('guest')\
            .auto()\
            .append_to(self)

        for scene in Scene:
            Group(scene.assignment_id)\
                .typed(GroupType.ONOFF)\
                .auto()\
                .append_to(self)

            if scene.has_time:
                Number(scene.timeworkingday_id)\
                    .typed(NumberType.TIME)\
                    .label(scene.label)\
                    .format('%d h')\
                    .icon('clock')\
                    .auto()\
                    .groups('sceneTimeConfiguration')\
                    .append_to(self)

                Number(scene.timeweekend_id)\
                    .typed(NumberType.TIME)\
                    .label(scene.label)\
                    .format('%d h')\
                    .icon('clock')\
                    .auto()\
                    .groups('sceneTimeConfiguration')\
                    .append_to(self)

        self.write_file('scene')
