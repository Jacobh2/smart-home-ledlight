from threading import Timer
from time import time
from datetime import datetime
from datetime import timedelta
import logging


class Alarm(object):

    def __init__(self, wake_up_fn, alarm_time, max_brightness):
        self.logger = logging.getLogger('alarm')
        self.alarm_time = timedelta(seconds=alarm_time)
        self.max_brightness = max_brightness

        self.time = None
        self.timer = None
        self.wake_up_fn = wake_up_fn

    def _handle_alarm(self):
        self.logger.info("Alarm is firing!!")
        #wake_up(self, total_time, steps, max_brightness):
        # Reset the time if we login during alarm!
        self.time = None
        
        total_time = steps = int(self.alarm_time.total_seconds())
        self.wake_up_fn(total_time, steps, self.max_brightness)


    def activate(self, alarm_time):
        self.time = alarm_time
        hour, minute = list(map(int, alarm_time.split(':')))
        
        # get unixtime at alarm time
        #year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]
        now = datetime.now()


        # Figure out if it is a time tomorrow or not:
        time_tomorrow = False
        if hour < now.hour:
            # Clearly tomorrow, since the hour is before what it is now
            time_tomorrow = True
        elif hour == now.hour:
            # Only tomorrow if the minutes are less than now
            time_tomorrow = minute <= now.minute

        #days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0
        if time_tomorrow:
            self.logger.info("Alarm is for a time tomorrow.")
            time_to_use = now + timedelta(1)
        else:
            self.logger.info("Alarm is for a time today.")
            time_to_use = now

        self.logger.info("Time to use for alarm: %s", time_to_use)

        alarm_time_datetime = datetime(
            time_to_use.year, time_to_use.month, time_to_use.day, hour, minute
        )

        self.logger.info("Setting alarm to %s minus the start time of wakeup: %s", alarm_time_datetime, self.alarm_time)

        sleep = alarm_time_datetime - self.alarm_time - now

        self.logger.info("Activating alarm in %s seconds from now! (%s sec)", sleep, sleep.seconds)
        self.timer = Timer(sleep.seconds, self._handle_alarm)
        self.timer.setDaemon(True)
        self.timer.start()
        return True

    def cancel(self):
        if self.timer is not None:
            self.logger.info("Cancelling alarm")
            self.timer.cancel()
            
        self.time = None
        self.timer = None
        return True

