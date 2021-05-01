# pylint: skip-file
from core.actions import ScriptExecution
from core.log import logging, LOG_PREFIX

from personal.dateutils import DateUtils


class TimerManager:
    def __init__(self, name):
        self.log = logging.getLogger(
            u"{}.TimerManager.{}".format(LOG_PREFIX, name))
        self.timers = {}

    def activate(self, key, timer, date_time):
        if DateUtils.now().isAfter(date_time):
            self.log.warn(
                "{} nicht aktiviert weil {} in der Vergangenheit liegt!".format(key, date_time))
            return

        if not self.reschedule(key, date_time):
            self.log.info(
                u"Aktiviere neuen Timer {} am {}".format(key, date_time))
            self.timers[key] = ScriptExecution.createTimer(date_time, timer)

    def reschedule(self, key, date_time):
        if self.is_active(key):
            self.log.info(
                u"Aktualisiere vorhandenen Timer {} auf {}".format(key, date_time))
            self.timers[key].reschedule(date_time)
            return True

        return False

    def is_active(self, key):
        return key in self.timers and not self.timers[key].hasTerminated()

    def cancel(self, key):
        if key in self.timers:
            self.log.info(u"Entferne Timer {}".format(key))
            self.timers[key].cancel()

    def cancel_all(self):
        for key in self.timers:
            self.cancel(key)
