from time import sleep

from led import wakeup
from led.pigpio import PiGPIO


class LED(PiGPIO):
    def __init__(self, pin_red, pin_green, pin_blue):
        super().__init__(pin_red, pin_green, pin_blue)

        # Presets
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.WARM_YELLOW = (255, 20, 0)
        self.WARM_WHITE = (255, 60, 20)
        self.PINK = (255, 0, 15)

        self.wakeup_thread = None

    def all_on(self):
        self.set_color_dec(*self.WHITE)

    def all_off(self):
        self.set_color_dec(*self.BLACK)

    def wake_up(self, total_time, steps, max_brightness):
        if self.wakeup_thread is not None:
            if self.wakeup_thread.is_alive():
                # We're already running the wakup program, cancel that one
                self.wakeup_thread.cancel()
        self.wakeup_thread = wakeup.WakeUp(self, total_time, steps, max_brightness)
        self.wakeup_thread.start()
        return self.wakeup_thread

    def wake_up_cancel(self):
        if self.wakeup_thread is not None:
            if self.wakeup_thread.is_alive():
                self.wakeup_thread.cancel()

    def confirm(self):
        self.logger.debug("Confirming!")
        current_state = self.color
        brightness = self.brightness
        # Blink the lights to confirm something
        self.all_off()
        sleep(0.07)
        self.set_color_dec(*current_state)
        sleep(0.1)
        self.all_off()
        sleep(0.07)
        # Set back what it was
        if brightness > 0:
            self.set_color_dec(*current_state)
