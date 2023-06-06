from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from openhab_creator import _, logger
from openhab_creator.models.common import MapTransformation
from openhab_creator.models.items import (AISensorDataType, Contact, Group,
                                          GroupType, Number, NumberType, PointType, PropertyType,
                                          String, Switch)
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

        heatings = dict((x.location, x)
                        for x in configuration.equipment.equipment('heating'))

        logger.info(heatings)

        for window in configuration.equipment.equipment('window'):
            self.__build_parent(window)

            if not self.__build_subequipment(window, heatings):
                self.__build_thing(window, heatings)

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

    def __build_subequipment(self, parent_window: Window, heatings: Dict) -> bool:
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
                self.__build_thing(subwindow, heatings)

        return parent_window.has_subequipment

    def __build_thing(self, window: Window, heatings: Dict) -> None:
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
            .scripting({
                'alarm_message': _('Alert! Window {name} was opened, while nobody at home.').format(name=window.name),
                'absence_message': _('Window {name} still open.').format(name=window.name),
                'reminder_message': _('Please close the window {name}.').format(name=window.name)
            })\
            .aisensor(AISensorDataType.CATEGORICAL)\
            .append_to(self)

        if window.remindertime:
            Number(window.item_ids.remindertime)\
                .typed(NumberType.TIME)\
                .label(_('Period window reminder'))\
                .format('%d m')\
                .icon('clock')\
                .equipment(window)\
                .semantic(PointType.SETPOINT, PropertyType.DURATION)\
                .config()\
                .append_to(self)

            Switch(window.item_ids.sendreminder)\
                .label(_("Send reminder"))\
                .equipment(window)\
                .semantic(PointType.SETPOINT)\
                .expire("2h", "ON")\
                .config()\
                .append_to(self)

            contact.scripting({
                'remindertime_item': window.item_ids.remindertime,
                'sendreminder_item': window.item_ids.sendreminder
            })

        if window.location in heatings:
            heating = heatings[window.location]
            String(heating.item_ids.heatcontrol_save)\
                .append_to(self)

            contact.scripting(
                {
                    'heating_item': heating.item_ids.heating,
                    'heating_control_save': heating.item_ids.heatcontrol_save
                })

        if window.is_child:
            contact.groups(window.parent.item_ids.windowopen)
