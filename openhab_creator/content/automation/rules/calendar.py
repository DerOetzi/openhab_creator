# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.dateutils import DateUtils
from personal.ephemerisutils import EphemerisUtils
from personal.item import Group, Item
from personal.signalmessenger import SignalMessenger
from personal.timermanager import TimerManager

timers = TimerManager('calendar')


logger = logging.getLogger('{}.Calendar'.format(LOG_PREFIX))


@rule("Is holiday")
@when("System started")
@when("Time cron 0 2 0 * * ?")
def is_holiday(event):
    holiday_item = Item('holiday')
    if EphemerisUtils.is_holiday():
        holiday_item.post_update(ON)
    else:
        holiday_item.post_update(OFF)

    Item('holidayName').post_update(EphemerisUtils.name_holiday())


@rule("Special day")
@when("System started")
@when("Time cron 0 3 0 * * ?")
def special_day(event):
    HOLIDAY = "holiday"
    BIRTHDAY = "birthdays"
    SPECIAL = "specialdays"

    found = {}

    found[HOLIDAY] = EphemerisUtils.next_holiday()
    found[BIRTHDAY] = EphemerisUtils.next_day(BIRTHDAY)
    found[SPECIAL] = EphemerisUtils.next_day(SPECIAL)

    min_key = min(found.keys(), key=(lambda k: found[k]["until"]))
    min_offset = found[min_key]["until"]
    date = DateUtils.now().plusDays(min_offset)
    date = DateUtils.set_time(date, 0)

    descriptions = []

    days = filter(lambda day: found[day]["until"] == min_offset, found)

    for day in days:
        description = found[day]["name"]
        if day == BIRTHDAY:
            birthdays = description.split(",")
            for birthday in birthdays:
                birthday = birthday.strip()
                birthday = DateUtils.replace_year_by_age(birthday, date)
                descriptions.append(birthday)
        elif day == SPECIAL:
            description = EphemerisUtils.holiday_key_to_map(description)
            description = DateUtils.replace_year_by_age(description, date)
            descriptions.append(description)
        else:
            descriptions.append(description)

    next_item = Item('nextSpecialDay')
    next_item.set_label(', '.join(descriptions))
    next_item.post_update(date)

    today_item = Item('todaySpecialDay')
    if (min_offset == 0):
        today_item.post_update(', '.join(descriptions))
    else:
        today_item.post_update(NULL)


@rule('Birthdays')
@when('System started')
@when('Time cron 0 2 0 * * ?')
def birthdays(event):
    offset = 0
    next_birthdays = []
    index = 0

    for i in range(0, 10):
        next_birthday = EphemerisUtils.next_day('birthdays', offset)
        next_name = next_birthday['name']
        next_until = next_birthday['until']

        append_for_timer = i == 0
        date = DateUtils.set_time(DateUtils.now().plusDays(next_until), 8)

        for birthday in next_name.split(','):
            if index < 10:
                birthday = birthday.strip()
                birthday = DateUtils.replace_year_by_age(birthday, date)
                if append_for_timer:
                    next_birthdays.append(birthday)
                    timer_date = date

                birthday_item = Item('nextBirthday{}'.format(index))
                birthday_item.set_label(birthday)
                birthday_item.post_update(date)

                index += 1

        offset = next_until + 1

    def timer(): return birthday_notification(next_birthdays)
    timers.activate("birthday", timer, timer_date)


def birthday_notification(birthdays):
    item = Item('todaySpecialDay')
    message = item.scripting('birthday') if len(
        birthdays) == 1 else item.scripting('birthdays')
    SignalMessenger.broadcast(message.format(", ".join(birthdays)))


@rule('Garbage cans system start')
@when('System started')
def garbage_cans(event):
    for item in Group('garbagecan'):
        garbage_can(item)


@rule('Garbage can event changed')
@when('Member of garbagecan changed')
def garbage_can_changed(event):
    garbagecan_item = Item.from_event(event)
    garbage_can_reminder(garbagecan_item, event)


def garbage_can(garbagecan_item, event=None):
    def timer(): return SignalMessenger.broadcast(
        garbagecan_item.scripting('message'))

    timer_date = garbagecan_item.get_datetime(DateUtils.now())
    timer_date = timer_date.minusDays(1)
    timer_date = DateUtils.set_time(timer_date, 18)

    timers.activate(garbagecan_item.scripting('identifier'), timer, timer_date)


@rule('Reminders restart')
@when('System started')
def restart_reminders(event):
    for reminder_item in Group('CalendarReminder'):
        config = reminder_item.scripting()

        default_time = DateUtils.now()
        default_time = DateUtils.set_time(default_time,
                                          config['hour'].intValue(),
                                          config['minutes'].intValue())

        reminder_time = reminder_item.get_datetime(default_time, True)

        if reminder_time.isBefore(DateUtils.now()):
            reminder_timer()
        else:
            timers.activate(config['identifier'],
                            lambda: reminder_timer(),
                            reminder_time)


def reminder_timer():
    for reminder_item in Group('CalendarReminder'):
        config = reminder_item.scripting()

        default_time = DateUtils.now()
        default_time = DateUtils.set_time(default_time,
                                          config['hour'].intValue(),
                                          config['minutes'].intValue())

        reminder_time = reminder_item.get_datetime(default_time)

        if DateUtils.now().isAfter(reminder_time):
            if config['recipient'] == 'broadcast':
                SignalMessenger.broadcast(config['message'])
            else:
                SignalMessenger.notification(
                    config['recipient'], config['message'])

            reminder_time = DateUtils.now().plusDays(1)
            reminder_time = DateUtils.set_time(reminder_time,
                                               config['hour'].intValue(),
                                               config['minutes'].intValue())

            reminder_item.post_update(reminder_time)

            timers.activate(config['identifier'],
                            lambda: reminder_timer(),
                            reminder_time)

            confirm_item = reminder_item.from_scripting('confirm')
            confirm_item.post_update(OFF)


@rule('Reminder confirm')
@when('Member of CalendarReminderConfirm received command ON')
def reminder_confirm(event):
    confirm_item = Item.from_event(event)
    reminder_item = confirm_item.from_scripting('reminder')
    config = confirm_item.scripting()

    reminder_time = DateUtils.now()
    reminder_time = reminder_time.plusDays(config['interval'].intValue())
    reminder_time = DateUtils.set_time(reminder_time,
                                       config['hour'].intValue(),
                                       config['minutes'].intValue())

    timers.activate(config['identifier'],
                    lambda: reminder_timer(),
                    reminder_time)

    reminder_item.post_update(reminder_time)
    confirm_item.post_update(ON)


def scriptUnloaded():  # NOSONAR
    timers.cancel_all()
