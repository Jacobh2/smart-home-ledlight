import os
import logging

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
        self.RED_STATE = 0
        self.GREEN_STATE = 0
        self.BLUE_STATE = 0

        self.pin_red = pin_red
        self.pin_green = pin_green
        self.pin_blue = pin_blue

    @property
    def brightness(self):
        return color_utils.rgb_to_hsv(
            self.RED_STATE / 255, self.GREEN_STATE / 255, self.BLUE_STATE / 255
        )[2]

    @property
    def color(self):
        return self.RED_STATE, self.GREEN_STATE, self.BLUE_STATE

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
            self.logger.debug("Executing command '%s'", command)
            os.system(command)
            return value
        except Exception:
            self.logger.exception("Failed to execute command '%s'", command)
            return None

    def set_red(self, value, set_state=True):
        new_state = self._set_color(self.pin_red, value)
        if set_state and new_state:
            self.RED_STATE = new_state

    def set_green(self, value, set_state=True):
        new_state = self._set_color(self.pin_green, value)
        if set_state and new_state:
            self.GREEN_STATE = new_state

    def set_blue(self, value, set_state=True):
        new_state = self._set_color(self.pin_blue, value)
        if set_state and new_state:
            self.BLUE_STATE = new_state

    def set_color_dec(self, red, green, blue, set_state=True):
        self.set_red(red, set_state=set_state)
        self.set_green(green, set_state=set_state)
        self.set_blue(blue, set_state=set_state)
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
        self.set_color_dec(
            self.RED_STATE * value,
            self.GREEN_STATE * value,
            self.BLUE_STATE * value,
            set_state=False,
        )
