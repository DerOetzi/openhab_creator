# pylint: skip-file

class StringUtils(object):
    decimal_sep = ','
    thousand_sep = '.'

    @staticmethod
    def set_number_format(decimal_sep, thousand_sep):
        StringUtils.decimal_sep = decimal_sep
        StringUtils.thousand_sep = thousand_sep

    @staticmethod
    def format_number(number, precision):
        format_str = '{{:,.{}f}}'.format(precision)
        number_str = format_str.format(number)
        return number_str.replace(',', 'X')\
            .replace('.', StringUtils.decimal_sep)\
            .replace('X', StringUtils.thousand_sep)
