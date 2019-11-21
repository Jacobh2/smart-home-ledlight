from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import _request_ctx_stack

from flask_cors import cross_origin

from os import system
from os.path import join
from os import environ

from room.room import Room

import logging
from setting import Setting
from auth.auth0 import AuthError
from auth.auth0 import Auth0
from google_home.action_handler import GoogleHomeActionHandler
from smart_home import RequestError

logging.basicConfig(level="DEBUG")
logger = logging.getLogger("main")

setting = Setting()


app = Flask(
    __name__,
    template_folder=setting.TEMPLATE_FOLDER,
    static_folder=setting.STATIC_FOLDER,
    static_url_path=setting.STATIC_URL_PATH,
)

auth = Auth0(setting)

# Register this room
if setting.THIS_ROOM:
    logger.info("This room is set to %s", setting.THIS_ROOM)
    room = Room(
        setting.THIS_ROOM, auth, setting.PIN_RED, setting.PIN_GREEN, setting.PIN_BLUE
    )
    room.bind(app)
    ghome_handler = GoogleHomeActionHandler(room.led, "Hallway LED Strip", "Hallway Strip", "Hallway Led Strip", "Hallway")
else:
    raise Exception("No room set for this room! Please set 'THIS_ROOM' env")


@app.route("/shortcut.png")
@cross_origin(allow_headers=["Content-Type", "Authorization"])
def shortcut():
    return send_from_directory(join(app.root_path, "public"), "shortcut.png")


@app.route("/favicon.png")
@cross_origin(allow_headers=["Content-Type", "Authorization"])
def favicon():
    return send_from_directory(join(app.root_path, "public"), "favicon.png")


@app.route("/", methods=["GET"])
@cross_origin(allow_headers=["Content-Type", "Authorization"])
@auth.requires_auth
def index():
    logger.info("Requesting index")
    return render_template("index.html")


@app.route("/", methods=["POST"])
@cross_origin(allow_headers=["Content-Type", "Authorization"])
@auth.requires_auth
def request_from_ghome():
    current_user = _request_ctx_stack.top.current_user
    logger.info("Current user: %s", current_user)

    json_data = request.get_json()
    if not json_data:
        raise Exception("No post body data found")

    logger.info("Got json data: %s", json_data)
    # Set the current user
    ghome_handler.agent_user_id = current_user.get("sub")
    ret = ghome_handler.handle_request(json_data)

    logger.info("Returning result: %s", ret)
    return jsonify(ret)


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    logger.exception("AuthError Crash: %s", ex)
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(404)
def page_not_found(e):
    logger.exception("404 Crash: %s", e)
    return render_template("404.html")


@app.errorhandler(RequestError)
def handle_ghome_error(ex):
    logger.exception("RequestError Crash: %s", ex)
    response = jsonify(ex.get_json())
    response.status_code = 400
    return response


@app.errorhandler(Exception)
def other_error(ex):
    logger.exception("Exception Crash: %s", ex)
    response = jsonify(str(ex))
    response.status_code = 500
    return response


if __name__ == "__main__":
    logger.info(
        "Starting debug server at %s:%s...", setting.HTTP_ADDRESS, setting.HTTP_PORT
    )
    app.run(host=setting.HTTP_ADDRESS, port=setting.HTTP_PORT, debug=True)
