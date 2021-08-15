from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.items import (Group, Number, NumberType, PointType,
                                          Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


@ItemsCreatorPipeline(6)
class LearningHouseItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        Group('LearningHouseTrain')\
            .append_to(self)

        for learninghouse in configuration.equipment.equipment('learninghouse'):
            Group(learninghouse.item_ids.learninghouse)\
                .label(_('LearningHouse: {name}').format(name=learninghouse.name))\
                .semantic(learninghouse)\
                .append_to(self)

            Switch(learninghouse.item_ids.dependent)\
                .label(_('Dependent variable'))\
                .icon(learninghouse.icon)\
                .equipment(learninghouse)\
                .semantic(PointType.STATUS)\
                .scripting({
                    'model_name': learninghouse.model_name,
                    'base_url': learninghouse.base_url,
                    'score_item': learninghouse.item_ids.score
                })\
                .append_to(self)

            Number(learninghouse.item_ids.score)\
                .typed(NumberType.DIMENSIONLESS)\
                .format('%.2f %%')\
                .label(_('Model score'))\
                .equipment(learninghouse)\
                .semantic(PointType.STATUS)\
                .append_to(self)

            Switch(learninghouse.item_ids.train)\
                .label(_('Prediction is'))\
                .icon('learninghouse')\
                .equipment(learninghouse)\
                .groups('LearningHouseTrain')\
                .semantic(PointType.CONTROL)\
                .scripting({
                    'model_name': learninghouse.model_name,
                    'base_url': learninghouse.base_url,
                    'dependent_item': learninghouse.item_ids.dependent,
                    'score_item': learninghouse.item_ids.score
                })\
                .append_to(self)

        self.write_file('learninghouse')
