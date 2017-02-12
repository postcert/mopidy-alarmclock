from __future__ import unicode_literals
from weekalarmhandler import WeekAlarmHandler

import datetime
import os
import re

import tornado.template
import tornado.web


template_directory = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = tornado.template.Loader(template_directory)

MESSAGES = {
    'ok': (u'Alarm has been properly set.', 'success'),
    'format': (u'The date\'s format you specified is incorrect.', 'danger'),
    'cancel': (u'Alarm has been canceled.', 'success'),
}


class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(self, config, core, alarm_manager, msg_store):
        self.config = config
        self.core = core
        self.alarm_manager = alarm_manager
        self.msg_store = msg_store

    def send_message(self, code):
        self.msg_store.msg_code = code
        self.redirect('/alarmclock/')


class MainRequestHandler(BaseRequestHandler):
    def get(self):
        message = None
        if self.msg_store.msg_code and self.msg_store.msg_code in MESSAGES:
            message = MESSAGES[self.msg_store.msg_code]
            self.msg_store.msg_code = None

        playlists = self.core.playlists.playlists.get()

        self.write(template_loader.load('index.html').generate(
            playlists=playlists,
            alarm_manager=self.alarm_manager,
            message=message,
            config=self.config['alarmclock']
        ))


class SetAlarmRequestHandler(BaseRequestHandler):
    def post(self):
        playlist = self.get_argument('playlist', None)

        # Ugly block for getting times
        raw_times = []
        days = ("sun", "mon", "tue", "wed", "thu", "fri", "sat")
        for day in days:
            raw_times.append(self.get_argument("time_{}".format(day)), None)

        converted_times = []
        # Sanity check times
        for alarm_time in raw_times:
            # Based on RE found here http://stackoverflow.com/a/7536768/927592
            match = re.match('^([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5]?[0-9])$', alarm_time)
            if not match:
                self.send_message('format')
                return

            time_comp = map(lambda x: int(x), match.groups())
            converted_times.append(datetime.time(hour=time_comp[0], minute=time_comp[1]))

        alarm_week = WeekAlarmHandler()
        for day_index, converted_time in converted_times:
            alarm_week.set_alarm(day_index, converted_time)


        random_mode = bool(self.get_argument('random', False))

        # Get and sanitize volume and seconds to full volume
        volume = int(self.get_argument('volume', 100))
        volume_increase_seconds = int(self.get_argument('incsec', 30))
        if volume < 1 or volume > 100:
            volume = 100
        if volume_increase_seconds < 0 or volume_increase_seconds > 300:
            volume_increase_seconds = 30

        self.alarm_manager.set_alarm(alarm_week, playlist, random_mode, volume, volume_increase_seconds)
        self.send_message('ok')


class CancelAlarmRequestHandler(BaseRequestHandler):
    def get(self):
        self.alarm_manager.cancel()
        self.send_message('cancel')


class MessageStore(object):
    msg_code = None  # Message to be stored


# little hack to pass a persistent instance (alarm_manager) to the handler
# and pass the instance of mopidy.Core to the AlarmManager (via get_core)
def factory_decorator(alarm_manager, msg_store):
    def app_factory(config, core):
        # since all the RequestHandler-classes get the same arguments ...
        def bind(url, klass):
            return (url, klass, {'config': config, 'core': core, 'alarm_manager': alarm_manager.get_core(core), 'msg_store': msg_store})

        return [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static')}),

            bind('/', MainRequestHandler),
            bind('/set/', SetAlarmRequestHandler),
            bind('/cancel/', CancelAlarmRequestHandler),
        ]

    return app_factory
