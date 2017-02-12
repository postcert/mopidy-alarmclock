import datetime


class Week(object):
    def __init__(self):
        self.week = [datetime.time] * 7
        self.one_day = datetime.timedelta(days=1)

    def get_alarm(self, date):
        # type: (datetime.time) -> datetime.time
        weekday_number = date.weekday()
        alarm = self.week[weekday_number]
        return alarm

    def get_alarm_today(self):
        # type: (None) -> datetime.time
        weekday_number = datetime.datetime.now().weekday()
        return self.week[weekday_number]

    def set_alarm(self, weekday_number, time):
        # type: (int, datetime.time) -> None
        self.week[weekday_number] = time
