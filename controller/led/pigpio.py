import os
import logging
import subprocess
from threading import Semaphore

from led import color_utils


class PiGPIO(object):
    """
    Control PiGPIO lights with feature:
        - Color
        - Brightness

    Ask about:
        - Current color
        - Current brightness
    """

    def __init__(self, pin_red, pin_green, pin_blue):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.pin_red = pin_red
        self.pin_green = pin_green
        self.pin_blue = pin_blue
        self.semaphore = Semaphore()

    @property
    def brightness(self):
        r, g, b = self.color
        if r is None or g is None or b is None:
            return None
        return color_utils.rgb_to_hsv(r / 255, g / 255, b / 255)[2]

    @property
    def color(self):
        return (
            self._read_color(self.pin_red),
            self._read_color(self.pin_green),
            self._read_color(self.pin_blue),
        )

    @property
    def color_hex(self):
        return color_utils.dec_to_hex(*self.color)

    @property
    def color_rgb_spectrum(self):
        return color_utils.hex_to_rgb_dec(self.color_hex[1:])

    @property
    def is_on(self):
        return sum(self.color) > 0

    def _set_color(self, pin, value):
        """
        Sets the color for the provided pin
        """
        if isinstance(value, float):
            value = int(round(value))
        elif not isinstance(value, int):
            raise TypeError(
                "Value needs to be an int or float, {} found".format(type(value))
            )
        command = "pigs p {PIN} {VALUE}".format(PIN=pin, VALUE=value)
        try:
            self.logger.debug("About to execute command '%s'", command)
            with self.semaphore:
                self.logger.debug("Executing command '%s'", command)
                os.system(command)
            return value
        except Exception:
            self.logger.exception("Failed to execute command '%s'", command)
            return None

    def _read_color(self, pin):
        command = ["pigs", "gdc", str(pin)]
        try:
            self.logger.debug("About to execute command '%s'", command)
            with self.semaphore:
                self.logger.debug("Executing command '%s'", command)
                result = subprocess.run(command, stdout=subprocess.PIPE)
            self.logger.debug("Result: %s", result)
            if result.returncode == 0:
                return int(result.stdout.decode().strip())
        except Exception:
            self.logger.exception("Failed to execute command '%s'", command)
        return None

    def set_red(self, value):
        self._set_color(self.pin_red, value)

    def set_green(self, value):
        self._set_color(self.pin_green, value)

    def set_blue(self, value):
        self._set_color(self.pin_blue, value)

    def set_color_dec(self, red, green, blue):
        self.set_red(red)
        self.set_green(green)
        self.set_blue(blue)
        self.logger.debug("Color set to R:%s, G:%s, B:%s", red, green, blue)

    def set_color_hex(self, color):
        r, g, b = color_utils.split_hex(color)
        self.set_color_dec(
            color_utils.hex_to_rgb_dec(r),
            color_utils.hex_to_rgb_dec(g),
            color_utils.hex_to_rgb_dec(b),
        )

    def set_color_rgb_dec(self, value):
        hex_value = color_utils.rgb_dec_to_hex(value)
        self.set_color_hex(hex_value)

    def set_brightness(self, value):
        if not isinstance(value, float):
            raise TypeError("Brightness needs to be float")
        if value > 1.0:
            raise ValueError("Brightness needs to be max 1.0")
        if value < 0.0:
            raise ValueError("Brightness needs to be min 0.0")
        r, g, b = self.color
        self.set_color_dec(r * value, g * value, b * value)
