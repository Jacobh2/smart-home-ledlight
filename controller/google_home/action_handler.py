from smart_home import RequestHandler
from smart_home import DeviceInfo
from smart_home import RGBLight
from smart_home import actions
from smart_home import error

import logging


class GoogleHomeActionHandler(RequestHandler):
    def __init__(self, led, name, nickname, fullname, room):
        super().__init__(
            None,
            [
                RGBLight(
                    name,
                    name,
                    [nickname],
                    [fullname],
                    DeviceInfo("Jacob Hagstedt", "V1", "1.0", "1.3"),
                    room,
                    obj=led,
                )
            ],
        )
        self.logger = logging.getLogger("GoogleHomeActionHandler")
        self.execute_handlers = {
            actions.ACTION_COMMAND_BRIGHTNESS_ABSOLUTE: self._set_brightness,
            actions.ACTION_COMMAND_COLOR_ABSOLUTE: self._set_color,
            actions.ACTION_COMMAND_ON_OFF: self._set_on_off,
        }

    def handle_query_request(self, input_data):
        # Parse the request
        devices = input_data["payload"]["devices"]

        device_status = dict()
        for device in devices:
            device_id = device.get("id")

            if not device_id:
                raise error.RequestError(
                    self.current_request_id, error.ERROR_DEVICE_NOT_FOUND
                )

            self.logger.info("Handing QUERY for device with id %s", device_id)
            device_obj = self.get_device(device_id).obj

            # Get the status of this device
            device_status[device_id] = {
                "on": device_obj.is_on,
                "online": True,
                "brightness": round(device_obj.brightness * 100.0),
                "color": {"spectrumRGB": device_obj.color_rgb_spectrum},
            }

        return self.format_query_response(device_status)

    def handle_execute_request(self, input_data):
        commands = input_data["payload"]["commands"]

        ret = dict()
        for command in commands:
            devices = command["devices"]
            executions = command["execution"]
            for device in devices:
                device_id = device["id"]
                self.logger.info("Handing EXECUTE for device with id %s", device_id)
                device = self.get_device(device_id)

                for execution in executions:
                    exec_command = execution.get("command")
                    params = execution.get("params")
                    if exec_command not in self.execute_handlers:
                        raise error.RequestError(
                            self.current_request_id, error.ERROR_NOT_SUPPORTED
                        )

                    self.execute_handlers[exec_command](ret, device, params)
        return self.format_execute_response(ret)

    def _set_brightness(self, ret, device, value):
        brightness = value["brightness"]
        device.obj.set_brightness(brightness / 100.0)
        if "ids" in ret:
            ret["ids"].append(device.name)
        else:
            ret["ids"] = [device.name]

        ret["status"] = "SUCCESS"
        ret["states"] = {"on": True, "brightness": brightness}

    def _set_color(self, ret, device, value):
        color_dec = value["color"]["spectrumRGB"]
        device.obj.set_color_rgb_dec(color_dec)
        if "ids" in ret:
            ret["ids"].append(device.name)
        else:
            ret["ids"] = [device.name]

        ret["status"] = "SUCCESS"
        ret["states"] = {"on": True, "color": {"spectrumRgb": color_dec}}

    def _set_on_off(self, ret, device, value):
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
