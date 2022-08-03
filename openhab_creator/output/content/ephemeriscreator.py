from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional
from xml.dom import minidom

from openhab_creator.output.basecreator import BaseCreator

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class Event():
    MONTHS = {
        1: 'JANUARY',
        2: 'FEBRUARY',
        3: 'MARCH',
        4: 'APRIL',
        5: 'MAY',
        6: 'JUNE',
        7: 'JULY',
        8: 'AUGUST',
        9: 'SEPTEMBER',
        10: 'OCTOBER',
        11: 'NOVEMBER',
        12: 'DECEMBER'
    }

    def __init__(self, typed: str):
        self.typed = typed
        self.names = []

    @property
    def description(self) -> str:
        return ', '.join(self.names)


class FixedDay(Event):
    ANNUAL_FLAG = 'A'
    BIRTHDAY_FLAG = 'B'
    FIXED_FLAG = 'F'

    FLAGS = (ANNUAL_FLAG, BIRTHDAY_FLAG, FIXED_FLAG)

    FIXED_DAYMATCHER = re.compile(
        r'^([ABF]) (0?\d{1,2})\.(0?\d{1,2})\.((19|20)\d{2})? (.*)$')

    def __init__(self, typed: str, event_str: str):
        super().__init__(typed)
        matches = self.FIXED_DAYMATCHER.match(event_str)
        if matches:
            _, day, month, year, _, event_name = matches.groups()
            self.day: int = int(day)
            self.month: int = int(month)
            self.year: Optional[int] = int(year) if year else None
            self.name: str = self._format_name(typed, event_name, year)
            self.names.append(self.name)

    def _format_name(self, typed: str, event_name: str, year) -> str:
        name = event_name
        if year:
            if self.BIRTHDAY_FLAG == typed:
                name += f' ({year})'
            elif self.ANNUAL_FLAG == typed:
                name = f'{year}. {name}'

        return name

    def add_name(self, name: str) -> None:
        self.names.append(name)

    @property
    def event_key(self) -> str:
        return f'{self.day}.{self.month}.'

    def add_as_node(self, xml_document, root_node):
        day_node = xml_document.createElement('tns:Fixed')
        day_node.setAttribute('month', self.MONTHS[self.month])
        day_node.setAttribute('day', str(self.day))
        day_node.setAttribute('descriptionPropertiesKey', self.description)

        if self.typed == self.FIXED_FLAG and self.year:
            day_node.setAttribute('validFrom', str(self.year))

        root_node.appendChild(day_node)
        return root_node


class RelativeToFixedDay(Event):
    FLAG = 'R'

    RELATIVE_DAYMATCHER = re.compile(
        r'^R (0?\d{1,2})\.(0?\d{1,2})\. ([A-Z]+) ([A-Z]+) (.*)$')

    def __init__(self, event_str: str):
        super().__init__(self.FLAG)
        matches = self.RELATIVE_DAYMATCHER.match(event_str)
        if matches:
            day, month, weekday, direction, event_name = matches.groups()
            self.day: int = int(day)
            self.month: int = int(month)
            self.weekday: str = weekday
            self.direction: str = direction
            self.name: str = event_name
            self.names.append(self.name)

    @property
    def event_key(self) -> str:
        return f'R{self.day}.{self.month}.'

    def add_as_node(self, xml_document, root_node):
        day_node = xml_document.createElement('tns:RelativeToFixed')
        day_node.setAttribute('descriptionPropertiesKey', self.description)

        weekday_node = xml_document.createElement('tns:Weekday')
        weekday_node.appendChild(xml_document.createTextNode(self.weekday))
        day_node.appendChild(weekday_node)

        direction_node = xml_document.createElement('tns:When')
        direction_node.appendChild(xml_document.createTextNode(self.direction))
        day_node.appendChild(direction_node)

        date_node = xml_document.createElement('tns:Date')
        date_node.setAttribute('month', self.MONTHS[self.month])
        date_node.setAttribute('day', str(self.day))
        day_node.appendChild(date_node)

        root_node.appendChild(day_node)
        return root_node


class FixedWeekday(Event):
    FLAG = 'W'

    WEEKDAY_MATCHER = re.compile(
        r'^W (0?\d{1,2}) ([A-Z]+) ([A-Z]+) (.*)$')

    def __init__(self, event_str: str):
        super().__init__(self.FLAG)
        matches = self.WEEKDAY_MATCHER.match(event_str)

        if matches:
            month, which, weekday, event_name = matches.groups()
            self.month = int(month)
            self.which = which
            self.weekday = weekday
            self.name = event_name
            self.names.append(self.name)

    @property
    def event_key(self) -> str:
        return self.description

    def add_as_node(self, xml_document, root_node):
        day_node = xml_document.createElement('tns:FixedWeekday')
        day_node.setAttribute('which', self.which)
        day_node.setAttribute('weekday', self.weekday)
        day_node.setAttribute('month', self.MONTHS[self.month])
        day_node.setAttribute('descriptionPropertiesKey', self.description)

        root_node.appendChild(day_node)
        return root_node


class ChristianHoliday(Event):
    FLAG = 'C'

    def __init__(self, event_str: str):
        super().__init__(self.FLAG)
        self.name = event_str[2:]

    @property
    def event_key(self) -> str:
        return self.name

    def add_as_node(self, xml_document, root_node):
        day_node = xml_document.createElement('tns:ChristianHoliday')
        day_node.setAttribute('type', self.name)

        root_node.appendChild(day_node)
        return root_node


class EphemerisCreator(BaseCreator):

    def __init__(self, outputdir):
        super().__init__('xml', outputdir, 'ephemeris')

    def build(self, configuration: Configuration) -> None:
        for event_type in ['birthdays', 'holidays', 'specialdays']:
            data = self._read_data_from_secrets(configuration, event_type)

            if data:
                xml_document, root_node = self._get_holiday_base_xml()

                for event in data.values():
                    root_node = event.add_as_node(xml_document, root_node)

                self.append(xml_document.toprettyxml(indent="\t"))
                self.write_file(event_type)

    @staticmethod
    def _read_data_from_secrets(configuration: Configuration, events_type: str):
        events = configuration.secrets.secret_optional(
            'ephemeris', events_type)

        data = None

        if events:
            data = {}
            for event_str in events:
                flag = event_str[0]

                if flag in FixedDay.FLAGS:
                    event = FixedDay(flag, event_str)

                    if event.event_key in data:
                        data[event.event_key].add_name(event.name)
                    else:
                        data[event.event_key] = event
                elif flag == RelativeToFixedDay.FLAG:
                    event = RelativeToFixedDay(event_str)
                    data[event.event_key] = event
                elif flag == ChristianHoliday.FLAG:
                    event = ChristianHoliday(event_str)
                    data[event.event_key] = event
                elif flag == FixedWeekday.FLAG:
                    event = FixedWeekday(event_str)
                    data[event.event_key] = event

        return data

    @staticmethod
    def _get_holiday_base_xml():
        xml_document = minidom.Document()
        config = xml_document.createElement('tns:Configuration')
        config.setAttribute('hierarchy', 'de')
        config.setAttribute('description', 'Germany')
        config.setAttribute('xmlns:tns', 'http://www.example.org/Holiday')
        config.setAttribute(
            'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        config.setAttribute('xsi:schemaLocation',
                            'http://www.example.org/Holiday /Holiday.xsd')

        xml_document.appendChild(config)

        root_node = xml_document.createElement('tns:Holidays')
        config.appendChild(root_node)
        return xml_document, root_node
