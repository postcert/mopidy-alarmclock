import datetime


class WeekAlarmHandler(object):
    def __init__(self):
        self.alarm_times = [datetime.time] * 7
        self.last_play = [datetime.date] * 7
        self.one_day = datetime.timedelta(days=1)

    def ring_alarm(self):
        # type: (None) -> bool
        now = datetime.datetime.now()
        weekday_number = now.weekday()
        if self.alarm_times[weekday_number] > now.time():
            if self.last_play[weekday_number] != now.date():
                self.last_play[weekday_number] = now.date()
                return True
        else:
            return False

    def set_alarm(self, weekday_number, time):
        # type: (int, datetime.time) -> None
        self.alarm_times[weekday_number] = time
        # Set last_played times to yesterday, in case the alarm is for today
        self.last_play[weekday_number] = datetime.date - datetime.timedelta(days=1)
