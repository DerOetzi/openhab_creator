from __future__ import annotations

from typing import TYPE_CHECKING

from openhab_creator import _
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (AISensorDataType, Contact, Group,
                                          GroupType, PointType, PropertyType)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.window import \
        Window


@ItemsCreatorPipeline(4)
class WindowItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        self.__build_general_groups()

        for window in configuration.equipment.equipment('window'):
            window_item = self.__build_parent(window)

            if not self.__build_subequipment(window, window_item):
                self.__build_thing(window)

        self.write_file('window')

    def __build_general_groups(self) -> None:
        Group('windows')\
            .typed(GroupType.OPENCLOSED)\
            .label(_('Windows'))\
            .map(MapTransformation.WINDOWOPEN)\
            .icon('window')\
            .append_to(self)

    def __build_parent(self, window: Window) -> Group:
        window_item = Group(window.item_ids.window)\
            .label(_('Window {blankname}').format(blankname=window.blankname))\
            .icon('window')\
            .location(window.location)\
            .semantic(window)\
            .append_to(self)

        return window_item

    def __build_subequipment(self, parent_window: Window, parent_window_item: Group) -> bool:
        if parent_window.has_subequipment:
            Group(parent_window.item_ids.windowopen)\
                .typed(GroupType.OPENCLOSED)\
                .label(_('Window'))\
                .map(MapTransformation.WINDOWOPEN)\
                .icon('window')\
                .equipment(parent_window)\
                .semantic(PointType.OPENSTATE, PropertyType.OPENING)\
                .append_to(self)

            for subwindow in parent_window.subequipment:
                self.__build_thing(subwindow)

        return parent_window.has_subequipment

    def __build_thing(self, window: Window) -> None:
        if window.is_child:
            Group(window.item_ids.window)\
                .label(_('Window {name}').format(name=window.name))\
                .icon('window')\
                .equipment(window.parent)\
                .semantic(window)\
                .append_to(self)

        contact = Contact(window.item_ids.windowopen)\
            .label(_('Window'))\
            .map(MapTransformation.WINDOWOPEN)\
            .icon('window')\
            .equipment(window)\
            .groups('windows')\
            .semantic(PointType.OPENSTATE, PropertyType.OPENING)\
            .channel(window.points.channel('open'))\
            .sensor('window', window.influxdb_tags)\
            .aisensor(AISensorDataType.CATEGORICAL)\
            .append_to(self)

        if window.is_child:
            contact.groups(window.parent.item_ids.windowopen)
