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

        for lightbulb in configuration.equipment('lightbulb'):
            self.__build_parent(lightbulb)

            if not self.__build_subequipment(lightbulb):
                self.__build_thing(lightbulb)

            if configuration.has_equipment('wallswitch'):
                self.__build_buttons_assignment(
                    lightbulb, configuration.equipment('wallswitch'))

            if configuration.has_equipment('motiondetector'):
                self.__build_motion_assignment(
                    lightbulb, configuration.equipment('motiondetector'))

        self.write_file('lightbulb')

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
            .icon('configuration')\
            .append_to(self)

        Group('SwitchingCyclesReset')\
            .label(_('Switching cycles reset'))\
            .append_to(self)

    def __build_parent(self, lightbulb: Lightbulb) -> None:
        Group(lightbulb.lightbulb_id)\
            .label(_('Lightbulb {blankname}').format(blankname=lightbulb.blankname))\
            .icon('light')\
            .location(lightbulb.location)\
            .semantic(lightbulb)\
            .append_to(self)

        String(lightbulb.lightcontrol_id)\
            .label(_('Lightcontrol'))\
            .icon('lightcontrol')\
            .equipment(lightbulb)\
            .groups('Lightcontrol')\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(lightbulb.hide_id)\
            .label(_('Hide on lights page'))\
            .icon('hide')\
            .config()\
            .equipment(lightbulb)\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(lightbulb.auto_id)\
            .label(_('Scene controlled'))\
            .icon('auto')\
            .equipment(lightbulb)\
            .groups('AutoLight')\
            .semantic(PointType.CONTROL)\
            .append_to(self)

        Switch(lightbulb.autodisplay_id)\
            .label(_('Display scene controlled'))\
            .equipment(lightbulb)\
            .semantic(PointType.STATUS)\
            .append_to(self)

        Number(lightbulb.autoreactivation_id)\
            .label(_('Reactivate scene controlled'))\
            .icon('reactivation')\
            .equipment(lightbulb)\
            .groups('AutoReactivationLight')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Switch(lightbulb.autodarkness_id)\
            .label(_('In the dark'))\
            .icon('darkness')\
            .equipment(lightbulb)\
            .groups('AutoDarkness')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Switch(lightbulb.autoabsence_id)\
            .label(_('Even in absence'))\
            .icon('absence')\
            .equipment(lightbulb)\
            .groups('AutoAbsenceLight')\
            .semantic(PointType.SETPOINT)\
            .append_to(self)

        Number(lightbulb.motiondetectorperiod_id)\
            .typed(NumberType.TIME)\
            .label(_('Motiondetector period'))\
            .format('%d s')\
            .icon('timeout')\
            .equipment(lightbulb)\
            .groups('MotionDetectorPeriod')\
            .semantic(PointType.SETPOINT, PropertyType.DURATION)\
            .append_to(self)

        if lightbulb.nightmode:
            String(lightbulb.nightmode_id)\
                .label(_('Nightmode configuration'))\
                .icon('configuration')\
                .equipment(lightbulb)\
                .groups('Nightmode')\
                .semantic(PointType.SETPOINT)\
                .append_to(self)

    def __build_subequipment(self, parent_lightbulb: Lightbulb) -> bool:
        if parent_lightbulb.has_subequipment:
            if parent_lightbulb.has_brightness:
                Group(parent_lightbulb.brightness_id)\
                    .typed(GroupType.DIMMER_AVG)\
                    .label(_('Brightness'))\
                    .icon('light')\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.CONTROL, PropertyType.LIGHT)\
                    .append_to(self)

            if parent_lightbulb.has_colortemperature:
                Group(parent_lightbulb.colortemperature_id)\
                    .typed(GroupType.NUMBER_AVG)\
                    .label(_('Colortemperature'))\
                    .icon('light')\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.CONTROL, PropertyType.COLORTEMPERATURE)\
                    .append_to(self)

            if parent_lightbulb.has_onoff:
                Group(parent_lightbulb.onoff_id)\
                    .typed(GroupType.ONOFF)\
                    .label(_('On/Off'))\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.SWITCH, PropertyType.LIGHT)\
                    .append_to(self)

            if parent_lightbulb.has_rgb:
                Group(parent_lightbulb.rgb_id)\
                    .typed(GroupType.COLOR)\
                    .label(_('RGB Color'))\
                    .equipment(parent_lightbulb)\
                    .semantic(PointType.CONTROL)\
                    .append_to(self)

            for sublightbulb in parent_lightbulb.subequipment:
                self.__build_thing(sublightbulb)

        return parent_lightbulb.has_subequipment

    def __build_thing(self, lightbulb: Lightbulb) -> None:
        if lightbulb.is_child:
            Group(lightbulb.lightbulb_id)\
                .label(_('Lightbulb {name}').format(name=lightbulb.name))\
                .icon('light')\
                .equipment(lightbulb.parent)\
                .semantic(lightbulb)\
                .append_to(self)

        Number(lightbulb.switchingcycles_id)\
            .typed(NumberType.DIMENSIONLESS)\
            .label(_('Switching cycles {name}').format(name=lightbulb.name))\
            .format('%d')\
            .icon('switchingcycles')\
            .sensor('switchingcycle', lightbulb.influxdb_tags)\
            .equipment(lightbulb)\
            .groups('SwitchingCycles')\
            .semantic(PointType.MEASUREMENT)\
            .append_to(self)

        Switch(lightbulb.switchingcyclesreset_id)\
            .label(_('Reset'))\
            .icon('configuration')\
            .equipment(lightbulb)\
            .groups('SwitchingCyclesReset')\
            .semantic(PointType.CONTROL)\
            .expire('10s', state='OFF')\
            .append_to(self)

        if lightbulb.has_brightness:
            brightness = Dimmer(lightbulb.brightness_id)\
                .label(_('Brightness'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL, PropertyType.LIGHT)\
                .channel(lightbulb.channel('brightness'))

            if lightbulb.is_child:
                brightness.groups(lightbulb.parent.brightness_id)

            brightness.append_to(self)

        if lightbulb.has_colortemperature:
            colortemperature = Number(lightbulb.colortemperature_id)\
                .label(_('Colortemperature'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL, PropertyType.COLORTEMPERATURE)\
                .channel(lightbulb.channel('colortemperature'))

            if lightbulb.is_child:
                colortemperature.groups(lightbulb.parent.colortemperature_id)

            colortemperature.append_to(self)

        if lightbulb.has_onoff:
            onoff = Switch(lightbulb.onoff_id)\
                .label(_('On/Off'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL, PropertyType.LIGHT)\
                .channel(lightbulb.channel('onoff'))

            if lightbulb.is_child:
                onoff.groups(lightbulb.parent.onoff_id)

            onoff.append_to(self)

        if lightbulb.has_rgb:
            rgb = Color(lightbulb.rgb_id)\
                .label(_('RGB Color'))\
                .icon('light')\
                .equipment(lightbulb)\
                .semantic(PointType.CONTROL)\
                .channel(lightbulb.channel('rgb'))

            if lightbulb.is_child:
                rgb.groups(lightbulb.parent.rgb_id)

            rgb.append_to(self)

    def __build_buttons_assignment(self,
                                   lightbulb: Lightbulb,
                                   wallswitches: List[WallSwitch]) -> None:
        for wallswitch in wallswitches:
            for button_key in range(0, wallswitch.buttons_count):
                String(wallswitch.buttonassignment_id(button_key, lightbulb))\
                    .label(wallswitch.buttonassignment_name(button_key))\
                    .icon('configuration')\
                    .groups(wallswitch.buttonassignment_id(button_key))\
                    .append_to(self)

    def __build_motion_assignment(self,
                                  lightbulb: Lightbulb,
                                  motiondetectors: List[MotionDetector]) -> None:
        for motiondetector in motiondetectors:
            Switch(motiondetector.assignment_id(lightbulb))\
                .label(motiondetector.name)\
                .icon('motiondetector')\
                .groups(motiondetector.assignment_id())\
                .append_to(self)
