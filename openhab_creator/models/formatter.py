class Formatter(object):
    @staticmethod
    def ucfirst(raw: str) -> str:
        if len(raw) > 1:
            return raw[0].upper() + raw[1:].lower()
        elif len(raw) == 1:
            return raw.upper()
        else:
            return ''

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
