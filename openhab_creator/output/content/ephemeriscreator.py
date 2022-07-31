from __future__ import annotations
from typing import TYPE_CHECKING
import re

from openhab_creator.output.basecreator import BaseCreator
from openhab_creator import logger

from xml.dom import minidom

if TYPE_CHECKING:
    from openhab_creator.models.configuration import Configuration


class EphemerisCreator(BaseCreator):
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

    DAYMATCHER = re.compile(
        r'^(0?[1-9]|[1-2]\d|3[0-1])\.(0?[1-9]|1[0-2])\.((19|20)\d{2})? (.*)$')

    def __init__(self, outputdir):
        super().__init__('xml', outputdir, 'ephemeris')

    def build(self, configdir: str, configuration: Configuration) -> None:
        birthdays = configuration.secrets.secret_optional(
            'ephemeris', 'birthdays')

        data = {}

        for birthday in birthdays:
            result = self.DAYMATCHER.match(birthday)

            if result:
                day, month, year, _, name = result.groups()
                month = int(month)
                day = int(day)
                key = (day, month)

                value = f'{name} ({year})' if year else name

                if key in data:
                    data[key].append(value)
                else:
                    data[key] = [value]

        doc = minidom.Document()
        config = doc.createElement('tns:Configuration')
        config.setAttribute('hierarchy', 'de')
        config.setAttribute('description', 'Germany')
        config.setAttribute('xmlns:tns', 'http://www.example.org/Holiday')
        config.setAttribute(
            'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        config.setAttribute('xsi:schemaLocation',
                            'http://www.example.org/Holiday /Holiday.xsd')

        doc.appendChild(config)

        days = doc.createElement('tns:Holidays')
        config.appendChild(days)

        for key, value in data.items():
            day, month = key
            day_node = doc.createElement('tns:Fixed')
            day_node.setAttribute('month', self.MONTHS[month])
            day_node.setAttribute('day', str(day))
            day_node.setAttribute('descriptionPropertiesKey', ', '.join(value))
            days.appendChild(day_node)

        self.append(doc.toprettyxml(indent="\t"))
        self.write_file('birthdays')
