from threading import Thread
from time import sleep
import logging


# Linspace so we don't need to depend on numpy
# for just this one function
def linspace(start, stop, n):
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i


def calculate_steps(start, stop, steps):
    return list(linspace(start, stop, steps))


def add_brightness(steps, brightness_steps):
    return list(map(lambda s: s[0]*s[1], zip(steps, brightness_steps)))


def filter_zeros(steps, index):
    return steps[index:]

def find_nonzero(steps):
    return next((i for i, x in enumerate(steps) if x), None)


class WakeUp(Thread):

    def __init__(self, led, total_time, steps, max_brightness):
        super(WakeUp, self).__init__()
        self.setName("WakeUp")
        self.setDaemon(True)
        self.led = led
        self.total_time = total_time
        self.steps = steps
        self.max_brightness = max_brightness
        self.is_cancelled = False
        self.logger = logging.getLogger("WakeUp")

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        brightness_steps = calculate_steps(0, self.max_brightness, self.steps)
        red_steps = calculate_steps(self.led.WARM_YELLOW[0], self.led.WARM_WHITE[0], self.steps)
        green_steps = calculate_steps(self.led.WARM_YELLOW[1], self.led.WARM_WHITE[1], self.steps)
        blue_steps = calculate_steps(self.led.WARM_YELLOW[2], self.led.WARM_WHITE[2], self.steps)

        red_steps_brightness = add_brightness(red_steps, brightness_steps)
        green_steps_brightness = add_brightness(green_steps, brightness_steps)
        blue_steps_brightness = add_brightness(blue_steps, brightness_steps)

        # Check which list has the least zeros!
        red_index = find_nonzero(red_steps_brightness)
        green_index = find_nonzero(green_steps_brightness)
        blue_index = find_nonzero(blue_steps_brightness)

        index = min(red_index, green_index, blue_index)

        red_steps_filtered = filter_zeros(red_steps_brightness, index)
        green_steps_filtered = filter_zeros(green_steps_brightness, index)
        blue_steps_filtered = filter_zeros(blue_steps_brightness, index)

        actual_steps = len(red_steps_filtered)


        sleep_time = round(float(self.total_time)/actual_steps, 4)

        self.logger.info("Sleep time: %s", sleep_time)

        for colors in zip(red_steps_filtered, green_steps_filtered, blue_steps_filtered):
            if self.is_cancelled:
                self.logger.info("The wake up sequence is cancelled")
                break
            self.logger.debug("Colors: %s", list(map(round, colors)))
            self.led.color_dec(*colors)
            sleep(sleep_time)
        
        # At the end, set the lights to warm white
        self.led.warm_white(self.max_brightness)
