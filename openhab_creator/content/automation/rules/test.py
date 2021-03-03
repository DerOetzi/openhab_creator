
from personal.signalmessenger import SignalMessenger
from core.rules import rule
from core.triggers import StartupTrigger

from core.log import logging, LOG_PREFIX

from personal.timermanager import TimerManager

from personal.dateutils import DateUtils


@rule('Test Timer')
class Test():
    def __init__(self):
        self.log = logging.getLogger('{}.Test'.format(LOG_PREFIX))
        self.timer = TimerManager('Test')

        self.triggers = [StartupTrigger(trigger_name="TestStartup").trigger]

    def execute(self, module, inputs):
        self.log.info(module)
        modulecfg = inputs["module"].split("_")
        if modulecfg[0] == 'TestStartup':
            self.log.info('Timer start')
            self.timer.activate('test', lambda: self.log.info(
                'Timer done.'), DateUtils.now().plusSeconds(10))