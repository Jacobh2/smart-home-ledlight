from led.led import LED
from alarm.alarm import Alarm

from flask import jsonify
from flask import request
from flask import Blueprint
from flask import render_template
from flask_cors import cross_origin

import logging


class Room(object):
    def __init__(
        self,
        name,
        auth,
        pin_red,
        pin_green,
        pin_blue,
        alarm_time=30 * 60,
        alarm_max_brightness=1.0,
    ):
        self.logger = logging.getLogger("Room({})".format(name))
        self.name = name
        self.auth = auth

        self.led = LED(pin_red, pin_green, pin_blue)

        self.ALARM_TIME = alarm_time
        self.ALARM_MAX_BRIGHTNESS = alarm_max_brightness

        self.alarm_handler = Alarm(
            self.led.wake_up, self.ALARM_TIME, self.ALARM_MAX_BRIGHTNESS
        )

        self.route = Blueprint(self.name, __name__)
        self.route.add_url_rule("/color", "color", self.color)
        self.route.add_url_rule("/brightness", "brightness", self.brightness)
        self.route.add_url_rule("/alarm", "alarm", self.alarm)
        self.route.add_url_rule("/wakeup", "wakeup", self.wakeup_route)
        self.route.add_url_rule("/", "index", self.index)

    def bind(self, app):
        self.logger.info("Registering %s", self.name)
        app.register_blueprint(self.route, url_prefix="/{}".format(self.name))
        self.logger.info("%s is registered", self.name)

    def _return_state(self):
        return jsonify(
            {
                "ok": True,
                "r": self.led.RED_STATE,
                "g": self.led.GREEN_STATE,
                "b": self.led.BLUE_STATE,
            }
        )

    def color(self):
        if request.method != "GET":

            @cross_origin(allow_headers=["Content-Type", "Authorization"])
            @self.auth.requires_auth
            def set_color():
                # First, check if we have data in post
                json_data = request.get_json()
                if json_data is None:
                    json_data = request.args

                hex_ = json_data.get("hex", None)
                if hex_ is None:
                    # Check if rgb is provided
                    r = int(json_data.get("red"))
                    g = int(json_data.get("green"))
                    b = int(json_data.get("blue"))

                    self.led.set_color_dec(r, g, b)
                elif len(hex_) != 6:
                    return jsonify({"ok": False, "error": "Please provide hex"}), 400
                else:
                    self.led.set_color_hex(hex_)

            set_color()

        return self._return_state()

    def brightness(self):
        if request.method != "GET":

            @cross_origin(allow_headers=["Content-Type", "Authorization"])
            @self.auth.requires_auth
            def _set_brightness():
                json_data = request.get_json()
                if json_data is None:
                    json_data = request.args

                value = json_data.get("value")

                self.logger.info("Got brightness %s", value)
                if value is None:
                    return jsonify({"ok": False, "error": "Please provide value"}), 400

                self.led.set_brightness(float(value))

        return self._return_state()

    def alarm(self):
        if request.method != "GET":

            @cross_origin(allow_headers=["Content-Type", "Authorization"])
            @self.auth.requires_auth
            def _set_alarm(self):
                json_data = request.get_json()
                if json_data is None:
                    json_data = request.args

                time = json_data.get("time")
                self.logger.info("Got time %s", time)
                if time is None:
                    # Check if we have cancel
                    cancel = bool(int(json_data.get("cancel", 0)))
                    if cancel:
                        # Cancel any ongoing alarm
                        self.led.wake_up_cancel()
                        # Cancel the alarm
                        cancel_ok = self.alarm_handler.cancel()
                        if cancel_ok:
                            self.led.confirm()
                else:
                    # Set the alarm!
                    alarm_is_activated = self.alarm_handler.activate(time)
                    if alarm_is_activated:
                        # Blink the lights
                        self.led.confirm()

        self.logger.info("Current alarm time: %s", self.alarm_handler.time)
        return jsonify({"ok": True, "data": self.alarm_handler.time})

    def wakeup_route(self):
        steps = int(request.args.get("steps", 10))
        seconds = int(request.args.get("time", 10))
        brightness = float(request.args.get("brightness", 1.0))

        self.logger.info(
            "Running wakeup program in %s sec, %s steps and to %s brightness",
            seconds,
            steps,
            brightness,
        )
        self.led.wake_up(seconds, steps, brightness)

        return jsonify({"ok": True})

    def index(self):
        @cross_origin(allow_headers=["Content-Type", "Authorization"])
        @self.auth.requires_auth
        def _index():
            # If the initial state is off, then at least set the
            # initial color to white, so that the color wheel looks nicer
            if not self.led.is_on:
                initialColor = "#FFFFFF"
            else:
                initialColor = self.led.color_hex

            if self.alarm_handler.time is None:
                alarm_time = ""
            else:
                alarm_time = self.alarm_handler.time

            return render_template(
                "controller.html",
                roomName=self.name,
                initialColor=initialColor,
                initialOnState="true" if self.led.is_on else "false",
                initialAlarm=alarm_time,
            )

        return _index()
