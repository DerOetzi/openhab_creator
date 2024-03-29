from __future__ import annotations

from typing import Any, Dict, Optional, List, Tuple

from openhab_creator import CreatorEnum


class Formatter():
    @staticmethod
    def ucfirst(raw: str) -> str:
        ucfirst = ''
        if len(raw) > 1:
            ucfirst = raw[0].upper() + raw[1:].lower()
        elif len(raw) == 1:
            ucfirst = raw.upper()

        return ucfirst

    @staticmethod
    def format_id(raw_id: str) -> str:
        formatted_id = raw_id.strip()
        formatted_id = formatted_id.replace('ö', 'oe')
        formatted_id = formatted_id.replace('ä', 'ae')
        formatted_id = formatted_id.replace('ü', 'ue')
        formatted_id = formatted_id.replace('ß', 'ss')
        formatted_id = formatted_id.replace(' ', '')
        formatted_id = formatted_id.replace('_', '')
        return formatted_id

    @staticmethod
    def key_value_pairs(pairs: Dict[str, Any],
                        prefix: Optional[str] = '',
                        suffix: Optional[str] = '',
                        separator: Optional[str] = ', ',
                        escape: Optional[bool] = True) -> str:

        if escape:
            output = [
                f'{key}={Formatter.value(value)}' for key, value in pairs.items()]
        else:
            output = [
                f'{key}={value}' for key, value in pairs.items()]

        return prefix + separator.join(output) + suffix

    @staticmethod
    def key_value_tuples(pairs: List[Tuple],
                         prefix: Optional[str] = '',
                         suffix: Optional[str] = '',
                         separator: Optional[str] = ', ') -> str:

        output = []

        for pair in pairs:
            if len(pair) == 2:
                comp = '='
                val = pair[1]
            else:
                comp = pair[1]
                val = pair[2]

            output.append(f'{pair[0]}{comp}{Formatter.value(val)}')

        return prefix + separator.join(output) + suffix

    @staticmethod
    def value(value: Any) -> str:
        if isinstance(value, (str, CreatorEnum)):
            value = f'"{value}"'
        elif isinstance(value, bool):
            value = 'true' if value else 'false'
        else:
            value = str(value)

        return value

    @staticmethod
    def label(label: Optional[str] = '', format_str: Optional[str] = None) -> Optional[str]:
        if format_str is not None:
            label += f' [{format_str}]'

        label = label.strip()

        if label == '':
            label = None

        return label
