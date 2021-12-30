# pylint: skip-file
import re

from core.date import format_date
from java.time import ZonedDateTime, LocalTime


class DateUtils():
    YEAR_MATCHER = re.compile(r'.*([0-9]{4}).*')

    @staticmethod
    def now():
        return ZonedDateTime.now()

    @staticmethod
    def set_now():
        return format_date(DateUtils.now())

    @staticmethod
    def is_today(date_time):
        return date_time.withTimeAtStartOfDay().getMillis() == ZonedDateTime.now().withTimeAtStartOfDay().getMillis()

    @staticmethod
    def set_time(date_time, hour, minute=0, second=0, nanos=0):
        return date_time.withHour(hour).withMinute(minute).withSecond(second).withNano(nanos)

    @classmethod
    def is_now_after(cls, date_time):
        return cls.now().isAfter(date_time)

    @classmethod
    def replace_year_by_age(cls, dayname, date=None):
        if date is None:
            date = cls.now()

        reference_year = int(format_date(date, "Y"))

        result = cls.YEAR_MATCHER.match(dayname)

        if result is not None:
            year = int(result.group(1))
            age = reference_year - year
            dayname = dayname.replace(str(year), str(age))

        return dayname
