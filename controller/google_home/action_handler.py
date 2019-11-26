from smart_home import RequestHandler
from smart_home import DeviceInfo
from smart_home import RGBLight
from smart_home import actions
from smart_home import error

import logging

from threading import Thread
from time import sleep
from uuid import uuid4


class GoogleHomeActionHandler(RequestHandler):
    def __init__(self, led, name, nickname, fullname, room):
        device_info = DeviceInfo("Jacob Hagstedt", "V1", "1.0", "1.3")
        rgb_light = RGBLight(
            name, name, [nickname], [fullname], device_info, room, obj=led
        )
        action_mapping = {
            actions.ACTION_COMMAND_BRIGHTNESS_ABSOLUTE: self.set_brightness,
            actions.ACTION_COMMAND_COLOR_ABSOLUTE: self.set_color,
            actions.ACTION_COMMAND_ON_OFF: self.set_on_off,
        }
        initial_agent_id = None
        super().__init__(initial_agent_id, [rgb_light], action_mapping)
        self.logger = logging.getLogger("GoogleHomeActionHandler")

    def format_device_state(self, device_ids):
        device_status = dict()
        for device_id in device_ids:

            self.logger.info("Handing state for device with id '%s'", device_id)
            device = self.get_device(device_id)

            if not device:
                raise error.RequestError(
                    self.current_request_id, error.ERROR_DEVICE_NOT_FOUND
                )

            device_obj = device.obj

            device_color = device_obj.color
            self.logger.info("Device have color %s", device_color)

            if device_color is None:
                device_status[device_id] = {"online": False}
                continue

            on = device_color is not None and sum(device_color) > 0

            if not on:
                device_status[device_id] = {"on": False, "online": True}
                continue

            # Get the status of this device
            device_status[device_id] = {
                "on": True,
                "online": True,
                "brightness": round(
                    device_obj.calculate_brightness(*device_color) * 100.0
                ),
                "color": {
                    "spectrumRGB": device_obj.calculate_rgb_spectrum(*device_color)
                },
            }

        return device_status

    def set_brightness(self, ret, device, value):
        # return_payload, device, params
        brightness = value["brightness"]
        device.obj.set_brightness(brightness / 100.0)
        if "ids" in ret:
            ret["ids"].append(device.name)
        else:
            ret["ids"] = [device.name]

        ret["status"] = "SUCCESS"
        ret["states"] = {"on": True, "brightness": brightness}

    def set_color(self, ret, device, value):
        color_dec = value["color"]["spectrumRGB"]
        device.obj.set_color_rgb_dec(color_dec)
        if "ids" in ret:
            ret["ids"].append(device.name)
        else:
            ret["ids"] = [device.name]

        ret["status"] = "SUCCESS"
        ret["states"] = {"on": True, "color": {"spectrumRgb": color_dec}}

    def set_on_off(self, ret, device, value):
        if value["on"]:
            device.obj.all_on()
        else:
            device.obj.all_off()
        if "ids" in ret:
            ret["ids"].append(device.name)
        else:
            ret["ids"] = [device.name]

        ret["status"] = "SUCCESS"
        ret["states"] = {"on": True, "online": True}
