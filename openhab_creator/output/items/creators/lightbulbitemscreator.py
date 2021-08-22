from __future__ import annotations

from typing import TYPE_CHECKING, List

from openhab_creator import _
from openhab_creator.models.items import (Color, Dimmer, Group, GroupType,
                                          Number, NumberType, PointType,
                                          PropertyType, String, Switch)
from openhab_creator.output.items import ItemsCreatorPipeline
from openhab_creator.output.items.baseitemscreator import BaseItemsCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration
    from openhab_creator.models.configuration.equipment.types.lightbulb import Lightbulb
    from openhab_creator.models.configuration.equipment.types.motiondetector import MotionDetector
    from openhab_creator.models.configuration.equipment.types.wallswitch import WallSwitch


@ItemsCreatorPipeline(4)
class LightbulbItemsCreator(BaseItemsCreator):
    def build(self, configuration: Configuration) -> None:
        self.__build_general_groups()

        for lightbulb in configuration.equipment.equipment('lightbulb'):
            lightbulb_item = self.__build_parent(lightbulb)

            if not self.__build_subequipment(lightbulb, lightbulb_item):
                self.__build_thing(lightbulb, lightbulb_item)

        self.write_file('lightbulb')

        for lightbulb in configuration.equipment.equipment('lightbulb'):
            if configuration.equipment.has('wallswitch'):
                self.__build_buttons_assignment(
                    lightbulb, configuration.equipment.equipment('wallswitch'))

        self.write_file('lightbulb_wallswitch')

        for lightbulb in configuration.equipment.equipment('lightbulb'):
            if configuration.equipment.has('motiondetector'):
                self.__build_motion_assignment(
                    lightbulb, configuration.equipment.equipment('motiondetector'))

        self.write_file('lightbulb_motiondetector')

    def __build_general_groups(self) -> None:
        Group('Lightcontrol')\
            .label(_('Lightcontrol items'))\
            .config()\
            .append_to(self)

        Group('Nightmode')\
            .label(_('Nightmode configuration items'))\
            .config()\
            .append_to(self)

        Group('AutoLight')\
            .label(_('Scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('AutoReactivationLight')\
            .label(_('Reactivation scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('AutoAbsenceLight')\
            .label(_('Absence scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('AutoDarkness')\
            .label(_('Darkness scene controlled configuration items'))\
            .auto()\
            .append_to(self)

        Group('MotionDetectorPeriod')\
            .label(_('Motiondetector period configuration items'))\
            .config()\
            .append_to(self)

        Group('SwitchingCycles')\
            .typed(GroupType.NUMBER_AVG)\
            .label(_('Lights switching cycles'))\
            .format('%d')\
            .icon('switchingcycles')\
            .append_to(self)

        Group('SwitchingCyclesReset')\
            .label(_('Switching cycles reset'))\
            .append_to(self)

    def __build_parent(self, lightbulb: Lightbulb) -> Group:
        lightbulb_item = Group(lightbulb.item_ids.lightbulb)\
            .label(_('Lightbulb {blankname}').format(blankname=lightbulb.blankname))\
            .icon('light')\
            .location(lightbulb.location)\
            .semantic(lightbulb)\
            .scripting({
                'control_item': lightbulb.item_ids.lightcontrol
            })\
            .append_to(self)

        String(lightbulb.item_ids.lightcontrol)\
            .label(_('Lightcontrol'))\
            .icon('lightcontrol')\
            .equipment(lightbulb)\
            .groups('Lightcontrol')\
            .semantic(PointType.CONTROL)\
            .scripting({'lightbulb_item': lightbulb.item_ids.lightbulb})\
            .append_to(self)

        Switch(lightbulb.item_ids.hide)\
            .label(_('Hide on lights page'))\
            .icon('hide')\
            .config()\
            .equipment(lightbulb)\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(lightbulb.item_ids.auto)\
            .label(_('Scene controlled'))\
            .icon('auto')\
            .equipment(lightbulb)\
            .groups('AutoLight')\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(lightbulb.item_ids.autodisplay)\
            .label(_('Display scene controlled'))\
            .equipment(lightbulb)\
            .semantic(PointType.STATUS)\
            .append_to(self)

        Number(lightbulb.item_ids.autoreactivation)\
            .label(_('Reactivate scene controlled'))\
            .icon('reactivation')\
            .equipment(lightbulb)\
            .groups('AutoReactivationLight')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Switch(lightbulb.item_ids.autodarkness)\
            .label(_('In the dark'))\
            .icon('darkness')\
            .equipment(lightbulb)\
            .groups('AutoDarkness')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Switch(lightbulb.item_ids.autoabsence)\
            .label(_('Even in absence'))\
            .icon('absence')\
            .equipment(lightbulb)\
            .groups('AutoAbsenceLight')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Number(lightbulb.item_ids.motiondetectorperiod)\
            .typed(NumberType.TIME)\
            .label(_('Motiondetector period'))\
            .format('%d s')\
            .icon('timeout')\
            .equipment(lightbulb)\
            .groups('MotionDetectorPeriod')\
            .semantic(PointType.SETPOINT, PropertyType.DURATION)\
            .append_to(self)

        if lightbulb.nightmode:
            String(lightbulb.item_ids.nightmode)\
                .label(_('Nightmode configuration'))\
                .icon('configuration')\
                .equipment(lightbulb)\
                .groups('Nightmode')\
                .semantic(PointType.SETPOINT)\
                .append_to(self)

            lightbulb_item.scripting({
                'nightmode_item': lightbulb.item_ids.nightmode
            })

        return lightbulb_item

    def __build_subequipment(self, parent_lightbulb: Lightbulb, parent_lightbulb_item: Group) -> bool:
        if parent_lightbulb.has_subequipment:
            if parent_lightbulb.points.has_brightness:
                Group(parent_lightbulb.item_ids.brightness)\
                    .typed(GroupType.DIMMER_AVG)\
                    .label(_('Brightness'))\
                    .icon('light')\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.CONTROL, PropertyType.LIGHT)\
                    .append_to(self)

            if parent_lightbulb.points.has_colortemperature:
                Group(parent_lightbulb.item_ids.colortemperature)\
                    .typed(GroupType.NUMBER_AVG)\
                    .label(_('Colortemperature'))\
                    .icon('light')\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.CONTROL, PropertyType.COLORTEMPERATURE)\
                    .append_to(self)

            if parent_lightbulb.points.has_onoff:
                Group(parent_lightbulb.item_ids.onoff)\
                    .typed(GroupType.ONOFF)\
                    .label(_('On/Off'))\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.SWITCH, PropertyType.LIGHT)\
                    .append_to(self)

            if parent_lightbulb.points.has_rgb:
                Group(parent_lightbulb.item_ids.rgb)\
                    .typed(GroupType.COLOR)\
                    .label(_('RGB Color'))\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.CONTROL)\
                    .append_to(self)

            sublightbulbs = []

            for sublightbulb in parent_lightbulb.subequipment:
                sublightbulbs.append(sublightbulb.item_ids.lightbulb)
                self.__build_thing(sublightbulb, parent_lightbulb_item)

            parent_lightbulb_item.scripting({
                'is_thing': False,
                'subequipment': ','.join(sublightbulbs)
            })

        return parent_lightbulb.has_subequipment

    def __build_thing(self, lightbulb: Lightbulb, lightbulb_item: Group) -> None:
        if lightbulb.is_child:
            lightbulb_item = Group(lightbulb.item_ids.lightbulb)\
                .label(_('Lightbulb {name}').format(name=lightbulb.name))\
                .icon('light')\
                .equipment(lightbulb.parent)\
                .semantic(lightbulb)\
                .append_to(self)

        scripting = {
            'is_thing': True,
            'cycles_item': lightbulb.item_ids.switchingcycles
        }

        Number(lightbulb.item_ids.switchingcycles)\
            .typed(NumberType.DIMENSIONLESS)\
            .label(_('Switching cycles'))\
            .format('%d')\
            .icon('switchingcycles')\
            .sensor('switchingcycle', lightbulb.influxdb_tags, True)\
            .equipment(lightbulb)\
            .groups('SwitchingCycles')\
            .semantic(PointType.MEASUREMENT)\
            .append_to(self)

        Switch(lightbulb.item_ids.switchingcyclesreset)\
            .label(_('Reset'))\
            .icon('configuration')\
            .equipment(lightbulb)\
            .groups('SwitchingCyclesReset')\
            .semantic(PointType.CONTROL)\
            .scripting({
                'cycles_item': lightbulb.item_ids.switchingcycles
            })\
            .expire('10s', state='OFF')\
            .append_to(self)

        if lightbulb.points.has_brightness:
            brightness = Dimmer(lightbulb.item_ids.brightness)\
                .label(_('Brightness'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL, PropertyType.LIGHT)\
                .channel(lightbulb.points.channel('brightness'))

            if lightbulb.is_child:
                brightness.groups(lightbulb.parent.item_ids.brightness)

            brightness.append_to(self)

            scripting['brightness_item'] = lightbulb.item_ids.brightness

        if lightbulb.points.has_colortemperature:
            colortemperature = Number(lightbulb.item_ids.colortemperature)\
                .label(_('Colortemperature'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL, PropertyType.COLORTEMPERATURE)\
                .channel(lightbulb.points.channel('colortemperature'))

            if lightbulb.is_child:
                colortemperature.groups(
                    lightbulb.parent.item_ids.colortemperature)

            colortemperature.append_to(self)

            scripting['colortemperature_item'] = lightbulb.item_ids.colortemperature

        if lightbulb.points.has_onoff:
            onoff = Switch(lightbulb.item_ids.onoff)\
                .label(_('On/Off'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL, PropertyType.LIGHT)\
                .channel(lightbulb.points.channel('onoff'))

            if lightbulb.is_child:
                onoff.groups(lightbulb.parent.item_ids.onoff)

            onoff.append_to(self)

            scripting['onoff_item'] = lightbulb.item_ids.onoff

        if lightbulb.points.has_rgb:
            rgb = Color(lightbulb.item_ids.rgb)\
                .label(_('RGB Color'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL)\
                .channel(lightbulb.points.channel('rgb'))

            if lightbulb.is_child:
                rgb.groups(lightbulb.parent.item_ids.rgb)

            rgb.append_to(self)

            scripting['rgb_item'] = lightbulb.item_ids.rgb

        lightbulb_item.scripting(scripting)

    def __build_buttons_assignment(self,
                                   lightbulb: Lightbulb,
                                   wallswitches: List[WallSwitch]) -> None:
        for wallswitch in wallswitches:
            for button_key in range(0, wallswitch.buttons_count):
                String(wallswitch.item_ids.buttonassignment(button_key, lightbulb))\
                    .label(wallswitch.buttonassignment_name(button_key))\
                    .icon('configuration')\
                    .groups(wallswitch.item_ids.buttonassignment(button_key))\
                    .append_to(self)

    def __build_motion_assignment(self,
                                  lightbulb: Lightbulb,
                                  motiondetectors: List[MotionDetector]) -> None:
        for motiondetector in motiondetectors:
            Switch(motiondetector.item_ids.assignment(lightbulb))\
                .label(motiondetector.name)\
                .icon('motiondetector')\
                .groups(motiondetector.item_ids.assignment())\
                .append_to(self)
