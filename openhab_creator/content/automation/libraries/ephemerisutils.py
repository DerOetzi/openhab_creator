# pylint: skip-file
import glob
import hashlib
import re
from os import mkdir, path, remove
from shutil import copyfile

from core.actions import Ephemeris
from core.log import LOG_PREFIX, logging


class EphemerisUtils(object):
    holiday_map = {}
    _initialized = False
    log = logging.getLogger(u"{}.ephemeris".format(LOG_PREFIX))

    CONFIGDIR = '/openhab/conf/ephemeris/'

    @classmethod
    def _init(cls):
        if not cls._initialized:
            cls._initialized = True
            properties_file = cls.CONFIGDIR + 'holidays.properties'
            if path.exists(properties_file):
                cls._read_holiday_map(properties_file)

    @classmethod
    def _read_holiday_map(cls, properties_file):
        with open(properties_file, 'rt') as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith('#'):
                    key_value = l.split('=')
                    key = key_value[0].strip()
                    value = "=".join(key_value[1:]).strip().strip('"')
                    cls.holiday_map[key] = value

    @classmethod
    def holiday_key_to_map(cls, holiday_key):
        cls._init()

        if holiday_key is not None:
            key = "holiday.description." + holiday_key
            if key in cls.holiday_map:
                return unicode(cls.holiday_map[key], 'unicode-escape')

        return holiday_key

    @classmethod
    def name_holiday(cls, offset=0):
        return cls.holiday_key_to_map(cls.name_day('holidays', offset))

    @classmethod
    def next_holiday(cls, offset=0):
        holiday_next = cls.next_day('holidays', offset)
        holiday_next['name'] = cls.holiday_key_to_map(holiday_next['name'])
        return holiday_next

    @classmethod
    def is_holiday(cls, offset=0):
        return cls.is_day('holidays', offset)

    @classmethod
    def name_day(cls, file_key, offset=0):
        filename = cls._init_file(file_key)
        dayname = Ephemeris.getBankHolidayName(offset, filename)
        return dayname

    @classmethod
    def is_day(cls, file_key, offset=0):
        next_day = cls.next_day(file_key, offset)
        return next_day['until'] == offset

    @classmethod
    def next_day(cls, file_key, offset=0):
        filename = cls._init_file(file_key)
        dayname = Ephemeris.getNextBankHoliday(offset, filename)
        until = Ephemeris.getDaysUntil(dayname, filename)
        return {"name": dayname, "until": until}

    @classmethod
    def until_day(cls, dayname, file_key):
        filename = cls._init_file(file_key)
        return Ephemeris.getDaysUntil(dayname, filename)

    @classmethod
    def _init_file(cls, file_key):
        cache_directory = cls.CONFIGDIR + '/cache/'

        if not path.exists(cache_directory):
            mkdir(cache_directory, 0o755)

        original_filename = cls.CONFIGDIR + file_key + '.xml'
        checksum = cls._checksum(original_filename)
        cached_filename = cache_directory + file_key + '_' + checksum + '.xml'

        if not path.exists(cached_filename):
            cls.log.warn(u"Recaching of file %s", file_key)
            for oldfile in glob.glob(cache_directory + file_key + '_*.xml'):
                remove(oldfile)

            copyfile(original_filename, cached_filename)

        return cached_filename

    @staticmethod
    def _checksum(filename):
        h = hashlib.sha256()

        with open(filename, 'rb') as check_file:
            while True:
                chunk = check_file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)

        return h.hexdigest()

    @staticmethod
    def is_weekend(offset=0):
        return Ephemeris.isWeekend(offset)
