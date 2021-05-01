# pylint: skip-file
from core.date import format_date
from java.time import ZonedDateTime


class DateUtils():
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
    def set_time(date_time, hour, minute=0, second=0, millis=0):
        return date_time.withHourOfDay(hour).withMinuteOfHour(minute).withSecondOfMinute(second).withMillisOfSecond(millis)
