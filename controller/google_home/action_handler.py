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
        self.time_sleep_report_state = 10
        # Start report state thread
        self.report_state_thread = Thread(
            name="ReportState", target=self.report_state_threaded, daemon=True
        )
        self.report_state_thread.start()

    def _format_device_state(self, device_ids):
        device_status = dict()
        for device_id in device_ids:

            self.logger.info("Handing state for device with id %s", device_id)
            device = self.get_device(device_id)

            if not device:
                raise error.RequestError(
                    self.current_request_id, error.ERROR_DEVICE_NOT_FOUND
                )

            device_obj = device.obj

            # Get the status of this device
            device_status[device_id] = {
                "on": device_obj.is_on,
                "online": True,
                "brightness": round(device_obj.brightness * 100.0),
                "color": {"spectrumRGB": device_obj.color_rgb_spectrum},
            }
        return device_status

    def handle_query_request(self, input_data):
        # Parse the request
        devices = input_data["payload"]["devices"]
        device_ids = [device["id"] for device in devices]
        device_status = self._format_device_state(device_ids)
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

    def report_state_threaded(self):
        try:
            while True:
                # Gather state
                state = self._format_device_state(self.devices.keys())
                payload = {
                    "requestId": str(uuid4()),
                    "agentUserId": self.agent_user_id,
                    "payload": {"devices": {"states": state}},
                }
                self.logger.debug("About to report state %s", state)

                # Report the sate
                self.report_state(payload)

                # Sleep 10 sec
                sleep(self.time_sleep_report_state)
        except Exception:
            self.logger.exception("Crash during report state")
